# Audio Splitter Suite Avanzado

Una suite completa de herramientas profesionales para procesamiento de audio con soporte para múltiples formatos y gestión avanzada de metadatos.

## 🚀 Nuevas Funcionalidades v2.0

### ✨ Características Principales

- **🔄 Conversión Multi-formato**: WAV ↔ MP3 ↔ FLAC con preservación de metadatos
- **🏷️ Editor de Metadatos Profesional**: Soporte completo ID3v2.4, Vorbis Comments, iTunes
- **🖼️ Gestión Avanzada de Carátulas**: Embedding, extracción, redimensionado automático
- **✂️ División Inteligente**: Segmentación precisa con preservación de calidad
- **📋 Plantillas de Metadatos**: Sistema de plantillas guardables y reutilizables
- **🎛️ Interfaz Unificada**: Menú principal con acceso a todos los módulos

### 🎯 Casos de Uso

- **Productores Musicales**: Conversión de masters, segmentación de tracks
- **Podcasters**: División de episodios, gestión de metadatos
- **Archivistas**: Digitalización y catalogación de colecciones
- **DJs**: Preparación de sets, gestión de bibliotecas
- **Desarrolladores**: Integración en workflows automatizados

## 📦 Instalación Rápida

```bash
# Clonar o descargar el repositorio
git clone [URL-del-repositorio]
cd Audio-Splitter

# Ejecutar instalación automática
chmod +x install_advanced.sh
./install_advanced.sh

# Activar entorno virtual
source venv/bin/activate

# Iniciar el sistema
python3 main.py
```

## 🎵 Módulos del Sistema

### 1. 🔄 Audio Converter

Conversión entre formatos con preservación total de metadatos.

**Formatos Soportados:**
- **Entrada**: WAV, MP3, FLAC, M4A, OGG
- **Salida**: WAV, MP3, FLAC

**Configuraciones de Calidad:**

```bash
# MP3
- Bitrate fijo: 128k, 192k, 320k
- VBR: Calidad variable alta/media

# FLAC  
- Compresión: 0 (rápida) a 8 (máxima)

# WAV
- Sin pérdida, frecuencia original
```

**Uso:**

```bash
# Modo interactivo
python3 audio_converter.py

# Línea de comandos - archivo individual
python3 audio_converter.py --input song.wav --output song.mp3 --format mp3 --quality high

# Conversión por lotes
python3 audio_converter.py --dir ./music --output-dir ./converted --format flac --recursive
```

### 2. ✂️ Audio Splitter Avanzado

División inteligente con preservación de metadatos y soporte multi-formato.

**Características:**
- ⏱️ Precisión de milisegundos
- 🏷️ Preservación automática de metadatos
- 📊 Barra de progreso y estadísticas
- 🔄 Conversión durante división

**Formatos de Tiempo Soportados:**
```
MM:SS          → 1:30 (1 minuto, 30 segundos)
MM:SS.ms       → 1:30.500 (con milisegundos)
HH:MM:SS       → 1:30:45 (con horas)
Segundos       → 90.5 (decimales)
```

**Uso:**

```bash
# Modo interactivo con información detallada
python3 audio_splitter.py

# Línea de comandos
python3 audio_splitter.py --input podcast.mp3 --format flac \
  --segments "0:00-5:00:intro" "5:00-45:00:main" "45:00-50:00:outro"

# Solo información del archivo
python3 audio_splitter.py --input file.wav --info
```

### 3. 🏷️ Metadata Editor Profesional

Editor completo con soporte para todos los estándares de metadatos.

**Estándares Soportados:**
- **ID3v2.4** (MP3): Todas las tags incluyendo artwork
- **Vorbis Comments** (FLAC): Metadatos nativos
- **iTunes Tags** (M4A): Compatibilidad completa

**Campos Soportados:**
```
🎵 Básicos: Título, Artista, Álbum, Género
📅 Fechas: Año, fecha completa
🔢 Numeración: Track, disco (con totales)
👥 Créditos: Compositor, director, intérprete
📝 Adicionales: Comentarios, copyright, BPM
🏷️ Identificadores: ISRC, código de barras, catálogo
🖼️ Artwork: Carátulas embebidas
```

**Funciones Avanzadas:**
- 📋 **Plantillas**: Guardar y aplicar conjuntos de metadatos (en desarrollo)
- 🖼️ **Carátulas**: Agregar/cambiar artwork durante edición individual

**Uso:**

```bash
# Modo interactivo completo
python3 metadata_editor.py

# Edición con plantilla
python3 metadata_editor.py --dir ./album --template "rock_album"

# Campos específicos
python3 metadata_editor.py --file song.mp3 --field "album=Mi Álbum" --field "year=2024"

# Agregar carátula
python3 metadata_editor.py --file song.mp3 --artwork cover.jpg
```

## 🎛️ Menú Principal Unificado

El sistema incluye un menú principal que integra todos los módulos:

```bash
python3 main.py
```

```
🎵 Audio Splitter Suite Avanzado
═══════════════════════════════

🎛️ Módulos disponibles:
  1. 🔄 Audio Converter - Conversión entre formatos
  2. ✂️  Audio Splitter - División en segmentos
  3. 🏷️  Metadata Editor - Editor profesional (incluye carátulas)
  4. 📄 Documentación y ayuda
  5. 🚪 Salir
```

## 📋 Workflows Típicos

### 🎙️ Procesamiento de Podcast

```bash
# 1. Convertir grabación original
python3 audio_converter.py --input raw_recording.wav --format mp3 --quality vbr_high

# 2. Dividir en episodios
python3 audio_splitter.py --input podcast_session.mp3 \
  --segments "0:00-45:00:episode1" "47:00-90:00:episode2"

# 3. Agregar metadatos y carátula
python3 metadata_editor.py --file episode1.mp3 \
  --field "title=Episodio 1: Introducción" \
  --field "artist=Mi Podcast" \
  --artwork podcast_cover.jpg
```

### 🎵 Masterización de Álbum

```bash
# 1. Convertir masters a FLAC para archivo
python3 audio_converter.py --dir ./masters --format flac --quality high

# 2. Aplicar metadatos con plantilla
python3 metadata_editor.py --dir ./album --template "new_album_2024"

# 3. Crear versiones MP3 para distribución
python3 audio_converter.py --dir ./album --format mp3 --quality 320k
```

### 📀 Digitalización de Vinilo

```bash
# 1. Dividir grabación completa del lado A
python3 audio_splitter.py --input side_a.wav \
  --segments "0:00-3:30:track1" "3:35-7:20:track2" "7:25-11:40:track3"

# 2. Aplicar metadatos de álbum vintage
python3 metadata_editor.py --dir ./tracks --template "vinyl_1975"

# 3. Crear archivo FLAC y distribución MP3
python3 audio_converter.py --dir ./tracks --format flac  # Archivo
python3 audio_converter.py --dir ./tracks --format mp3   # Distribución
```

## ⚙️ Configuración Avanzada

### 📁 Estructura de Directorios

```
Audio-Splitter/
├── 🎵 main.py                    # Menú principal
├── 🔄 audio_converter.py         # Conversión de formatos  
├── ✂️  audio_splitter.py          # División de audio
├── 🏷️  metadata_editor.py        # Editor de metadatos
├── 📦 requirements.txt           # Dependencias
├── 🔧 install_advanced.sh       # Instalación automática
├── 📋 PRD_Audio_Splitter.md     # Especificaciones
├── 🏗️  Arquitectura_Audio_Splitter.md  # Documentación técnica
├── 📂 metadata_templates/        # Plantillas guardadas
├── 📂 output/                   # Archivos procesados
├── 📂 sources/                  # Archivos fuente
└── 📂 venv/                     # Entorno virtual
```

### 🔧 Configuración de Calidad

```python
# Configuración en audio_converter.py
QUALITY_PRESETS = {
    'mp3': {
        'low': {'bitrate': '128k'},      # Streaming básico
        'medium': {'bitrate': '192k'},   # Calidad estándar
        'high': {'bitrate': '320k'},     # Máxima calidad MP3
        'vbr_high': {'quality': 0}       # Variable bitrate premium
    },
    'flac': {
        'low': {'compression': 0},       # Rápido, archivos grandes
        'medium': {'compression': 5},    # Balanceado
        'high': {'compression': 8}       # Máxima compresión
    }
}
```

### 📋 Plantillas de Metadatos

Las plantillas se guardan en `metadata_templates/` como archivos JSON:

```json
{
  "album": "Mi Álbum 2024",
  "albumartist": "Nombre del Artista", 
  "date": "2024",
  "genre": "Rock Alternativo",
  "label": "Mi Sello Discográfico",
  "composer": "Compositor Principal"
}
```

## 🛠️ Dependencias y Requisitos

### 📋 Requisitos del Sistema

- **Python**: 3.6 o superior
- **Memoria**: 512MB RAM mínimo (recomendado 2GB)
- **Espacio**: 100MB + espacio para archivos procesados
- **SO**: Windows, macOS, Linux

### 📦 Bibliotecas Principales

```txt
# Procesamiento de audio
librosa>=0.10.0          # Análisis y carga de audio
soundfile>=0.12.0        # Lectura/escritura eficiente
pydub>=0.25.0            # Manipulación y conversión
numpy>=1.21.0            # Operaciones matemáticas

# Metadatos
mutagen>=1.47.0          # Biblioteca universal de metadatos
eyed3>=0.9.7             # Metadatos ID3 avanzados

# Interfaz y utilidades
rich>=13.0.0             # Terminal UI moderna
click>=8.1.0             # Framework CLI avanzado
Pillow>=10.0.0           # Procesamiento de imágenes
```

## 🐛 Solución de Problemas

### ❗ Errores Comunes

**Error de dependencias de audio:**
```bash
# En Ubuntu/Debian
sudo apt-get install libsndfile1 ffmpeg

# En macOS
brew install libsndfile ffmpeg

# En Windows
# Usar conda: conda install -c conda-forge librosa
```

**Error de permisos:**
```bash
chmod +x *.py
chmod +x install_advanced.sh
```

**Problemas de memoria con archivos grandes:**
```bash
# Usar procesamiento por chunks para archivos >2GB
python3 audio_splitter.py --input large_file.wav --chunk-size 100MB
```

### 🔍 Diagnóstico

```bash
# Verificar instalación
python3 -c "
import librosa, soundfile, mutagen, rich
from PIL import Image
print('✅ Todas las dependencias OK')
"

# Ver información del sistema
python3 main.py --version

# Logs detallados
python3 audio_splitter.py --input test.wav --info --verbose
```

## 📚 Documentación Técnica

### 📖 Documentos Disponibles

1. **README.md** - Esta guía de usuario
2. **PRD_Audio_Splitter.md** - Product Requirements Document completo
3. **Arquitectura_Audio_Splitter.md** - Documentación de arquitectura de software

### 📊 API y Extensibilidad

```python
# Ejemplo de uso programático
from audio_converter import AudioConverter
from metadata_editor import MetadataEditor

# Convertir archivo
converter = AudioConverter()
converter.convert_file(
    'input.wav', 
    'output.mp3', 
    target_format='mp3',
    quality='high',
    preserve_metadata=True
)

# Editar metadatos
editor = MetadataEditor()
metadata = editor.read_metadata('song.mp3')
metadata.title = "Nuevo Título"
metadata.album = "Nuevo Álbum"
editor.write_metadata('song.mp3', metadata)
```

## 🎆 Roadmap Futuro

### 🛣️ Versiones Planificadas

**v2.1 - Q3 2025**
- 🎧 Efectos de audio: fade-in/fade-out, normalize
- 📊 Análisis de espectro y visualizaciones
- 🚀 Procesamiento paralelo para lotes grandes

**v2.2 - Q4 2025**
- 📱 Interfaz gráfica (GUI) con Qt/Tkinter
- ☁️ Integración con servicios cloud (Google Drive, Dropbox)
- 📊 Dashboard web para monitoreo

**v3.0 - 2026**
- 🤖 IA para detección automática de segmentos
- 🎤 Transcripción automática de audio
- 📋 API REST completa

### 💬 Contribuciones

Las contribuciones son bienvenidas:

1. **Fork** el repositorio
2. **Crea** una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. **Commit** tus cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. **Push** a la rama (`git push origin feature/nueva-funcionalidad`)
5. **Crea** un Pull Request

### 🔍 Issues y Soporte

- **🐛 Reportar bugs**: [GitHub Issues]
- **✨ Solicitar features**: [Feature Requests]
- **❓ Preguntas**: [Discussions]
- **📚 Wiki**: [Documentación extendida]

## 📜 Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo LICENSE para detalles.

## 🙏 Reconocimientos

- **librosa** - Biblioteca fundamental de análisis de audio
- **mutagen** - Manejo universal de metadatos
- **rich** - Terminal UI moderna
- **pydub** - Manipulación de audio simplificada

---

**🎉 ¡Disfruta procesando audio con Audio Splitter Suite!**

*Para soporte técnico y actualizaciones, visita la documentación completa en los archivos PRD y Arquitectura incluidos.*
