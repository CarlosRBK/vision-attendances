from typing import Union
import cv2
import os
import face_recognition
import numpy as np
import time
import threading
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent, FileDeletedEvent, FileModifiedEvent


class VideoConfig:
    def __init__(self, video_source: int = 0, use_optimized: bool = True):
        self.video_source = video_source
        self.use_optimized = use_optimized

class VideoCapture:
    _is_capturing = False
    _cap: cv2.VideoCapture

    frame_count = 0

    def __init__(self, config: VideoConfig):
        cv2.setUseOptimized(config.use_optimized)
        self._cap = cv2.VideoCapture(config.video_source)
        self._is_capturing = False

    def set(self, propId: int, value: float) -> bool:
        return self._cap.set(propId, value)

    def start(self, listener=None):
        self._is_capturing = True
        while self._is_capturing:
            self.frame_count += 1
            ret, frame = self._cap.read()
            if not ret:
                break
            if listener:
                listener(frame)

    def stop(self):
        self._is_capturing = False
        self._cap.release()
        cv2.destroyAllWindows()

class Asistencia:
    registrados = set()
    archivo_asistencia: str

    def __init__(self) -> None:
        # Obtener la fecha actual y generar el nombre del archivo
        fecha_actual = datetime.now().strftime("%d-%m-%Y")  # formato 12-07-2025
        self.archivo_asistencia = f"asistencia_{fecha_actual}.txt"
        
        # archivo_asistencia = "asistencia.txt"

        # Cargar asistencias anteriores (si se quiere continuar la lista entre ejecuciones)
        if os.path.exists(self.archivo_asistencia):
            with open(self.archivo_asistencia, "r", encoding="utf-8") as f:
                for linea in f:
                    self.registrados.add(linea.strip())

    def marcar_asistencia(self, nombre: str) -> None:
        if nombre not in self.registrados:
            fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(self.archivo_asistencia, "a", encoding="utf-8") as f:
                f.write(f"{fecha_hora} - {nombre}\n")
            self.registrados.add(nombre)

class FolderMonitor(FileSystemEventHandler):
    """Monitor de cambios en la carpeta de rostros"""
    def __init__(self, face_detector):
        self.face_detector = face_detector
        self.last_reload = time.time()
        self.reload_cooldown = 2.0  # segundos mínimos entre recargas
        self.pending_reload = False
        self.lock = threading.Lock()
    
    def on_created(self, event):
        # Cuando se crea un archivo nuevo
        if not event.is_directory and self._is_image_file(event.src_path):
            print(f"[INFO] Archivo nuevo detectado: {os.path.basename(event.src_path)}")
            self._schedule_reload()
    
    def on_deleted(self, event):
        # Cuando se elimina un archivo
        if not event.is_directory and self._is_image_file(event.src_path):
            print(f"[INFO] Archivo eliminado: {os.path.basename(event.src_path)}")
            self._schedule_reload()
    
    def on_modified(self, event):
        # Cuando se modifica un archivo
        if not event.is_directory and self._is_image_file(event.src_path):
            print(f"[INFO] Archivo modificado: {os.path.basename(event.src_path)}")
            self._schedule_reload()
    
    def _is_image_file(self, path):
        # Verificar si es un archivo de imagen por su extensión
        ext = os.path.splitext(path)[1].lower()
        return ext in [".jpg", ".jpeg", ".png"]
    
    def _schedule_reload(self):
        # Programar una recarga con protección contra recargas frecuentes
        with self.lock:
            current_time = time.time()
            time_since_last = current_time - self.last_reload
            
            if time_since_last > self.reload_cooldown:
                # Si ha pasado suficiente tiempo, recargar inmediatamente
                self._do_reload()
                self.last_reload = current_time
                self.pending_reload = False
            else:
                # Si es demasiado pronto, marcar como pendiente
                self.pending_reload = True
    
    def check_pending_reload(self):
        # Verificar si hay una recarga pendiente y ejecutarla si es necesario
        with self.lock:
            current_time = time.time()
            if self.pending_reload and (current_time - self.last_reload) > self.reload_cooldown:
                self._do_reload()
                self.last_reload = current_time
                self.pending_reload = False
    
    def _do_reload(self):
        # Realizar la recarga de rostros
        print("\n[INFO] Detectado cambio en la carpeta de rostros. Recargando...")
        try:
            # Limpiar las listas existentes para asegurar que se eliminen rostros que ya no existen
            self.face_detector.faces_encodings = []
            self.face_detector.faces_names = []
            # Recargar todos los rostros desde la carpeta
            self.face_detector.load_faces_from_folder(self.face_detector._faces_folder)
            print(f"[INFO] Recarga completada. {len(self.face_detector.faces_names)} rostros cargados.")
        except Exception as e:
            print(f"[ERROR] Error al recargar rostros: {e}")


class FaceDetector:
    _cap: VideoCapture
    _asistencia: Asistencia
    _face_detector: cv2.CascadeClassifier
    _faces_folder: str

    # Parámetros de rendimiento
    process_every_n = 2  # procesa 1 de cada 2 cuadros
    scale = 0.5  # detectar a media resolución
    last_detections = []  # lista de tuplas (X,Y,W,H,name,color)

    # Parámetros de codificación
    faces_encodings = []
    faces_names = []

    @staticmethod
    def resolve_haarcascade():
        """Devuelve la ruta del haarcascade_frontalface_default.xml en instalaciones típicas.
        Compatible con conda-forge (macOS/Windows/Linux) y Homebrew.
        """

        filename = "haarcascade_frontalface_default.xml"

        # Posibles rutas para el archivo.
        candidates = []

        # Si cv2.data existe
        try:
            data_dir = cv2.data.haarcascades  # type: ignore[attr-defined]  # noqa: F821
            candidates.append(os.path.join(data_dir, filename))
        except Exception:
            pass

        # Agregamos ruta de cv2. Junto al paquete cv2 (a veces existe carpeta data/)
        candidates.append(os.path.join(os.path.dirname(cv2.__file__), "data", filename))

        # Agregamos rutas de conda-forge
        conda_prefix = os.environ.get("CONDA_PREFIX", "")
        if conda_prefix:
            candidates.extend(
                [
                    os.path.join(
                        conda_prefix, "share", "opencv4", "haarcascades", filename
                    ),
                    os.path.join(conda_prefix, "share", "opencv", "haarcascades", filename),
                    os.path.join(conda_prefix, "etc", "haarcascades", filename),
                ]
            )

        # Agregamos rutas de sistema comunes (Linux/macOS/Homebrew)
        candidates.extend(
            [
                "/usr/share/opencv4/haarcascades/" + filename,
                "/usr/local/share/opencv4/haarcascades/" + filename,
                "/opt/homebrew/opt/opencv/share/opencv4/haarcascades/" + filename,
            ]
        )

        #  Retornamos la ruta que exista
        for path in candidates:
            if path and os.path.exists(path):
                return path
        raise FileNotFoundError(
            "No se encontró el clasificador Haar. Instala opencv con conda-forge o especifica la ruta manualmente."
        )
    
    def __init__(self, cap: VideoCapture, asistencia: Asistencia, faces_folder: str) -> None:
        self._cap = cap
        self._asistencia = asistencia
        self._face_detector = cv2.CascadeClassifier(FaceDetector.resolve_haarcascade())
        self._faces_folder = faces_folder

        # Cargar rostros inicialmente
        self.load_faces_from_folder(faces_folder)
        
        # Configurar el monitor de la carpeta
        self._setup_folder_monitor()
    
    def _get_encodings(self, image: np.ndarray) -> Union[np.ndarray, None]:
        """Obtiene los embeddings de un rostro en una imagen."""
        try:
            # Convertir a RGB y redimensionar para acelerar el cómputo
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image_rgb_small = cv2.resize(image_rgb, (150, 150))
            # Asegurar que sea contiguo en memoria
            image_rgb_small = np.ascontiguousarray(image_rgb_small, dtype=np.uint8)
            encodings = face_recognition.face_encodings(
                image_rgb_small, known_face_locations=[(0, 150, 150, 0)]
            )
            return encodings[0] if encodings else None
        except Exception as e:
            print(f"Error al obtener encodings: {e}")
            return None

    def load_faces_from_folder(self, folder_path: str):
        """Carga los rostros desde una carpeta y los codifica."""
        if not os.path.exists(folder_path):
            os.makedirs(folder_path, exist_ok=True)
            print(f"Carpeta '{folder_path}' creada.")
        
        # Obtener lista de archivos en la carpeta
        files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
        image_files = [f for f in files if os.path.splitext(f)[1].lower() in [".jpg", ".jpeg", ".png"]]
        
        print(f"Encontrados {len(image_files)} archivos de imagen en '{folder_path}'")
        
        face_count = 0
        for file_name in image_files:
            file_path = os.path.join(folder_path, file_name)
            try:
                # Extraer nombre de la persona del nombre del archivo
                name = os.path.splitext(file_name)[0]
                
                # Cargar imagen y obtener encoding
                image = cv2.imread(file_path)
                if image is None:
                    print(f"No se pudo cargar la imagen: {file_path}")
                    continue
                    
                # Convertir a RGB (face_recognition usa RGB)
                rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                
                # Obtener encoding
                encoding = self._get_encodings(rgb_image)
                if encoding is not None:
                    self.faces_encodings.append(encoding)
                    self.faces_names.append(name)
                    face_count += 1
            except Exception as e:
                print(f"Error al procesar {file_path}: {e}")
        
        print(f"Se cargaron {face_count} rostros desde '{folder_path}'")
        
        if face_count == 0:
            print(
                f"No se encontraron rostros en la carpeta '{folder_path}'. Ejecuta primero extracting_faces.py y verifica que existan imágenes."
            )

    def _draw_label(self, frame, x: int, y: int, w: int, h: int, label: str, color):
        """Dibujo de etiqueta adaptativa para evitar desborde del texto"""
        font_face = cv2.FONT_HERSHEY_SIMPLEX
        max_w = max(30, w - 8)  # ancho máximo permitido (ligero margen)
        scale = 0.7
        thickness = 2
        # Ajustar escala y, si es necesario, recortar con elipsis
        while True:
            (tw, th), bl = cv2.getTextSize(label, font_face, scale, thickness)
            if tw <= max_w:
                break
            if scale > 0.45:
                scale -= 0.1
                continue
            # Escala mínima alcanzada: recortar y añadir elipsis
            if len(label) > 2:
                label = label[:-2] + "…"
            else:
                break
        pad = 4
        rect_w = min(tw + 2 * pad, w)
        rect_h = th + 2 * pad
        Hf, Wf = frame.shape[:2]
        # Preferir dibujar debajo; si no hay espacio, dibujar arriba
        box_y = y + h
        if box_y + rect_h > Hf:
            box_y = max(0, y - rect_h)
        box_x = max(0, min(x, Wf - rect_w))
        # Fondo
        cv2.rectangle(frame, (box_x, box_y), (box_x + rect_w, box_y + rect_h), color, -1)
        # Texto
        text_x = box_x + pad
        text_y = box_y + rect_h - pad - 1
        cv2.putText(
            frame,
            label,
            (text_x, text_y),
            font_face,
            scale,
            (255, 255, 255),
            thickness,
            cv2.LINE_AA,
        )

    def _on_frame(self, frame):
        # Verificar si hay cambios pendientes en la carpeta de rostros
        if self._folder_observer:
            self._folder_observer[1].check_pending_reload()
            
        frame = cv2.flip(frame, 1)
        process_this_frame = cap.frame_count % self.process_every_n == 0
        if process_this_frame:
            # Detección en resolución reducida
            small = cv2.resize(frame, (0, 0), fx=self.scale, fy=self.scale)
            gray_small = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
            faces_small = self._face_detector.detectMultiScale(gray_small, 1.2, 5)
            current = []
            if len(faces_small) > 0:
                inv_scale = 1.0 / self.scale
                for sx, sy, sw, sh in faces_small:
                    X = int(sx * inv_scale)
                    Y = int(sy * inv_scale)
                    W = int(sw * inv_scale)
                    H = int(sh * inv_scale)
                    roi = frame[Y : Y + H, X : X + W]
                    if roi.size == 0:
                        continue
                    roi_rgb = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)
                    # Reducir tamaño del ROI para acelerar el cómputo del embedding
                    roi_rgb_small = cv2.resize(roi_rgb, (150, 150))
                    # Asegurar uint8 y contigüidad en memoria (evita errores en Windows/dlib)
                    roi_rgb_small = np.ascontiguousarray(roi_rgb_small, dtype=np.uint8)
                    encs = face_recognition.face_encodings(
                        roi_rgb_small,
                        known_face_locations=[(0, 150, 150, 0)],
                        num_jitters=1,
                    )
                    name = "Desconocido"
                    color = (50, 50, 255)
                    if encs:
                        actual = encs[0]
                        result = face_recognition.compare_faces(self.faces_encodings, actual)
                        if True in result:
                            index = result.index(True)
                            name = self.faces_names[index]
                            color = (125, 220, 0)
                            asistencia.marcar_asistencia(name)
                    current.append((X, Y, W, H, name, color))
            self.last_detections = current
        # Dibujo de las últimas detecciones conocidas (evitar desbordes del texto)
        for X, Y, W, H, name, color in self.last_detections:
            cv2.rectangle(frame, (X, Y), (X + W, Y + H), color, 2)
            self._draw_label(frame, X, Y, W, H, name, color)
        cv2.imshow("Frame", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cap.stop()

    def _setup_folder_monitor(self):
        """Configura el monitor para la carpeta de rostros"""
        try:
            # Crear el monitor y el observador
            event_handler = FolderMonitor(self)
            observer = Observer()
            observer.schedule(event_handler, self._faces_folder, recursive=False)
            observer.daemon = True  # Terminar cuando el programa principal termine
            observer.start()
            self._folder_observer = (observer, event_handler)
            print(f"[INFO] Monitor de carpeta iniciado: {self._faces_folder}")
        except Exception as e:
            print(f"[ERROR] No se pudo iniciar el monitor de carpeta: {e}")
    
    def star_detection(self):
        self._cap.start(self._on_frame)
    
    def stop_detection(self):
        # Detener el observador de archivos si existe
        if self._folder_observer:
            try:
                self._folder_observer[0].stop()
                self._folder_observer[0].join()
                print("[INFO] Monitor de carpeta detenido")
            except Exception as e:
                print(f"[ERROR] Error al detener el monitor: {e}")
        
        # Detener la captura de video
        self._cap.stop()


cap = VideoCapture(VideoConfig())
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, 30)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

asistencia = Asistencia()

# Obtener la ruta base de la aplicación (backend/app)
current_file_path = os.path.abspath(__file__)
current_dir_path = os.path.dirname(current_file_path)
app_dir_path = os.path.dirname(os.path.dirname(current_dir_path))  # Subir dos niveles desde face-services

# Usar la nueva ubicación de las fotos
optimized_faces_path = os.path.join(app_dir_path, "static", "people_photos")

face_detector = FaceDetector(cap, asistencia, optimized_faces_path)

face_detector.star_detection()