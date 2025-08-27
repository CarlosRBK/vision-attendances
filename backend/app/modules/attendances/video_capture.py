import platform
import cv2


class VideoConfig:
    def __init__(self, video_source: int = 0, use_optimized: bool = True):
        self.video_source = video_source
        self.use_optimized = use_optimized

class VideoCapture:
    _cap: cv2.VideoCapture
    _listeners = []
    _is_capturing = False

    frame_count = 0
    cap_configs = []

    def _get_video_capture(self, target_source: int = 0) -> cv2.VideoCapture:
        """Obtiene una captura de video de la cámara."""
        system = platform.system()
        candidates = []
        if system == "Windows":
            candidates = [(target_source, cv2.CAP_DSHOW), (0, None)]
        elif system == "Darwin":  # macOS
            candidates = [(target_source, cv2.CAP_AVFOUNDATION), (0, None)]
        else:
            candidates = [(target_source, None)]
        for source, backend in candidates:
            cap = cv2.VideoCapture(source) if backend is None else cv2.VideoCapture(source, backend)
            if cap.isOpened():
                return cap
            cap.release()
        # Fallback: probar más índices sin backend explícito
        for source in range(target_source, 4):
            cap = cv2.VideoCapture(source)
            if cap.isOpened():
                return cap
            cap.release()
        raise RuntimeError("No se pudo abrir la cámara. Verifica permisos del sistema y que no esté en uso por otra aplicación.")

    def __init__(self, config: VideoConfig):
        cv2.setUseOptimized(config.use_optimized)

    def set(self, propId: int, value: float):
        """Establece un parámetro de configuración de la cámara."""
        self.cap_configs.append((propId, value))

    def add_listener(self, listener):
        if listener not in self._listeners:
            self._listeners.append(listener)

    def _loop(self, can_run):
        while can_run():
            self.frame_count += 1
            ret, frame = self._cap.read()
            if not ret:
                print("No se pudo capturar el frame")
                break
            for listener in self._listeners:
                listener(frame)

    def start(self, can_run):
        self._cap = self._get_video_capture()

        for propId, value in self.cap_configs:
            self._cap.set(propId, value)

        self.frame_count = 0
        self._loop(lambda: can_run())
        self._cap.release()
        cv2.destroyAllWindows()
        self._is_capturing = False

