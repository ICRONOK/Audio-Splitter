#!/usr/bin/env python3
"""
Professional Music Mastering Workflow
Workflow automatizado para mastering de música profesional

Pipeline:
1. Channel Conversion - Conversión mono ↔ stereo (opcional)
2. Convert to FLAC - Formato lossless de alta calidad
3. Validate Quality - Validación científica (THD+N, SNR)
4. Convert to MP3 - Versión comprimida para distribución
5. Add Metadata - Información del track
6. Generate Spectrogram - Análisis visual de frecuencias
"""

import sys
from pathlib import Path
from typing import Optional, Dict, Any

# Imports relativos con fallback
try:
    from ..workflow_engine import WorkflowEngine, create_workflow, WorkflowStep, WorkflowContext
    from ..workflow_steps import (
        ConvertAudioStep,
        AddMetadataStep,
        GenerateSpectrogramStep,
        ValidateQualityStep
    )
    from ..converter import AudioConverter
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from audio_splitter.core.workflow_engine import WorkflowEngine, create_workflow, WorkflowStep, WorkflowContext
    from audio_splitter.core.workflow_steps import (
        ConvertAudioStep,
        AddMetadataStep,
        GenerateSpectrogramStep,
        ValidateQualityStep
    )
    from audio_splitter.core.converter import AudioConverter

from rich.console import Console
console = Console()


class ChannelConversionStep(WorkflowStep):
    """
    Step para conversión de canales (mono ↔ stereo)
    """

    def __init__(self,
                 target_channels: int,
                 mixing_algorithm: str = "downmix_center",
                 preserve_metadata: bool = True,
                 name: Optional[str] = None):
        channel_name = "mono" if target_channels == 1 else "stereo"
        name = name or f"Convert to {channel_name.capitalize()}"
        super().__init__(
            name=name,
            description=f"Convertir audio a {channel_name}",
            required=False  # Opcional
        )
        self.target_channels = target_channels
        self.mixing_algorithm = mixing_algorithm
        self.preserve_metadata = preserve_metadata
        self.converter = AudioConverter()

    def validate_preconditions(self, context: WorkflowContext) -> bool:
        """Validar que existe archivo de entrada"""
        if not context.input_file:
            return False
        return Path(context.input_file).exists()

    def execute(self, context: WorkflowContext) -> Dict[str, Any]:
        """Ejecutar conversión de canales"""
        input_file = context.input_file
        output_dir = Path(context.output_dir or ".")
        output_dir.mkdir(parents=True, exist_ok=True)

        # Generar nombre de archivo de salida
        input_path = Path(input_file)
        channel_suffix = "mono" if self.target_channels == 1 else "stereo"
        output_file = output_dir / f"{input_path.stem}_{channel_suffix}{input_path.suffix}"

        console.print(f"[cyan]Converting channels to {channel_suffix}...[/cyan]")

        # Ejecutar conversión usando AudioConverter
        success = self.converter.convert_channels(
            input_path=str(input_file),
            output_path=str(output_file),
            target_channels=self.target_channels,
            mixing_algorithm=self.mixing_algorithm if self.target_channels == 1 else "downmix_center",
            preserve_metadata=self.preserve_metadata
        )

        if success:
            # Registrar archivo generado y actualizar input para siguientes steps
            context.add_intermediate_file('channel_converted', str(output_file))
            # IMPORTANTE: Actualizar input_file para que siguientes steps usen el archivo convertido
            context.input_file = str(output_file)
            console.print(f"[green]✓ Channel conversion successful: {output_file}[/green]")

            return {
                'output_file': str(output_file),
                'target_channels': self.target_channels,
                'algorithm': self.mixing_algorithm
            }
        else:
            from ..workflow_engine import WorkflowError
            raise WorkflowError(f"Channel conversion failed")

    def validate_postconditions(self, context: WorkflowContext) -> bool:
        """Validar que el archivo convertido existe"""
        output_file = context.get_intermediate_file('channel_converted')
        return output_file and Path(output_file).exists()


def create_music_mastering_workflow(
    input_file: str,
    output_dir: str,
    metadata: Optional[Dict[str, str]] = None,
    quality_profile: str = "professional",
    channel_conversion: Optional[str] = None,  # "mono", "stereo", o None
    mixing_algorithm: str = "downmix_center",
    include_flac: bool = True,
    include_mp3: bool = True,
    generate_analysis: bool = True
) -> WorkflowEngine:
    """
    Crear workflow de mastering de música profesional

    Args:
        input_file: Archivo de audio master
        output_dir: Directorio para archivos procesados
        metadata: Metadatos del track (title, artist, album, etc.)
        quality_profile: Perfil de calidad (professional, studio)
        channel_conversion: Conversión de canales ("mono", "stereo", o None para mantener original)
        mixing_algorithm: Algoritmo para downmix stereo→mono (downmix_center, left_only, right_only, average)
        include_flac: Si incluir versión FLAC lossless
        include_mp3: Si incluir versión MP3 para distribución
        generate_analysis: Si generar espectrogramas de análisis

    Returns:
        WorkflowEngine configurado con pipeline de mastering
    """

    # Metadatos por defecto
    if metadata is None:
        metadata = {
            'title': 'Untitled Track',
            'artist': 'Unknown Artist',
            'album': 'Single',
            'date': '2025',
            'genre': 'Music'
        }

    # Crear workflow
    workflow = create_workflow(
        name="Professional Music Mastering",
        description="Pipeline automatizado para mastering profesional de música"
    )

    # Configurar contexto
    workflow.configure(
        input_file=input_file,
        output_dir=output_dir,
        workflow_type="music_mastering",
        quality_profile=quality_profile
    )

    # Step 0: Channel Conversion (OPCIONAL - Si se especifica)
    if channel_conversion:
        target_channels = 1 if channel_conversion.lower() == "mono" else 2
        workflow.add_step(
            ChannelConversionStep(
                target_channels=target_channels,
                mixing_algorithm=mixing_algorithm,
                preserve_metadata=True,
                name=f"Convert to {channel_conversion.capitalize()}"
            )
        )

    # Step 1: Convert to FLAC (formato lossless master)
    if include_flac:
        workflow.add_step(
            ConvertAudioStep(
                output_format="flac",
                quality_level="high",  # Compression level 8 (máxima calidad)
                quality_validation=True,  # Siempre validar FLAC master
                name="Convert to FLAC Master"
            )
        )

        # Validate FLAC master quality
        workflow.add_step(
            ValidateQualityStep(
                name="Validate FLAC Master Quality"
            )
        )

    # Step 2: Convert to MP3 (distribución)
    if include_mp3:
        workflow.add_step(
            ConvertAudioStep(
                output_format="mp3",
                quality_level="high",  # VBR high o 320kbps
                quality_validation=True,
                name="Convert to MP3 Distribution"
            )
        )

    # Step 3: Add Metadata
    workflow.add_step(
        AddMetadataStep(
            metadata=metadata,
            target="converted",
            name="Add Track Metadata"
        )
    )

    # Step 4: Generate Spectrograms para análisis
    if generate_analysis:
        # Mel spectrogram para análisis general
        workflow.add_step(
            GenerateSpectrogramStep(
                spectrogram_type="mel",
                enhanced=True,
                name="Generate Mel Spectrogram"
            )
        )

        # CQT spectrogram para análisis musical detallado (opcional)
        workflow.add_step(
            GenerateSpectrogramStep(
                spectrogram_type="cqt",
                enhanced=True,
                name="Generate CQT Musical Analysis"
            )
        )

    # Step 5: Final Quality Validation
    workflow.add_step(
        ValidateQualityStep(
            name="Final Master Quality Validation"
        )
    )

    return workflow


def create_quick_music_workflow(
    input_file: str,
    output_dir: str,
    track_title: str,
    artist_name: str,
    album_name: str,
    to_mono: bool = False
) -> WorkflowEngine:
    """
    Versión rápida del workflow de mastering

    Args:
        input_file: Archivo de audio
        output_dir: Directorio de salida
        track_title: Título del track
        artist_name: Nombre del artista
        album_name: Nombre del álbum
        to_mono: Si convertir a mono para distribución específica

    Returns:
        WorkflowEngine configurado
    """

    metadata = {
        'title': track_title,
        'artist': artist_name,
        'album': album_name,
        'comment': 'Mastered with Audio Splitter Suite'
    }

    return create_music_mastering_workflow(
        input_file=input_file,
        output_dir=output_dir,
        metadata=metadata,
        quality_profile="professional",
        channel_conversion="mono" if to_mono else None,
        include_flac=False,  # Solo MP3 para workflow rápido
        include_mp3=True,
        generate_analysis=False
    )


def create_studio_mastering_workflow(
    input_file: str,
    output_dir: str,
    metadata: Dict[str, str],
    channel_mode: Optional[str] = None,
    isrc: Optional[str] = None
) -> WorkflowEngine:
    """
    Versión studio-grade del workflow con máxima calidad

    Args:
        input_file: Archivo de audio master
        output_dir: Directorio de salida
        metadata: Metadatos completos del track
        channel_mode: "mono", "stereo", o None (mantener original)
        isrc: International Standard Recording Code

    Returns:
        WorkflowEngine configurado con estándares de estudio
    """

    # Agregar ISRC si existe
    if isrc:
        metadata['isrc'] = isrc

    metadata['quality_profile'] = 'studio'
    metadata['mastered_by'] = 'Audio Splitter Suite - Studio Workflow'

    return create_music_mastering_workflow(
        input_file=input_file,
        output_dir=output_dir,
        metadata=metadata,
        quality_profile="studio",
        channel_conversion=channel_mode,
        mixing_algorithm="downmix_center",  # Algoritmo profesional por defecto
        include_flac=True,   # FLAC master obligatorio
        include_mp3=True,    # MP3 para distribución
        generate_analysis=True  # Análisis completo
    )


def create_mono_mastering_workflow(
    input_file: str,
    output_dir: str,
    metadata: Dict[str, str],
    mixing_algorithm: str = "downmix_center"
) -> WorkflowEngine:
    """
    Workflow específico para mastering mono (podcasts, radio, audiobooks)

    Args:
        input_file: Archivo de audio
        output_dir: Directorio de salida
        metadata: Metadatos del track
        mixing_algorithm: Algoritmo de downmix (downmix_center, left_only, right_only, average)

    Returns:
        WorkflowEngine configurado para mono
    """

    # Agregar información de canales al comentario
    if 'comment' in metadata:
        metadata['comment'] = f"{metadata['comment']} | Channels: 1 (Mono) | Type: Mono Master"
    else:
        metadata['comment'] = 'Channels: 1 (Mono) | Type: Mono Master'

    return create_music_mastering_workflow(
        input_file=input_file,
        output_dir=output_dir,
        metadata=metadata,
        quality_profile="professional",
        channel_conversion="mono",
        mixing_algorithm=mixing_algorithm,
        include_flac=True,
        include_mp3=True,
        generate_analysis=True
    )


def create_stereo_upmix_workflow(
    input_file: str,
    output_dir: str,
    metadata: Dict[str, str]
) -> WorkflowEngine:
    """
    Workflow para convertir mono a stereo

    Args:
        input_file: Archivo de audio mono
        output_dir: Directorio de salida
        metadata: Metadatos del track

    Returns:
        WorkflowEngine configurado para upmix stereo
    """

    # Agregar información de canales al comentario
    if 'comment' in metadata:
        metadata['comment'] = f"{metadata['comment']} | Channels: 2 (Stereo) | Type: Stereo Upmix"
    else:
        metadata['comment'] = 'Channels: 2 (Stereo) | Type: Stereo Upmix'

    return create_music_mastering_workflow(
        input_file=input_file,
        output_dir=output_dir,
        metadata=metadata,
        quality_profile="professional",
        channel_conversion="stereo",
        include_flac=True,
        include_mp3=True,
        generate_analysis=True
    )


# Templates y configuraciones predefinidas
MASTERING_TEMPLATES = {
    'single_release': {
        'include_flac': True,
        'include_mp3': True,
        'channel_conversion': None,
        'generate_analysis': True,
        'quality_profile': 'professional',
        'description': 'Master para single release (mantiene canales originales)'
    },
    'streaming_optimized': {
        'include_flac': False,
        'include_mp3': True,
        'channel_conversion': None,
        'generate_analysis': False,
        'quality_profile': 'professional',
        'description': 'Optimizado para plataformas streaming'
    },
    'vinyl_master': {
        'include_flac': True,
        'include_mp3': False,
        'channel_conversion': 'stereo',
        'generate_analysis': True,
        'quality_profile': 'studio',
        'description': 'Master para producción de vinilo (stereo obligatorio)'
    },
    'digital_distribution': {
        'include_flac': True,
        'include_mp3': True,
        'channel_conversion': None,
        'generate_analysis': True,
        'quality_profile': 'professional',
        'description': 'Master para distribución digital (iTunes, Spotify, etc.)'
    },
    'mono_radio': {
        'include_flac': False,
        'include_mp3': True,
        'channel_conversion': 'mono',
        'generate_analysis': False,
        'quality_profile': 'professional',
        'description': 'Master mono para radio y broadcast'
    },
    'audiobook': {
        'include_flac': False,
        'include_mp3': True,
        'channel_conversion': 'mono',
        'generate_analysis': False,
        'quality_profile': 'professional',
        'description': 'Master mono para audiobooks'
    }
}


def get_mastering_template(template_name: str) -> Dict[str, Any]:
    """
    Obtener template predefinido de mastering

    Args:
        template_name: Nombre del template

    Returns:
        Dict con configuración del template
    """
    return MASTERING_TEMPLATES.get(template_name, MASTERING_TEMPLATES['single_release'])


if __name__ == "__main__":
    console.print("[cyan]Music Mastering Workflow Module Loaded[/cyan]")
    console.print(f"Available templates: {list(MASTERING_TEMPLATES.keys())}")
    console.print("✅ Professional Music Mastering workflow ready")
    console.print("✅ Channel conversion (mono ↔ stereo) integrated")
