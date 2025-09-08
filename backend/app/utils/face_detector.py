import cv2
import face_recognition
import numpy as np

from ..modules.attendances.video_capture import VideoCapture, VideoConfig
from .face_utils import resolve_haarcascade
from ..modules.attendances.loop_manager import LoopManager


class Face:
    def __init__(self, id, name, encoding):
        self.id = id
        self.name = name
        self.encoding = encoding


class FaceDetector:
    _cap: VideoCapture
    _face_detector: cv2.CascadeClassifier
    _loop_manager: LoopManager = LoopManager(lambda: face_detector._start_detection())

    # Parámetros de rendimiento
    process_every_n = 2  # procesa 1 de cada 2 cuadros
    scale = 0.5  # detectar a media resolución
    last_detections = []  # lista de tuplas (X,Y,W,H,name,color)

    # Parámetros de codificación
    faces: list[Face] = []
    faces_encodings: list[np.ndarray] = []
    
    # Listeners
    detect_faces_listeners = []

    def __init__(self, cap: VideoCapture) -> None:
        self._cap = cap
        self._face_detector = cv2.CascadeClassifier(resolve_haarcascade())

        self._cap.add_listener(lambda frame: self.detect_faces(frame))

    def load_faces(self, faces: list[Face]):
        """Carga los rostros conocidos. En caso de que ya hayan sido cargados, no hace nada.
        """
        if len(self.faces) > 0:
            return
        self.faces = faces
        self.faces_encodings = [f.encoding for f in faces]

    def append_face(self, id: str, name: str, encodings: np.ndarray) -> None:
        np_encodings = np.array(encodings)
        if np_encodings.shape != (1, 512):
            raise ValueError("Encodings must be a 1D array of 512 floats.")
        self.faces.append(Face(id, name, np_encodings))
        self.faces_encodings.append(np_encodings)

    def _draw_label(
        self,
        frame: cv2.typing.MatLike,
        x: int,
        y: int,
        w: int,
        h: int,
        label: str,
        color,
    ):
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
        cv2.rectangle(
            frame, (box_x, box_y), (box_x + rect_w, box_y + rect_h), color, -1
        )
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

    def detect_faces(self, frame: cv2.typing.MatLike):
        frame = cv2.flip(frame, 1)
        process_this_frame = self._cap.frame_count % self.process_every_n == 0
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
                        result = face_recognition.compare_faces(
                            self.faces_encodings, actual
                        )
                        if True in result:
                            index = result.index(True)
                            name = self.faces[index].name
                            color = (125, 220, 0)
                    current.append((X, Y, W, H, name, color))
            self.last_detections = current
        # Dibujo de las últimas detecciones conocidas (evitar desbordes del texto)
        for X, Y, W, H, name, color in self.last_detections:
            cv2.rectangle(frame, (X, Y), (X + W, Y + H), color, 2)
            self._draw_label(frame, X, Y, W, H, name, color)

        # Llamar a los listeners
        if len(self.detect_faces_listeners) > 0:
            for listener in self.detect_faces_listeners:
                self._loop_manager.delegar_async(
                    listener,
                    self.last_detections,
                )

        cv2.imshow("Frame", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            self._loop_manager.stop()

    def on_detected_faces(self, listener):
        """Cada listener recibirá una lista de caras detectadas,
        cada cara esta representada como (X, Y, W, H, name, color)"""
        self.detect_faces_listeners.append(listener)

    def _start_detection(self):
        self._cap.start(lambda: self._loop_manager.is_running())

    def start_detection(self):
        """Presiona q para finalizar"""
        if not self.faces:
            print("⚠️ No hay rostros conocidos por detectar.")
        self._loop_manager.start()
        self.is_running = True
        
    def stop_detection(self):
        self._loop_manager.stop()
        self.is_running = False


cap = VideoCapture(VideoConfig())
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, 30)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

face_detector = FaceDetector(cap)
