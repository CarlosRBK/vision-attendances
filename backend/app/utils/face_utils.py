import os
import cv2

def resolve_haarcascade() -> str:
    """
    Devuelve la ruta del clasificador Haar 'haarcascade_frontalface_default.xml'.
    Compatible con instalaciones de pip, conda-forge y Homebrew.
    """
    filename = "haarcascade_frontalface_default.xml"
    candidates = []

    # Ruta estándar en cv2
    try:
        data_dir = cv2.data.haarcascades
        candidates.append(os.path.join(data_dir, filename))
    except Exception:
        pass

    # Junto al paquete cv2
    candidates.append(os.path.join(os.path.dirname(cv2.__file__), "data", filename))

    # Posibles rutas de conda-forge
    conda_prefix = os.environ.get("CONDA_PREFIX", "")
    if conda_prefix:
        candidates.extend([
            os.path.join(conda_prefix, "share", "opencv4", "haarcascades", filename),
            os.path.join(conda_prefix, "share", "opencv", "haarcascades", filename),
            os.path.join(conda_prefix, "etc", "haarcascades", filename),
        ])

    # Rutas de sistema comunes
    candidates.extend([
        "/usr/share/opencv4/haarcascades/" + filename,
        "/usr/local/share/opencv4/haarcascades/" + filename,
        "/opt/homebrew/opt/opencv/share/opencv4/haarcascades/" + filename,
    ])

    # Buscar la primera existente
    for path in candidates:
        if path and os.path.exists(path):
            return path

    raise FileNotFoundError(
        "No se encontró el clasificador Haar. "
        "Instala opencv con conda-forge o especifica la ruta manualmente."
    )

def detect_faces(image):
    """
    Detecta rostros en una imagen usando Haarcascade.
    Retorna lista de (x, y, w, h).
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    face_detector = cv2.CascadeClassifier(resolve_haarcascade())
    faces = face_detector.detectMultiScale(gray, 1.1, 5)
    return faces
