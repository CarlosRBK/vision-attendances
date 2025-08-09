
## Primeros pasos

Asegúrate de tener **conda** disponible en tu terminal y crea/activa el entorno (igual en macOS y Windows):

```bash
conda env create -f environment.yml
conda activate face-recognition
```

Prepara datos y extrae rostros:

macOS / Linux:
```bash
mkdir -p input_images faces
# Copia imágenes con rostros a input_images/
python extracting_faces.py
```

Windows (PowerShell/CMD):
```powershell
mkdir input_images
mkdir faces
# Copia imágenes con rostros a input_images/
python extracting_faces.py
```

Ejecuta el reconocimiento con la webcam:

```bash
python f_recognition.py
```

## Funcionamiento

- Las imágenes de los rostros a detectar se cargan en la carpeta **input_images**, las imágenes pueden tener varias personas
- **extracting_faces.py**: El algoritmo reconoce un conjunto de rostro enumerándolos de 0 a n según la cantidad de rostros detectados guardándolos en la carpeta **faces**.
- **f_recognition.py** se encarga de correr el algoritmo para detectar rostros y generar un archivo .txt con las coincidencias encontradas.

### Notas multiplataforma

- En macOS: concede permisos de Cámara a Terminal/VS Code en Preferencias del Sistema > Privacidad y seguridad > Cámara.
- En Windows: revisa Configuración > Privacidad > Cámara y que ninguna app esté ocupando la cámara.
- El script selecciona automáticamente el backend de cámara según el sistema operativo.

## Tareas

- [ ] Modularizar el código. Se puede empezar por extraer la configuraciones básicas como las rutas y el target FPS en un archivo de configuración. Luego hay que corregir la documentación.
- [ ] Aumentar los FPS
- [ ] Agregar una interfaz web que no de vergüenza (####)