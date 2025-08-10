import cv2
import os
import face_recognition
import numpy as np
from datetime import datetime
from PIL import Image

from resolve_harcascade import resolve_haarcascade
from get_video_capture import get_video_capture

current_file_path = os.path.abspath(__file__)
current_dir_path = os.path.dirname(current_file_path)

optimized_faces_path = os.path.join(current_dir_path, "optimized_faces")

# Habilitar optimizaciones de OpenCV
cv2.setUseOptimized(True)


# fichero
# Obtener la fecha actual y generar el nombre del archivo
fecha_actual = datetime.now().strftime("%d-%m-%Y")  # formato 12-07-2025
archivo_asistencia = f"asistencia_{fecha_actual}.txt"
asistentes_registrados = set()
# archivo_asistencia = "asistencia.txt"

# Cargar asistencias anteriores (si se quiere continuar la lista entre ejecuciones)
if os.path.exists(archivo_asistencia):
    with open(archivo_asistencia, "r", encoding="utf-8") as f:
        for linea in f:
            asistentes_registrados.add(linea.strip())
# fin fichero


# Codificar los rostros extraidos
faces_encodings = []
faces_names = []
for file_name in os.listdir(optimized_faces_path):
    file_path = os.path.join(optimized_faces_path, file_name)
    # Carga robusta y normalización: garantizar RGB uint8 y memoria C-contigua (Windows)
    img = Image.open(file_path).convert("RGB")
    image = np.array(img, dtype=np.uint8)
    image = np.ascontiguousarray(image)

    height, width = image.shape[:2]
    print(f"Procesando imagen: {file_name} (dimensiones: {width}x{height})")
    print(f"Tipo de imagen: {image.dtype}, Forma: {image.shape}, Contiguous: {image.flags['C_CONTIGUOUS']}")
    print("Min pixel value:", image.min())
    print("Max pixel value:", image.max())
    print("PIL mode:", img.mode)  # Debe ser 'RGB'

    encs = face_recognition.face_encodings(
        image, known_face_locations=[(0, 150, 150, 0)]
    )
    if not encs:
        # No se detectó rostro válido en esta imagen recortada
        continue
    faces_encodings.append(encs[0])
    faces_names.append(file_name.split(".")[0])

if not faces_encodings:
    raise RuntimeError(
        f"No se encontraron rostros en la carpeta '{optimized_faces_path}'. Ejecuta primero extracting_faces.py y verifica que existan imágenes."
    )


# Inicializar captura de video
cap = get_video_capture()

# Intentar fijar propiedades de captura para mejorar FPS/latencia
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, 30)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

# Parámetros de rendimiento
process_every_n = 2  # procesa 1 de cada 2 cuadros
scale = 0.5  # detectar a media resolución
frame_count = 0
last_detections = []  # lista de tuplas (X,Y,W,H,name,color)

face_detector = cv2.CascadeClassifier(resolve_haarcascade())


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


while True:
    ret, frame = cap.read()
    if ret == False:
        break
    frame = cv2.flip(frame, 1)
    frame_count += 1
    process_this_frame = frame_count % process_every_n == 0
    if process_this_frame:
        # Detección en resolución reducida
        small = cv2.resize(frame, (0, 0), fx=scale, fy=scale)
        gray_small = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
        faces_small = face_detector.detectMultiScale(gray_small, 1.2, 5)
        current = []
        if len(faces_small) > 0:
            inv_scale = 1.0 / scale
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
                    result = face_recognition.compare_faces(faces_encodings, actual)
                    if True in result:
                        index = result.index(True)
                        name = faces_names[index]
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
    for X, Y, W, H, name, color in last_detections:
        cv2.rectangle(frame, (X, Y), (X + W, Y + H), color, 2)
        _draw_label(frame, X, Y, W, H, name, color)
    cv2.imshow("Frame", frame)
    k = cv2.waitKey(1) & 0xFF
    if k == 27:
        break
cap.release()
cv2.destroyAllWindows()
