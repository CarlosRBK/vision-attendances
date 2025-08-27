import base64
import io
import cv2
import os

import face_recognition
import numpy as np

from ...utils.face_utils import resolve_haarcascade

face_detector = cv2.CascadeClassifier(resolve_haarcascade())

class FaceExtractor:
    def __init__(self, output_folder: str) -> None:
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

    def _base64_to_np(self, image_base64: str) -> np.ndarray:
        img_bytes = base64.b64decode(image_base64)
        image_np = face_recognition.load_image_file(io.BytesIO(img_bytes))
        return image_np

    def extract_faces(self, base64_img: str, file_name: str) -> None:
        image = self._base64_to_np(base64_img) 
        if image is None:
            raise ValueError("Error al leer la imagen")
        
        image_gray_scale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Obtenemos los datos de las caras en la imagen
        faces = face_detector.detectMultiScale(image_gray_scale, 1.1, 5)
        if len(faces) == 0:
            raise ValueError("No se detectaron caras en la imagen")

        for i, (x, y, w, h) in enumerate(faces):
            # obtenemos la imagen de la cara
            face = image[y : y + h, x : x + w]

            # la optimizamos a 150x150 pixeles
            face = cv2.resize(face, (150, 150))

            # guardamos la imagen de la cara en la carpeta faces/
            out_name = f"{file_name}.jpg" if len(faces) == 1 else f"{file_name}_{i}.jpg"
            cv2.imwrite(os.path.join(output_file_path, out_name), face)


current_file_path = os.path.abspath(__file__)
current_dir_path = os.path.dirname(current_file_path)
output_file_path = os.path.join(current_dir_path, "optimized_faces")

face_extractor = FaceExtractor(output_file_path)