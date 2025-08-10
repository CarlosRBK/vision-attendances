import cv2
import os

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
