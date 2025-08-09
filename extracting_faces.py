import cv2
import os
def _resolve_haarcascade():
     """Devuelve la ruta del haarcascade_frontalface_default.xml en instalaciones típicas.
     Compatible con conda-forge (macOS/Windows/Linux) y Homebrew.
     """
     filename = "haarcascade_frontalface_default.xml"
     candidates = []
     # 1) Si cv2.data existe
     try:
          data_dir = cv2.data.haarcascades  # type: ignore[attr-defined]
          candidates.append(os.path.join(data_dir, filename))
     except Exception:
          pass
     # 2) Junto al paquete cv2 (a veces existe carpeta data/)
     candidates.append(os.path.join(os.path.dirname(cv2.__file__), "data", filename))
     # 3) Instalaciones conda-forge
     conda_prefix = os.environ.get("CONDA_PREFIX", "")
     if conda_prefix:
          candidates.append(os.path.join(conda_prefix, "share", "opencv4", "haarcascades", filename))
          candidates.append(os.path.join(conda_prefix, "share", "opencv", "haarcascades", filename))
          candidates.append(os.path.join(conda_prefix, "etc", "haarcascades", filename))
     # 4) Rutas de sistema comunes (Linux/macOS/Homebrew)
     candidates.extend([
          "/usr/share/opencv4/haarcascades/" + filename,
          "/usr/local/share/opencv4/haarcascades/" + filename,
          "/opt/homebrew/opt/opencv/share/opencv4/haarcascades/" + filename,
     ])
     for path in candidates:
          if path and os.path.exists(path):
               return path
     raise FileNotFoundError(
          "No se encontró el clasificador Haar. Instala opencv con conda-forge o especifica la ruta manualmente."
     )

imagesPath = os.path.join(os.path.curdir, "input_images")
if not os.path.exists("faces"):
     os.makedirs("faces")
     print("Nueva carpeta: faces")
# Detector facial
faceClassif = cv2.CascadeClassifier(_resolve_haarcascade())
for imageName in os.listdir(imagesPath):
     print(imageName)
     image = cv2.imread(os.path.join(imagesPath, imageName))
     if image is None:
          raise ValueError(f"Error al leer la imagen: {imageName}")
     gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
     faces = faceClassif.detectMultiScale(gray, 1.1, 5)
     if len(faces) == 0:
          continue
     base_name = os.path.splitext(imageName)[0]
     for i, (x, y, w, h) in enumerate(faces):
          #cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
          face = image[y:y + h, x:x + w]
          face = cv2.resize(face, (150, 150))
          out_name = f"{base_name}.jpg" if len(faces) == 1 else f"{base_name}_{i}.jpg"
          cv2.imwrite(os.path.join("faces", out_name), face)
          #cv2.imshow("face", face)
          #cv2.waitKey(0)
     #cv2.imshow("Image", image)
     #cv2.waitKey(0)
#cv2.destroyAllWindows()

