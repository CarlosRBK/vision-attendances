import os
import cv2
import face_recognition
import numpy as np
from pathlib import Path
from PIL import Image

def debug_single_image(image_path):
    """
    Función para debuggear una imagen específica que está causando problemas
    """
    print(f"=== Debug de imagen: {image_path} ===")
    
    # Método 1: PIL
    try:
        pil_image = Image.open(image_path)
        print(f"PIL - Mode: {pil_image.mode}, Size: {pil_image.size}")
        
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')
            print("Convertido a RGB")
        
        image_array = np.array(pil_image)
        print(f"PIL Array - Shape: {image_array.shape}, Dtype: {image_array.dtype}")
        print(f"PIL Array - Min: {image_array.min()}, Max: {image_array.max()}")
        print(f"PIL Array - Contiguous: {image_array.flags['C_CONTIGUOUS']}")
        
        # Asegurar formato correcto
        if not image_array.flags['C_CONTIGUOUS']:
            image_array = np.ascontiguousarray(image_array)
            print("Array hecho contíguo")
        
        # Intentar extraer encoding
        try:
            encodings = face_recognition.face_encodings(image_array)
            print(f"✓ PIL method successful, encodings found: {len(encodings)}")
            return image_array, encodings
        except Exception as e:
            print(f"✗ PIL method failed: {e}")
    
    except Exception as e:
        print(f"✗ PIL loading failed: {e}")
    
    # Método 2: OpenCV
    try:
        image_bgr = cv2.imread(image_path)
        if image_bgr is not None:
            image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
            print(f"OpenCV Array - Shape: {image_rgb.shape}, Dtype: {image_rgb.dtype}")
            print(f"OpenCV Array - Min: {image_rgb.min()}, Max: {image_rgb.max()}")
            print(f"OpenCV Array - Contiguous: {image_rgb.flags['C_CONTIGUOUS']}")
            
            try:
                encodings = face_recognition.face_encodings(image_rgb)
                print(f"✓ OpenCV method successful, encodings found: {len(encodings)}")
                return image_rgb, encodings
            except Exception as e:
                print(f"✗ OpenCV method failed: {e}")
        else:
            print("✗ OpenCV couldn't load the image")
    except Exception as e:
        print(f"✗ OpenCV loading failed: {e}")
    
    # Método 3: face_recognition
    try:
        image = face_recognition.load_image_file(image_path)
        print(f"face_recognition Array - Shape: {image.shape}, Dtype: {image.dtype}")
        print(f"face_recognition Array - Min: {image.min()}, Max: {image.max()}")
        print(f"face_recognition Array - Contiguous: {image.flags['C_CONTIGUOUS']}")
        
        try:
            encodings = face_recognition.face_encodings(image)
            print(f"✓ face_recognition method successful, encodings found: {len(encodings)}")
            return image, encodings
        except Exception as e:
            print(f"✗ face_recognition method failed: {e}")
    except Exception as e:
        print(f"✗ face_recognition loading failed: {e}")
    
    return None, []

def extract_face_encodings_from_folder(images_folder_path, output_file=None):
    """
    Extrae los encodings de todas las imágenes de rostros en una carpeta.
    
    Args:
        images_folder_path (str): Ruta a la carpeta con las imágenes
        output_file (str, optional): Ruta para guardar los encodings en un archivo .npy
    
    Returns:
        tuple: (encodings_array, image_names) donde encodings_array es un numpy array
               con todos los encodings e image_names es una lista con los nombres de archivos
    """
    
    # Extensiones de imagen válidas
    valid_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}
    
    # Listas para almacenar encodings y nombres
    all_encodings = []
    image_names = []
    failed_images = []
    
    # Convertir a Path object para mejor manejo
    folder_path = Path(images_folder_path)
    
    if not folder_path.exists():
        raise FileNotFoundError(f"La carpeta {images_folder_path} no existe")
    
    # Obtener todas las imágenes
    image_files = [f for f in folder_path.iterdir() 
                   if f.is_file() and f.suffix.lower() in valid_extensions]
    
    print(f"Procesando {len(image_files)} imágenes...")
    
    for i, image_path in enumerate(image_files):
        try:
            # Múltiples métodos de carga para mayor compatibilidad
            image = None
            
            # Método 1: Usar PIL y convertir a numpy array
            try:
                pil_image = Image.open(str(image_path))
                
                # Asegurar que esté en RGB
                if pil_image.mode != 'RGB':
                    pil_image = pil_image.convert('RGB')
                
                # Convertir a numpy array
                image = np.array(pil_image)
                
                print(f"Debug - PIL: {image_path.name}, Shape: {image.shape}, Dtype: {image.dtype}")
                
            except Exception as e:
                print(f"Error cargando con PIL {image_path.name}: {e}")
            
            # Método 2: Si PIL falla, usar OpenCV
            if image is None:
                try:
                    image_bgr = cv2.imread(str(image_path))
                    if image_bgr is not None:
                        image = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
                        print(f"Debug - OpenCV: {image_path.name}, Shape: {image.shape}, Dtype: {image.dtype}")
                except Exception as e:
                    print(f"Error cargando con OpenCV {image_path.name}: {e}")
            
            # Método 3: Si ambos fallan, usar face_recognition
            if image is None:
                try:
                    image = face_recognition.load_image_file(str(image_path))
                    print(f"Debug - face_recognition: {image_path.name}, Shape: {image.shape}, Dtype: {image.dtype}")
                except Exception as e:
                    print(f"Error cargando con face_recognition {image_path.name}: {e}")
            
            if image is None:
                print(f"✗ No se pudo cargar la imagen: {image_path.name}")
                failed_images.append(image_path.name)
                continue
            
            # Verificar y asegurar formato correcto
            if len(image.shape) != 3 or image.shape[2] != 3:
                print(f"✗ Formato incorrecto para {image_path.name}: {image.shape}")
                failed_images.append(image_path.name)
                continue
            
            # Asegurar que sea uint8
            if image.dtype != np.uint8:
                image = image.astype(np.uint8)
            
            # Asegurar que los valores estén en el rango correcto
            if image.max() <= 1.0:
                image = (image * 255).astype(np.uint8)
            
            # Asegurar que el array sea contíguo en memoria
            if not image.flags['C_CONTIGUOUS']:
                image = np.ascontiguousarray(image)
            
            # Extraer encodings
            face_encodings = face_recognition.face_encodings(image)
            
            if len(face_encodings) > 0:
                # Si hay múltiples rostros, tomar el primero
                encoding = face_encodings[0]
                all_encodings.append(encoding)
                image_names.append(image_path.name)
                
                print(f"✓ Procesada: {image_path.name} ({i+1}/{len(image_files)})")
            else:
                print(f"✗ No se detectó rostro en: {image_path.name}")
                failed_images.append(image_path.name)
                
        except Exception as e:
            print(f"✗ Error procesando {image_path.name}: {str(e)}")
            failed_images.append(image_path.name)
    
    # Convertir a numpy array
    if all_encodings:
        encodings_array = np.array(all_encodings)
        
        print(f"\n✓ Procesamiento completado!")
        print(f"  - Encodings extraídos: {len(all_encodings)}")
        print(f"  - Imágenes fallidas: {len(failed_images)}")
        print(f"  - Shape del array: {encodings_array.shape}")
        
        # Guardar en archivo si se especifica
        if output_file:
            np.save(output_file, encodings_array)
            print(f"  - Encodings guardados en: {output_file}")
        
        return encodings_array, image_names
    else:
        print("✗ No se pudieron extraer encodings de ninguna imagen")
        return None, []

def extract_face_encodings_opencv_method(images_folder_path):
    """
    Método alternativo usando OpenCV para cargar imágenes.
    Útil si necesitas más control sobre el preprocesamiento.
    """
    
    valid_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}
    all_encodings = []
    image_names = []
    
    folder_path = Path(images_folder_path)
    image_files = [f for f in folder_path.iterdir() 
                   if f.is_file() and f.suffix.lower() in valid_extensions]
    
    for image_path in image_files:
        try:
            # Cargar imagen con OpenCV
            image_bgr = cv2.imread(str(image_path))
            
            if image_bgr is None:
                print(f"✗ No se pudo cargar: {image_path.name}")
                continue
            
            # Convertir BGR a RGB (face_recognition espera RGB)
            image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
            
            # Extraer encodings
            face_encodings = face_recognition.face_encodings(image_rgb)
            
            if len(face_encodings) > 0:
                encoding = face_encodings[0]
                all_encodings.append(encoding)
                image_names.append(image_path.name)
                print(f"✓ Procesada: {image_path.name}")
            else:
                print(f"✗ No se detectó rostro en: {image_path.name}")
                
        except Exception as e:
            print(f"✗ Error procesando {image_path.name}: {str(e)}")
    
    if all_encodings:
        return np.array(all_encodings), image_names
    return None, []

def debug_single_image(image_path):
    """
    Función para debuggear una imagen específica que está causando problemas
    """
    print(f"=== Debug de imagen: {image_path} ===")
    
    # Método 1: PIL
    try:
        from PIL import Image
        pil_image = Image.open(image_path)
        print(f"PIL - Mode: {pil_image.mode}, Size: {pil_image.size}")
        
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')
            print("Convertido a RGB")
        
        image_array = np.array(pil_image)
        print(f"PIL Array - Shape: {image_array.shape}, Dtype: {image_array.dtype}")
        print(f"PIL Array - Min: {image_array.min()}, Max: {image_array.max()}")
        print(f"PIL Array - Contiguous: {image_array.flags['C_CONTIGUOUS']}")
        
        # Asegurar formato correcto
        if not image_array.flags['C_CONTIGUOUS']:
            image_array = np.ascontiguousarray(image_array)
            print("Array hecho contíguo")
        
        # Intentar extraer encoding
        try:
            encodings = face_recognition.face_encodings(image_array)
            print(f"✓ PIL method successful, encodings found: {len(encodings)}")
            return image_array, encodings
        except Exception as e:
            print(f"✗ PIL method failed: {e}")
    
    except Exception as e:
        print(f"✗ PIL loading failed: {e}")
    
    # Método 2: OpenCV
    try:
        image_bgr = cv2.imread(image_path)
        if image_bgr is not None:
            image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
            print(f"OpenCV Array - Shape: {image_rgb.shape}, Dtype: {image_rgb.dtype}")
            print(f"OpenCV Array - Min: {image_rgb.min()}, Max: {image_rgb.max()}")
            print(f"OpenCV Array - Contiguous: {image_rgb.flags['C_CONTIGUOUS']}")
            
            try:
                encodings = face_recognition.face_encodings(image_rgb)
                print(f"✓ OpenCV method successful, encodings found: {len(encodings)}")
                return image_rgb, encodings
            except Exception as e:
                print(f"✗ OpenCV method failed: {e}")
        else:
            print("✗ OpenCV couldn't load the image")
    except Exception as e:
        print(f"✗ OpenCV loading failed: {e}")
    
    # Método 3: face_recognition
    try:
        image = face_recognition.load_image_file(image_path)
        print(f"face_recognition Array - Shape: {image.shape}, Dtype: {image.dtype}")
        print(f"face_recognition Array - Min: {image.min()}, Max: {image.max()}")
        print(f"face_recognition Array - Contiguous: {image.flags['C_CONTIGUOUS']}")
        
        try:
            encodings = face_recognition.face_encodings(image)
            print(f"✓ face_recognition method successful, encodings found: {len(encodings)}")
            return image, encodings
        except Exception as e:
            print(f"✗ face_recognition method failed: {e}")
    except Exception as e:
        print(f"✗ face_recognition loading failed: {e}")
    
    return None, []

# Ejemplo de uso
if __name__ == "__main__":
    # Para debuggear una imagen específica
    debug_single_image("optimized_faces/yo.jpg")
    
    # Ruta a tu carpeta de imágenes
    images_folder = "optimized_faces"
    
    # Extraer encodings
    encodings, names = extract_face_encodings_from_folder(
        images_folder, 
        output_file="face_encodings.npy"  # Opcional: guardar en archivo
    )
    
    if encodings is not None:
        print(f"\nEncodings extraídos exitosamente!")
        print(f"Shape: {encodings.shape}")
        print(f"Primeros archivos procesados: {names[:5]}")
        
        # Ejemplo: cargar encodings guardados
        # loaded_encodings = np.load("face_encodings.npy")
        # print(f"Encodings cargados: {loaded_encodings.shape}")