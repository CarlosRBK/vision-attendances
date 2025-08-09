import cv2
import os
import face_recognition
import platform
import time
 
# Habilitar optimizaciones de OpenCV
cv2.setUseOptimized(True)
 
from datetime import datetime
#fichero
# Obtener la fecha actual y generar el nombre del archivo
fecha_actual = datetime.now().strftime("%d-%m-%Y")  # formato 12-07-2025
archivo_asistencia = f"asistencia_{fecha_actual}.txt"
asistentes_registrados = set()
#archivo_asistencia = "asistencia.txt"
 
# Cargar asistencias anteriores (si se quiere continuar la lista entre ejecuciones)
if os.path.exists(archivo_asistencia):
    with open(archivo_asistencia, "r", encoding="utf-8") as f:
        for linea in f:
            asistentes_registrados.add(linea.strip())
#fin fichero
             
# Resolver ruta del clasificador Haar de forma robusta (conda-forge/Homebrew)
def _resolve_haarcascade():
     filename = "haarcascade_frontalface_default.xml"
     candidates = []
     try:
          data_dir = cv2.data.haarcascades  # type: ignore[attr-defined]
          candidates.append(os.path.join(data_dir, filename))
     except Exception:
          pass
     candidates.append(os.path.join(os.path.dirname(cv2.__file__), "data", filename))
     conda_prefix = os.environ.get("CONDA_PREFIX", "")
     if conda_prefix:
          candidates.append(os.path.join(conda_prefix, "share", "opencv4", "haarcascades", filename))
          candidates.append(os.path.join(conda_prefix, "share", "opencv", "haarcascades", filename))
          candidates.append(os.path.join(conda_prefix, "etc", "haarcascades", filename))
     candidates.extend([
          "/usr/share/opencv4/haarcascades/" + filename,
          "/usr/local/share/opencv4/haarcascades/" + filename,
          "/opt/homebrew/opt/opencv/share/opencv4/haarcascades/" + filename,
     ])
     for path in candidates:
          if path and os.path.exists(path):
               return path
     raise FileNotFoundError("No se encontró el clasificador Haar. Instala opencv con conda-forge o especifica la ruta manualmente.")

# Codificar los rostros extraidos
imageFacesPath = os.path.join(os.path.curdir, "faces")
facesEncodings = []
facesNames = []
for file_name in os.listdir(imageFacesPath):
     image = cv2.imread(os.path.join(imageFacesPath, file_name))
     if image is None:
          raise ValueError(f"Error al leer la imagen: {file_name}")
     image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
     encs = face_recognition.face_encodings(image, known_face_locations=[(0, 150, 150, 0)])
     if not encs:
          # No se detectó rostro válido en esta imagen recortada
          continue
     facesEncodings.append(encs[0])
     facesNames.append(file_name.split(".")[0])
#print(facesEncodings)
#print(facesNames)
if not facesEncodings:
     raise RuntimeError("No se encontraron rostros en la carpeta 'faces/'. Ejecuta primero extracting_faces.py y verifica que existan imágenes.")
##############################################
# LEYENDO VIDEO
def open_default_camera():
     system = platform.system()
     candidates = []
     if system == "Windows":
          candidates = [(0, cv2.CAP_DSHOW), (0, None)]
     elif system == "Darwin":  # macOS
          candidates = [(0, cv2.CAP_AVFOUNDATION), (0, None)]
     else:
          candidates = [(0, None)]
     for idx, backend in candidates:
          cap = cv2.VideoCapture(idx) if backend is None else cv2.VideoCapture(idx, backend)
          if cap.isOpened():
               return cap
          cap.release()
     # Fallback: probar más índices sin backend explícito
     for idx in range(1, 4):
          cap = cv2.VideoCapture(idx)
          if cap.isOpened():
               return cap
          cap.release()
     raise RuntimeError("No se pudo abrir la cámara. Verifica permisos del sistema y que no esté en uso por otra aplicación.")

cap = open_default_camera()
# Intentar fijar propiedades de captura para mejorar FPS/latencia
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, 30)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
# Detector facial
faceClassif = cv2.CascadeClassifier(_resolve_haarcascade())
 
# Parámetros de rendimiento
process_every_n = 2  # procesa 1 de cada 2 cuadros
scale = 0.5          # detectar a media resolución
frame_count = 0
last_detections = []  # lista de tuplas (X,Y,W,H,name,color)

# Dibujo de etiqueta adaptativa para evitar desborde del texto
def _draw_label(frame, x, y, w, h, label, color):
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
     cv2.putText(frame, label, (text_x, text_y), font_face, scale, (255, 255, 255), thickness, cv2.LINE_AA)
while True:
     ret, frame = cap.read()
     if ret == False:
          break
     frame = cv2.flip(frame, 1)
     frame_count += 1
     process_this_frame = (frame_count % process_every_n == 0)
     if process_this_frame:
          # Detección en resolución reducida
          small = cv2.resize(frame, (0, 0), fx=scale, fy=scale)
          gray_small = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
          faces_small = faceClassif.detectMultiScale(gray_small, 1.2, 5)
          current = []
          if len(faces_small) > 0:
               inv_scale = 1.0 / scale
               for (sx, sy, sw, sh) in faces_small:
                    X = int(sx * inv_scale)
                    Y = int(sy * inv_scale)
                    W = int(sw * inv_scale)
                    H = int(sh * inv_scale)
                    roi = frame[Y:Y + H, X:X + W]
                    if roi.size == 0:
                         continue
                    roi_rgb = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)
                    # Reducir tamaño del ROI para acelerar el cómputo del embedding
                    roi_rgb_small = cv2.resize(roi_rgb, (150, 150))
                    encs = face_recognition.face_encodings(
                         roi_rgb_small,
                         known_face_locations=[(0, 150, 150, 0)],
                         num_jitters=1,
                    )
                    name = "Desconocido"
                    color = (50, 50, 255)
                    if encs:
                         actual = encs[0]
                         result = face_recognition.compare_faces(facesEncodings, actual)
                         if True in result:
                              index = result.index(True)
                              name = facesNames[index]
                              color = (125, 220, 0)
                              # ✅ Guardar en archivo si no está registrado aún
                              if name not in asistentes_registrados:
                                   fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                   with open(archivo_asistencia, "a", encoding="utf-8") as f:
                                        f.write(f"{fecha_hora} - {name}\n")
                                   asistentes_registrados.add(name)
                    current.append((X, Y, W, H, name, color))
          last_detections = current
     # Dibujo de las últimas detecciones conocidas (evitar desbordes del texto)
     for (X, Y, W, H, name, color) in last_detections:
          cv2.rectangle(frame, (X, Y), (X + W, Y + H), color, 2)
          _draw_label(frame, X, Y, W, H, name, color)
     cv2.imshow("Frame", frame)
     k = cv2.waitKey(1) & 0xFF
     if k == 27:
          break
cap.release()
cv2.destroyAllWindows()
