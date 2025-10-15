#!/usr/bin/env python3
"""
Complete Podcast Production Workflow
Workflow automatizado para producción de podcasts profesionales

Pipeline:
1. Split Audio - Dividir en segmentos (intro, main, outro)
2. Add Metadata - Agregar información del episodio
3. Convert to MP3 - Convertir a formato distribución
4. Generate Spectrogram - Crear visualización para análisis
"""

import sys
from pathlib import Path
from typing import Optional, Dict, Any, List

# Imports relativos con fallback
try:
    from ..workflow_engine import WorkflowEngine, create_workflow
    from ..workflow_steps import (
        SplitAudioStep,
        AddMetadataStep,
        ConvertAudioStep,
        GenerateSpectrogramStep,
        ValidateQualityStep
    )
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from audio_splitter.core.workflow_engine import WorkflowEngine, create_workflow
    from audio_splitter.core.workflow_steps import (
        SplitAudioStep,
        AddMetadataStep,
        ConvertAudioStep,
        GenerateSpectrogramStep,
        ValidateQualityStep
    )


def create_podcast_workflow(
    input_file: str,
    output_dir: str,
    segments: Optional[List[str]] = None,
    metadata: Optional[Dict[str, str]] = None,
    generate_spectrogram: bool = True,
    quality_validation: bool = False
) -> WorkflowEngine:
    """
    Crear workflow de producción de podcast completo

    Args:
        input_file: Archivo de audio raw del podcast
        output_dir: Directorio para archivos procesados
        segments: Lista de segmentos a crear (ej: ["0:00-0:30:intro", "0:30-30:00:main"])
        metadata: Metadatos del episodio (title, artist, album, etc.)
        generate_spectrogram: Si generar espectrograma para análisis
        quality_validation: Si validar calidad en cada paso

    Returns:
        WorkflowEngine configurado con pipeline de podcast
    """

    # Configuración por defecto de segmentos si no se proveen
    if segments is None:
        segments = [
            "0:00-0:30:intro",      # 30 segundos de intro
            "0:30-29:30:main",      # Contenido principal
            "29:30-30:00:outro"     # 30 segundos de outro
        ]

    # Metadatos por defecto
    if metadata is None:
        metadata = {
            'title': 'Podcast Episode',
            'artist': 'Podcast Host',
            'album': 'Podcast Series',
            'genre': 'Podcast'
        }

    # Crear workflow
    workflow = create_workflow(
        name="Complete Podcast Production",
        description="Pipeline automatizado para producción profesional de podcasts"
    )

    # Configurar contexto
    workflow.configure(
        input_file=input_file,
        output_dir=output_dir,
        workflow_type="podcast"
    )

    # Step 1: Split Audio en segmentos
    workflow.add_step(
        SplitAudioStep(
            segments=segments,
            enhanced=True,
            quality_validation=quality_validation,
            name="Split Podcast Segments"
        )
    )

    # Step 2: Add Metadata a segmentos
    workflow.add_step(
        AddMetadataStep(
            metadata=metadata,
            target="segments",
            name="Add Podcast Metadata"
        )
    )

    # Step 3: Convert to MP3 (formato estándar para podcasts)
    workflow.add_step(
        ConvertAudioStep(
            output_format="mp3",
            quality_level="high",  # 192kbps+ para calidad broadcast
            quality_validation=quality_validation,
            name="Convert to MP3 Distribution"
        )
    )

    # Step 4: Generate Spectrogram (opcional, para análisis)
    if generate_spectrogram:
        workflow.add_step(
            GenerateSpectrogramStep(
                spectrogram_type="mel",
                enhanced=True,
                name="Generate Podcast Spectrogram"
            )
        )

    # Step 5: Validate Quality (opcional)
    if quality_validation:
        workflow.add_step(
            ValidateQualityStep(
                name="Validate Podcast Quality"
            )
        )

    return workflow


def create_quick_podcast_workflow(
    input_file: str,
    output_dir: str,
    episode_title: str,
    host_name: str,
    series_name: str
) -> WorkflowEngine:
    """
    Versión rápida del workflow de podcast con configuración simplificada

    Args:
        input_file: Archivo de audio del podcast
        output_dir: Directorio de salida
        episode_title: Título del episodio
        host_name: Nombre del host
        series_name: Nombre de la serie

    Returns:
        WorkflowEngine configurado
    """

    metadata = {
        'title': episode_title,
        'artist': host_name,
        'album': series_name,
        'genre': 'Podcast',
        'comment': f'Processed with Audio Splitter Suite - Podcast Workflow'
    }

    return create_podcast_workflow(
        input_file=input_file,
        output_dir=output_dir,
        segments=None,  # Usar segmentos por defecto
        metadata=metadata,
        generate_spectrogram=False,  # Más rápido sin spectrogram
        quality_validation=False
    )


def create_advanced_podcast_workflow(
    input_file: str,
    output_dir: str,
    segments: List[str],
    metadata: Dict[str, str],
    quality_profile: str = "professional"
) -> WorkflowEngine:
    """
    Versión avanzada del workflow con todas las validaciones

    Args:
        input_file: Archivo de audio del podcast
        output_dir: Directorio de salida
        segments: Segmentos personalizados
        metadata: Metadatos completos
        quality_profile: Perfil de calidad (professional, studio)

    Returns:
        WorkflowEngine configurado con validación completa
    """

    # Agregar información del quality profile a metadata
    metadata['quality_profile'] = quality_profile

    return create_podcast_workflow(
        input_file=input_file,
        output_dir=output_dir,
        segments=segments,
        metadata=metadata,
        generate_spectrogram=True,  # Incluir análisis visual
        quality_validation=True     # Validación científica activada
    )


# Ejemplos de uso y templates
PODCAST_TEMPLATES = {
    'short_episode': {
        'segments': [
            "0:00-0:15:intro",
            "0:15-14:45:content",
            "14:45-15:00:outro"
        ],
        'duration': '15 minutes'
    },
    'standard_episode': {
        'segments': [
            "0:00-0:30:intro",
            "0:30-29:30:content",
            "29:30-30:00:outro"
        ],
        'duration': '30 minutes'
    },
    'long_episode': {
        'segments': [
            "0:00-1:00:intro",
            "1:00-58:00:content",
            "58:00-60:00:outro"
        ],
        'duration': '60 minutes'
    },
    'interview_format': {
        'segments': [
            "0:00-0:30:intro",
            "0:30-2:00:guest_intro",
            "2:00-27:00:interview",
            "27:00-29:30:q_and_a",
            "29:30-30:00:outro"
        ],
        'duration': '30 minutes'
    }
}


def get_podcast_template(template_name: str) -> Dict[str, Any]:
    """
    Obtener template predefinido de podcast

    Args:
        template_name: Nombre del template (short_episode, standard_episode, etc.)

    Returns:
        Dict con configuración del template
    """
    return PODCAST_TEMPLATES.get(template_name, PODCAST_TEMPLATES['standard_episode'])


if __name__ == "__main__":
    from rich.console import Console
    console = Console()

    console.print("[cyan]Podcast Workflow Module Loaded[/cyan]")
    console.print(f"Available templates: {list(PODCAST_TEMPLATES.keys())}")
    console.print("✅ Complete Podcast Production workflow ready")
