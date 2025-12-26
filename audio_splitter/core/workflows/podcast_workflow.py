#!/usr/bin/env python3
"""
Professional Podcast Production Workflow
Post-production workflow for podcast distribution

Real-world pipeline:
1. Validate Input Quality - Check for technical issues
2. Convert to MP3 192kbps - Optimized for streaming platforms
3. Add Podcast Metadata - Episode info, host, series
4. Generate Waveform Visual - Optional marketing asset
"""

import sys
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

# Imports relativos con fallback
try:
    from ..workflow_engine import WorkflowEngine, create_workflow
    from ..workflow_steps import (
        AddMetadataStep,
        ConvertAudioStep,
        GenerateSpectrogramStep,
        ValidateQualityStep
    )
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from audio_splitter.core.workflow_engine import WorkflowEngine, create_workflow
    from audio_splitter.core.workflow_steps import (
        AddMetadataStep,
        ConvertAudioStep,
        GenerateSpectrogramStep,
        ValidateQualityStep
    )


def create_podcast_workflow(
    input_file: str,
    output_dir: str,
    metadata: Optional[Dict[str, str]] = None,
    quality_validation: bool = True,
    generate_visual: bool = False
) -> WorkflowEngine:
    """
    Professional podcast post-production workflow

    Converts edited podcast audio to distribution-ready MP3 with metadata

    Args:
        input_file: Edited podcast audio file (WAV, FLAC, etc.)
        output_dir: Output directory for processed files
        metadata: Podcast metadata (title, host, series, description)
        quality_validation: Enable pre-production quality checks
        generate_visual: Generate waveform visual for marketing

    Returns:
        WorkflowEngine configured with podcast production pipeline

    Pipeline:
        1. Validate Input Quality (optional) - Detect clipping, DC offset, etc.
        2. Convert to MP3 192kbps CBR - Streaming-optimized format
        3. Add Podcast Metadata - Complete episode information
        4. Generate Waveform (optional) - Marketing/thumbnail asset
    """

    # Default metadata
    if metadata is None:
        metadata = {
            'title': 'Podcast Episode',
            'artist': 'Host Name',
            'album': 'Podcast Series',
            'genre': 'Podcast',
            'date': str(datetime.now().year),
            'comment': 'Processed with Audio Splitter Suite'
        }

    # Create workflow
    workflow = create_workflow(
        name="Podcast Production",
        description="Professional podcast post-production and distribution prep"
    )

    # Configure context
    workflow.configure(
        input_file=input_file,
        output_dir=output_dir,
        workflow_type="podcast"
    )

    # Step 1: Pre-Production Quality Check (optional)
    if quality_validation:
        workflow.add_step(
            ValidateQualityStep(
                name="Pre-Production Quality Check",
                strict=False  # Warning only, don't reject
            )
        )

    # Step 2: Convert to MP3 192kbps CBR
    workflow.add_step(
        ConvertAudioStep(
            output_format="mp3",
            bitrate="192k",
            quality_level="high",
            quality_validation=quality_validation,
            name="Convert to MP3 Distribution Format"
        )
    )

    # Step 3: Add Podcast Metadata
    workflow.add_step(
        AddMetadataStep(
            metadata=metadata,
            target="converted",
            name="Add Podcast Metadata"
        )
    )

    # Step 4: Generate Waveform Visual (optional)
    if generate_visual:
        workflow.add_step(
            GenerateSpectrogramStep(
                spectrogram_type="linear",
                enhanced=False,
                name="Generate Waveform Visual"
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
    Quick podcast workflow - minimal configuration

    Fast conversion with basic metadata, no quality checks

    Args:
        input_file: Audio file to process
        output_dir: Output directory
        episode_title: Episode title
        host_name: Host name(s)
        series_name: Podcast series name

    Returns:
        WorkflowEngine with quick processing pipeline
    """

    metadata = {
        'title': episode_title,
        'artist': host_name,
        'album': series_name,
        'genre': 'Podcast',
        'date': str(datetime.now().year),
        'comment': f'Episode: {episode_title}'
    }

    return create_podcast_workflow(
        input_file=input_file,
        output_dir=output_dir,
        metadata=metadata,
        quality_validation=False,
        generate_visual=False
    )


def create_professional_podcast_workflow(
    input_file: str,
    output_dir: str,
    episode_title: str,
    episode_number: int,
    season_number: Optional[int],
    host_name: str,
    series_name: str,
    description: str,
    publication_date: Optional[str] = None
) -> WorkflowEngine:
    """
    Professional podcast workflow with complete metadata

    Full quality validation and complete episode information

    Args:
        input_file: Audio file to process
        output_dir: Output directory
        episode_title: Episode title
        episode_number: Episode number
        season_number: Season number (optional)
        host_name: Host name(s)
        series_name: Podcast series name
        description: Episode description/show notes
        publication_date: Publication date (YYYY-MM-DD)

    Returns:
        WorkflowEngine with professional pipeline
    """

    if publication_date is None:
        publication_date = datetime.now().strftime('%Y-%m-%d')

    # Build complete metadata
    metadata = {
        'title': episode_title,
        'artist': host_name,
        'album': series_name,
        'genre': 'Podcast',
        'date': publication_date[:4],
        'comment': f'{description}\n\nEpisode: {episode_number}'
    }

    if season_number:
        metadata['comment'] += f' | Season: {season_number}'

    metadata['comment'] += f'\nPublished: {publication_date}'

    return create_podcast_workflow(
        input_file=input_file,
        output_dir=output_dir,
        metadata=metadata,
        quality_validation=True,
        generate_visual=True
    )


# Workflow modes for UI
PODCAST_MODES = {
    'quick': {
        'name': 'Quick Production',
        'description': 'Fast conversion with basic metadata',
        'quality_validation': False,
        'generate_visual': False
    },
    'standard': {
        'name': 'Standard Production',
        'description': 'Quality checks with complete metadata',
        'quality_validation': True,
        'generate_visual': False
    },
    'professional': {
        'name': 'Professional Production',
        'description': 'Full validation with waveform visual',
        'quality_validation': True,
        'generate_visual': True
    }
}


def get_podcast_mode(mode_name: str) -> Dict[str, Any]:
    """
    Get podcast workflow mode configuration

    Args:
        mode_name: Mode name (quick, standard, professional)

    Returns:
        Mode configuration dict
    """
    return PODCAST_MODES.get(mode_name, PODCAST_MODES['standard'])


if __name__ == "__main__":
    from rich.console import Console
    console = Console()

    console.print("[cyan]Professional Podcast Production Workflow Loaded[/cyan]")
    console.print(f"Available modes: {list(PODCAST_MODES.keys())}")
    console.print("✅ Real-world podcast post-production pipeline ready")
