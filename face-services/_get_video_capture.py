import platform

import cv2


def get_video_capture():
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
