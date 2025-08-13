import cv2
import os
from main import FaceDetector

current_file_path = os.path.abspath(__file__)
current_dir_path = os.path.dirname(current_file_path)

input_file_path = os.path.join(current_dir_path, "input_images")
output_file_path = os.path.join(current_dir_path, "optimized_faces")

# Aseguramos que exista la carpeta con las caras
if not os.path.exists(output_file_path):
    os.makedirs(output_file_path)

# Detector facial
face_detector = cv2.CascadeClassifier(FaceDetector.resolve_haarcascade())

for image_name in os.listdir(input_file_path):
    image = cv2.imread(os.path.join(input_file_path, image_name))

    if image is None:
        raise ValueError(f"Error al leer la imagen: {image_name}")
    
    image_gray_scale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Obtenemos los datos de las caras en la imagen
    faces = face_detector.detectMultiScale(image_gray_scale, 1.1, 5)
    if len(faces) == 0:
        continue

    
    base_file_name = os.path.splitext(image_name)[0]
    for i, (x, y, w, h) in enumerate(faces):
        # obtenemos la imagen de la cara
        face = image[y : y + h, x : x + w]

        # la optimizamos a 150x150 pixeles
        face = cv2.resize(face, (150, 150))

        # guardamos la imagen de la cara en la carpeta faces/
        out_name = f"{base_file_name}.jpg" if len(faces) == 1 else f"{base_file_name}_{i}.jpg"
        cv2.imwrite(os.path.join(output_file_path, out_name), face)
