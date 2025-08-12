# Vision Attendances - Frontend

Aplicación web para gestión de asistencias con reconocimiento facial, desarrollada con React, TypeScript y Vite.

## Características

- Registro y gestión de personas con fotografías
- Captura de fotos desde la cámara web
- Carga de imágenes desde el dispositivo
- Interfaz de usuario moderna y responsiva
- Manejo robusto de errores y feedback visual

## Requisitos previos

- Node.js (v18 o superior)
- npm o yarn
- Conexión a internet para las dependencias
- Cámara web (para funcionalidad de captura de fotos)

## Instalación

1. Clona el repositorio:

```bash
git clone https://github.com/tu-usuario/vision-attendances.git
cd vision-attendances/frontend
```

2. Instala las dependencias:

```bash
npm install
# o con yarn
yarn install
```

## Configuración

Crea un archivo `.env` en la raíz del proyecto frontend con las siguientes variables:

```
VITE_API_BASE_URL=http://localhost:8000
```

IMPORTANTE: Si no se crea el .env, el proyecto no funcionará correctamente, especificamente las imágenes.
Ajusta la URL según la configuración de tu backend.

## Ejecución

### Modo desarrollo

```bash
npm run dev
# o con yarn
yarn dev
```

Esto iniciará el servidor de desarrollo en `http://localhost:5173`.

### Compilación para producción

```bash
npm run build
# o con yarn
yarn build
```

Los archivos compilados se generarán en la carpeta `dist`.

### Vista previa de producción

```bash
npm run preview
# o con yarn
yarn preview
```

## Estructura del proyecto (featured-based architecture)

```
src/
├── features/           # Módulos funcionales de la aplicación
│   ├── people/         # Gestión de personas
│   └── attendances/    # Gestión de asistencias
├── shared/             # Componentes y utilidades compartidas
│   ├── api/            # Configuración y utilidades de API
│   ├── hooks/          # Hooks personalizados
│   ├── layouts/        # Layouts de la aplicación
│   └── ui/             # Componentes de UI reutilizables
├── App.tsx             # Componente principal
└── main.tsx           # Punto de entrada
```

## Tecnologías principales

- React 19
- TypeScript
- Vite
- React Query
- Framer Motion
- Tailwind CSS

## Licencia

MIT