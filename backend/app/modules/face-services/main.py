from typing import Union
import cv2
import os
import face_recognition
import numpy as np
from datetime import datetime


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

        self.load_faces_from_folder(faces_folder)
    
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
        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)
            image = cv2.imread(file_path)
            if image is None:
                print(f"Error al cargar la imagen: {file_name}. Verifica que sea una imagen válida.")
                continue

            encoding = self._get_encodings(image)
            if encoding is not None:
                self.faces_encodings.append(encoding)
                self.faces_names.append(file_name.split(".")[0])
            else:
                print(f"No se detectó un rostro válido en la imagen: {file_name}")

        if not self.faces_encodings:
            raise RuntimeError(
                f"No se encontraron rostros en la carpeta '{folder_path}'. Ejecuta primero extracting_faces.py y verifica que existan imágenes."
            )

    def _draw_label(self, frame: cv2.typing.MatLike, x: int, y: int, w: int, h: int, label: str, color):
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

    def _on_frame(self, frame: cv2.typing.MatLike):
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

    def star_detection(self):
        cap.start(self._on_frame)
    
    def stop_detection(self):
        cap.stop()


cap = VideoCapture(VideoConfig())
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, 30)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

asistencia = Asistencia()

current_file_path = os.path.abspath(__file__)
current_dir_path = os.path.dirname(current_file_path)
optimized_faces_path = os.path.join(current_dir_path, "optimized_faces")

face_detector = FaceDetector(cap, asistencia, optimized_faces_path)

face_detector.star_detection()