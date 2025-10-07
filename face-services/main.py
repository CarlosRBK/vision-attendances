"""
Face Services - Microservicio HTTP para Detección Facial
Recibe frames desde el frontend vía HTTP POST y realiza detección facial en tiempo real
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import os
import face_recognition
import numpy as np
import base64
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading
import time
import requests
from typing import Optional

app = Flask(__name__)
CORS(app)  # Permitir requests desde el frontend

# ==================== CONFIGURACIÓN GLOBAL ====================

# Configuración del backend
BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")
DEVICE_ID = os.getenv("DEVICE_ID", "face-service-default")

# Obtener la ruta base para las fotos
current_file_path = os.path.abspath(__file__)
current_dir_path = os.path.dirname(current_file_path)
app_dir_path = os.path.dirname(os.path.dirname(current_dir_path))
FACES_FOLDER = os.path.join(app_dir_path, "static", "people_photos")

# Variables globales para cachear rostros conocidos
faces_encodings = []
faces_names = []
faces_lock = threading.Lock()

# ==================== CLASE ASISTENCIA ====================

class Asistencia:
    """Maneja el registro de asistencias enviándolas al backend"""
    
    def __init__(self):
        self.registrados_hoy = set()  # Cache local para evitar duplicados en la misma sesión
        self.lock = threading.Lock()
        print(f"[INFO] Sistema de asistencia iniciado")
        print(f"[INFO] Backend URL: {BACKEND_URL}")
        print(f"[INFO] Device ID: {DEVICE_ID}")
    
    def marcar_asistencia(self, person_id: str, person_name: str, confidence: float) -> bool:
        """Marca asistencia enviando los datos al backend. Retorna True si se marcó."""
        with self.lock:
            # Verificar si ya se registró en esta sesión
            if person_id in self.registrados_hoy:
                return False
            
            try:
                # Enviar datos al backend
                payload = {
                    "person_id": person_id,
                    "person_name": person_name,
                    "confidence": float(confidence),
                    "device_id": DEVICE_ID
                }
                
                response = requests.post(
                    f"{BACKEND_URL}/attendances/",
                    json=payload,
                    timeout=5.0
                )
                
                if response.status_code in [200, 201]:
                    self.registrados_hoy.add(person_id)
                    fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(f"[ASISTENCIA] ✓ {person_name} (ID: {person_id}) - {fecha_hora} - Confianza: {confidence:.2%}")
                    return True
                else:
                    print(f"[ERROR] Backend respondió con código {response.status_code}: {response.text}")
                    return False
                    
            except requests.exceptions.RequestException as e:
                print(f"[ERROR] No se pudo conectar al backend: {e}")
                return False
            except Exception as e:
                print(f"[ERROR] Error al marcar asistencia: {e}")
                return False

# ==================== MONITOR DE CARPETA ====================

class FolderMonitor(FileSystemEventHandler):
    """Monitorea cambios en la carpeta de fotos y recarga rostros"""
    
    def __init__(self):
        self.last_reload = time.time()
        self.reload_cooldown = 2.0  # Esperar 2 segundos entre recargas
        self.pending_reload = False
        self.lock = threading.Lock()
    
    def on_any_event(self, event):
        """Detecta cualquier cambio en archivos de imagen"""
        if event.is_directory:
            return
        
        ext = os.path.splitext(event.src_path)[1].lower()
        if ext in [".jpg", ".jpeg", ".png"]:
            print(f"[INFO] Cambio detectado: {os.path.basename(event.src_path)}")
            self._schedule_reload()
    
    def _schedule_reload(self):
        """Programa una recarga con cooldown"""
        with self.lock:
            current_time = time.time()
            if (current_time - self.last_reload) > self.reload_cooldown:
                self._do_reload()
                self.last_reload = current_time
            else:
                self.pending_reload = True
    
    def check_pending(self):
        """Verifica si hay una recarga pendiente"""
        with self.lock:
            if self.pending_reload:
                current_time = time.time()
                if (current_time - self.last_reload) > self.reload_cooldown:
                    self._do_reload()
                    self.last_reload = current_time
                    self.pending_reload = False
    
    def _do_reload(self):
        """Recarga todos los rostros desde la carpeta"""
        print("[INFO] Recargando rostros...")
        load_known_faces()
        print(f"[INFO] Recarga completada: {len(faces_names)} rostros")

# ==================== FUNCIONES DE DETECCIÓN ====================

def load_known_faces():
    """Carga todos los rostros conocidos desde la carpeta"""
    global faces_encodings, faces_names
    
    with faces_lock:
        faces_encodings = []
        faces_names = []
        
        if not os.path.exists(FACES_FOLDER):
            os.makedirs(FACES_FOLDER, exist_ok=True)
            print(f"[INFO] Carpeta creada: {FACES_FOLDER}")
            return
        
        image_files = [f for f in os.listdir(FACES_FOLDER) 
                      if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        
        print(f"[INFO] Cargando rostros desde: {FACES_FOLDER}")
        print(f"[INFO] Archivos encontrados: {len(image_files)}")
        
        for filename in image_files:
            filepath = os.path.join(FACES_FOLDER, filename)
            try:
                # Extraer nombre del archivo
                name = os.path.splitext(filename)[0]
                
                # Cargar imagen
                image = cv2.imread(filepath)
                if image is None:
                    continue
                
                # Convertir a RGB y redimensionar
                rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                rgb_small = cv2.resize(rgb_image, (150, 150))
                rgb_small = np.ascontiguousarray(rgb_small, dtype=np.uint8)
                
                # Obtener encoding
                encodings = face_recognition.face_encodings(
                    rgb_small, 
                    known_face_locations=[(0, 150, 150, 0)]
                )
                
                if encodings:
                    faces_encodings.append(encodings[0])
                    faces_names.append(name)
                    print(f"  ✓ {name}")
                    
            except Exception as e:
                print(f"  ✗ Error con {filename}: {e}")
        
        print(f"[INFO] Total rostros cargados: {len(faces_names)}")


def detect_faces_in_frame(frame):
    """Detecta y reconoce rostros en un frame. Retorna lista de detecciones."""
    try:
        # Convertir a escala de grises para detección rápida
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Usar Haar Cascade para detección rápida
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        
        if len(faces) > 0:
            print(f"[DEBUG] {len(faces)} rostro(s) detectado(s) en el frame")
        
        detections = []
        
        for (x, y, w, h) in faces:
            # Extraer ROI del rostro
            face_roi = frame[y:y+h, x:x+w]
            
            if face_roi.size == 0:
                continue
            
            # Convertir a RGB y redimensionar
            rgb_roi = cv2.cvtColor(face_roi, cv2.COLOR_BGR2RGB)
            rgb_small = cv2.resize(rgb_roi, (150, 150))
            rgb_small = np.ascontiguousarray(rgb_small, dtype=np.uint8)
            
            # Obtener encoding del rostro detectado
            encodings = face_recognition.face_encodings(
                rgb_small,
                known_face_locations=[(0, 150, 150, 0)],
                num_jitters=1
            )
            
            name = "Desconocido"
            confidence = 0
            
            if encodings and len(faces_encodings) > 0:
                encoding = encodings[0]
                
                # Comparar con rostros conocidos
                with faces_lock:
                    distances = face_recognition.face_distance(faces_encodings, encoding)
                    
                    if len(distances) > 0:
                        best_match_index = np.argmin(distances)
                        best_distance = distances[best_match_index]
                        
                        print(f"[DEBUG] Mejor coincidencia: {faces_names[best_match_index]} con distancia {best_distance:.4f}")
                        
                        # Umbral de 0.5 (más bajo = más estricto, 0.5 es más exigente que 0.6)
                        if best_distance < 0.5:
                            name = faces_names[best_match_index]
                            confidence = 1 - best_distance
                            
                            print(f"[DEBUG] Rostro reconocido: {name} con confianza {confidence:.2%}")
                            
                            # Marcar asistencia (enviar al backend)
                            # Usar el nombre como person_id por ahora
                            # TODO: Obtener el person_id real desde el backend
                            resultado = asistencia.marcar_asistencia(
                                person_id=name,
                                person_name=name,
                                confidence=confidence
                            )
                            
                            if resultado:
                                print(f"[DEBUG] Asistencia marcada exitosamente para {name}")
                            else:
                                print(f"[DEBUG] No se marcó asistencia para {name} (posiblemente ya registrado hoy)")
            
            detections.append({
                "name": name,
                "confidence": float(confidence),
                "box": {
                    "x": int(x),
                    "y": int(y),
                    "width": int(w),
                    "height": int(h)
                }
            })
        
        return detections
        
    except Exception as e:
        print(f"[ERROR] Error en detección: {e}")
        return []

# ==================== ENDPOINTS HTTP ====================

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "ok",
        "service": "face-services",
        "known_faces": len(faces_names),
        "faces_folder": FACES_FOLDER
    }), 200


@app.route('/detect', methods=['POST'])
def detect():
    """
    Endpoint principal para detección facial
    Recibe un frame en base64 y retorna las detecciones
    
    Body: { "frame": "base64_encoded_image" }
    Response: { "detections": [...], "timestamp": "..." }
    """
    try:
        # Verificar pending reload del monitor
        if folder_monitor:
            folder_monitor.check_pending()
        
        data = request.get_json()
        
        if not data or 'frame' not in data:
            return jsonify({"error": "No frame provided"}), 400
        
        # Decodificar frame desde base64
        frame_b64 = data['frame']
        
        # Remover prefijo data:image si existe
        if ',' in frame_b64:
            frame_b64 = frame_b64.split(',')[1]
        
        # Decodificar base64
        frame_bytes = base64.b64decode(frame_b64)
        nparr = np.frombuffer(frame_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            return jsonify({"error": "Invalid image data"}), 400
        
        # Detectar rostros
        detections = detect_faces_in_frame(frame)
        
        return jsonify({
            "success": True,
            "detections": detections,
            "timestamp": datetime.now().isoformat(),
            "known_faces": len(faces_names)
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Error en /detect: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/reload', methods=['POST'])
def reload_faces():
    """Recarga manualmente los rostros conocidos"""
    try:
        load_known_faces()
        return jsonify({
            "success": True,
            "message": "Rostros recargados",
            "count": len(faces_names)
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/attendance/today', methods=['GET'])
def get_attendance_today():
    """Obtiene la lista de asistencia del día actual desde el backend"""
    try:
        # Redirigir al backend para obtener las asistencias del día
        response = requests.get(
            f"{BACKEND_URL}/attendances/today/",
            timeout=5.0
        )
        
        if response.status_code == 200:
            return jsonify(response.json()), 200
        else:
            return jsonify({
                "error": "Error al obtener asistencias del backend",
                "status_code": response.status_code
            }), response.status_code
            
    except requests.exceptions.RequestException as e:
        return jsonify({
            "error": "No se pudo conectar al backend",
            "details": str(e)
        }), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ==================== INICIALIZACIÓN ====================

# Instancia global de asistencia
asistencia = Asistencia()

# Monitor de carpeta
folder_monitor = None

def start_folder_monitor():
    """Inicia el monitor de la carpeta de fotos"""
    global folder_monitor
    try:
        folder_monitor = FolderMonitor()
        observer = Observer()
        observer.schedule(folder_monitor, FACES_FOLDER, recursive=False)
        observer.daemon = True
        observer.start()
        print(f"[INFO] Monitor de carpeta iniciado: {FACES_FOLDER}")
    except Exception as e:
        print(f"[ERROR] No se pudo iniciar monitor: {e}")


if __name__ == '__main__':
    print("="*60)
    print("  FACE SERVICES - Microservicio de Detección Facial")
    print("="*60)
    print(f"  Carpeta de fotos: {FACES_FOLDER}")
    print(f"  Puerto: 5001")
    print("="*60)
    
    # Cargar rostros conocidos al iniciar
    load_known_faces()
    
    # Iniciar monitor de carpeta
    start_folder_monitor()
    
    # Iniciar servidor Flask
    app.run(
        host='0.0.0.0',
        port=5001,
        debug=False,
        threaded=True
    )
