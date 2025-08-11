import base64
import io
import face_recognition
import numpy as np


async def img_to_np(image_base64: str) -> np.ndarray:
    img_bytes = base64.b64decode(image_base64)
    image_np = face_recognition.load_image_file(io.BytesIO(img_bytes))
    return image_np