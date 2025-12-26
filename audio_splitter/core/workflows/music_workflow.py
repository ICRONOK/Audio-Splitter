#!/usr/bin/env python3
"""
Professional Music Mastering Workflow
Multi-format mastering for music distribution and archiving

Real-world pipeline:
1. Pre-Master Quality Analysis - Scientific validation
2. Archive Master (FLAC) - Lossless archival format
3. Distribution Master (MP3) - Streaming-optimized format
4. Add Music Metadata - Complete track information
5. Frequency Analysis - Dual spectrogram analysis
6. Post-Master Validation - Quality comparison
"""

import sys
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

# Imports relativos con fallback
try:
    from ..workflow_engine import WorkflowEngine, create_workflow
    from ..workflow_steps import (
        ConvertAudioStep,
        AddMetadataStep,
        GenerateSpectrogramStep,
        ValidateQualityStep,
        ChannelConversionStep
    )
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from audio_splitter.core.workflow_engine import WorkflowEngine, create_workflow
    from audio_splitter.core.workflow_steps import (
        ConvertAudioStep,
        AddMetadataStep,
        GenerateSpectrogramStep,
        ValidateQualityStep,
        ChannelConversionStep
    )


def create_music_mastering_workflow(
    input_file: str,
    output_dir: str,
    metadata: Optional[Dict[str, str]] = None,
    quality_profile: str = "professional",
    channel_conversion: Optional[str] = None,
    mixing_algorithm: str = "downmix_center",
    include_flac: bool = True,
    include_mp3: bool = True,
    generate_analysis: bool = True
) -> WorkflowEngine:
    """
    Professional music mastering workflow for distribution

    Creates multiple format masters with scientific quality validation

    Args:
        input_file: Final mix audio file (WAV, FLAC, etc.)
        output_dir: Output directory for master files
        metadata: Track metadata (title, artist, album, etc.)
        quality_profile: Quality profile (professional, studio)
        channel_conversion: Channel conversion ("mono", "stereo", None to keep original)
        mixing_algorithm: Algorithm for stereo→mono (downmix_center, left_only, right_only, average)
        include_flac: Generate FLAC lossless archive master
        include_mp3: Generate MP3 distribution master
        generate_analysis: Generate frequency analysis spectrograms

    Returns:
        WorkflowEngine configured with mastering pipeline

    Pipeline:
        1. Pre-Master Quality Analysis - THD+N, SNR, artifact detection
        1.5. [OPTIONAL] Channel Conversion - Mono ↔ Stereo
        2. Archive Master (FLAC) - Lossless with quality validation
        3. Distribution Master (MP3 320kbps) - Streaming-optimized
        4. Add Complete Metadata - Album, artist, ISRC, production credits
        5. Frequency Analysis - Dual spectrogram (mel + CQT)
        6. Post-Master Validation - Format comparison and quality check
    """

    # Default metadata
    if metadata is None:
        metadata = {
            'title': 'Untitled Track',
            'artist': 'Unknown Artist',
            'album': 'Single',
            'genre': 'Music',
            'date': str(datetime.now().year),
            'comment': 'Mastered with Audio Splitter Suite'
        }

    # Create workflow
    workflow = create_workflow(
        name="Music Mastering",
        description="Professional music mastering and distribution preparation"
    )

    # Configure context
    workflow.configure(
        input_file=input_file,
        output_dir=output_dir,
        workflow_type="music_mastering",
        quality_profile=quality_profile
    )

    # Step 1: Pre-Master Quality Analysis
    workflow.add_step(
        ValidateQualityStep(
            name="Pre-Master Quality Analysis",
            strict=True,
            profile=quality_profile
        )
    )

    # Step 1.5: Channel Conversion (OPTIONAL)
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

    # Step 2: Archive Master (FLAC Lossless)
    if include_flac:
        workflow.add_step(
            ConvertAudioStep(
                output_format="flac",
                bitrate=None,  # Lossless
                quality_level="lossless",
                quality_validation=True,
                name="Create Archive Master (FLAC)"
            )
        )

    # Step 3: Distribution Master (MP3 320kbps)
    if include_mp3:
        workflow.add_step(
            ConvertAudioStep(
                output_format="mp3",
                bitrate="320k",
                quality_level="high",
                quality_validation=True,
                name="Create Distribution Master (MP3 320kbps)"
            )
        )

    # Step 4: Add Music Metadata
    workflow.add_step(
        AddMetadataStep(
            metadata=metadata,
            target="all",  # Apply to all formats
            name="Add Music Metadata"
        )
    )

    # Step 5: Frequency Analysis (Mel + CQT Spectrograms)
    if generate_analysis:
        # Mel spectrogram for general frequency analysis
        workflow.add_step(
            GenerateSpectrogramStep(
                spectrogram_type="mel",
                enhanced=True,
                name="Generate Mel Spectrogram"
            )
        )
        # CQT spectrogram for musical analysis
        workflow.add_step(
            GenerateSpectrogramStep(
                spectrogram_type="cqt",
                enhanced=True,
                name="Generate CQT Spectrogram (Musical Analysis)"
            )
        )

    # Step 6: Post-Master Quality Validation
    workflow.add_step(
        ValidateQualityStep(
            name="Post-Master Quality Validation",
            strict=False,  # Warning only
            compare_formats=True  # Compare FLAC vs MP3
        )
    )

    return workflow


def create_quick_mastering_workflow(
    input_file: str,
    output_dir: str,
    track_title: str,
    artist_name: str,
    album_name: str
) -> WorkflowEngine:
    """
    Quick mastering workflow - MP3 only with basic metadata

    Fast conversion for demos, previews, or quick distribution

    Args:
        input_file: Audio file to master
        output_dir: Output directory
        track_title: Track title
        artist_name: Artist name
        album_name: Album name

    Returns:
        WorkflowEngine with quick mastering pipeline
    """

    metadata = {
        'title': track_title,
        'artist': artist_name,
        'album': album_name,
        'genre': 'Music',
        'date': str(datetime.now().year),
        'comment': 'Quick master'
    }

    return create_music_mastering_workflow(
        input_file=input_file,
        output_dir=output_dir,
        metadata=metadata,
        quality_profile="professional",
        include_flac=False,  # MP3 only for speed
        include_mp3=True,
        generate_analysis=False
    )


def create_professional_mastering_workflow(
    input_file: str,
    output_dir: str,
    track_title: str,
    artist_name: str,
    album_name: str,
    track_number: int,
    total_tracks: int,
    genre: str,
    channel_conversion: Optional[str] = None,
    mixing_algorithm: str = "downmix_center",
    isrc: Optional[str] = None,
    production_credits: Optional[str] = None
) -> WorkflowEngine:
    """
    Professional mastering workflow with complete metadata

    Full quality validation and complete production information

    Args:
        input_file: Audio file to master
        output_dir: Output directory
        track_title: Track title
        artist_name: Artist name
        album_name: Album name
        track_number: Track number in album
        total_tracks: Total tracks in album
        genre: Music genre
        channel_conversion: Channel conversion (None, "mono", "stereo")
        mixing_algorithm: Mixing algorithm for stereo→mono
        isrc: International Standard Recording Code
        production_credits: Producer, engineer, studio info

    Returns:
        WorkflowEngine with professional mastering pipeline
    """

    # Build complete metadata
    metadata = {
        'title': track_title,
        'artist': artist_name,
        'album': album_name,
        'genre': genre,
        'date': str(datetime.now().year),
        'track': f'{track_number}/{total_tracks}',
        'comment': f'Track {track_number} of {total_tracks}'
    }

    if isrc:
        metadata['comment'] += f'\nISRC: {isrc}'

    if production_credits:
        metadata['comment'] += f'\n{production_credits}'

    return create_music_mastering_workflow(
        input_file=input_file,
        output_dir=output_dir,
        metadata=metadata,
        quality_profile="studio",
        channel_conversion=channel_conversion,
        mixing_algorithm=mixing_algorithm,
        include_flac=True,
        include_mp3=True,
        generate_analysis=True
    )


def create_album_mastering_workflow(
    input_file: str,
    output_dir: str,
    metadata: Dict[str, str],
    quality_profile: str = "studio"
) -> WorkflowEngine:
    """
    Album mastering workflow - highest quality for album releases

    Complete validation and analysis for album production

    Args:
        input_file: Audio file to master
        output_dir: Output directory
        metadata: Complete track metadata
        quality_profile: Quality profile (studio recommended)

    Returns:
        WorkflowEngine with album mastering pipeline
    """

    # Ensure album metadata is complete
    if 'comment' not in metadata:
        metadata['comment'] = 'Album Master'

    metadata['comment'] = f"{metadata.get('comment', 'Album Master')}\nMastered for album release"

    return create_music_mastering_workflow(
        input_file=input_file,
        output_dir=output_dir,
        metadata=metadata,
        quality_profile=quality_profile,
        include_flac=True,  # Always include FLAC for albums
        include_mp3=True,
        generate_analysis=True  # Full frequency analysis
    )


def create_streaming_optimized_workflow(
    input_file: str,
    output_dir: str,
    metadata: Dict[str, str]
) -> WorkflowEngine:
    """
    Streaming-optimized workflow for Spotify, Apple Music, etc.

    MP3 320kbps with quality validation, no FLAC

    Args:
        input_file: Audio file to master
        output_dir: Output directory
        metadata: Track metadata

    Returns:
        WorkflowEngine with streaming-optimized pipeline
    """

    metadata['comment'] = f"{metadata.get('comment', 'Streaming Master')}\nOptimized for streaming platforms"

    return create_music_mastering_workflow(
        input_file=input_file,
        output_dir=output_dir,
        metadata=metadata,
        quality_profile="professional",
        include_flac=False,  # No FLAC for streaming only
        include_mp3=True,
        generate_analysis=False  # Speed over analysis
    )


def create_vinyl_preparation_workflow(
    input_file: str,
    output_dir: str,
    metadata: Dict[str, str]
) -> WorkflowEngine:
    """
    Vinyl preparation workflow for cutting master

    Stereo-only FLAC with strictest quality validation

    Args:
        input_file: Audio file to master
        output_dir: Output directory
        metadata: Track metadata

    Returns:
        WorkflowEngine with vinyl preparation pipeline
    """

    metadata['comment'] = f"{metadata.get('comment', 'Vinyl Master')}\nPrepared for vinyl cutting | Stereo Required"

    return create_music_mastering_workflow(
        input_file=input_file,
        output_dir=output_dir,
        metadata=metadata,
        quality_profile="studio",  # Strictest validation
        channel_conversion="stereo",  # Vinyl requires stereo
        mixing_algorithm="average",
        include_flac=True,
        include_mp3=False,  # No lossy compression for vinyl
        generate_analysis=True  # Full frequency analysis required
    )


def create_broadcast_mastering_workflow(
    input_file: str,
    output_dir: str,
    metadata: Dict[str, str],
    mixing_algorithm: str = "downmix_center"
) -> WorkflowEngine:
    """
    Broadcast mastering workflow for radio distribution

    Mono-only MP3 optimized for AM/FM broadcast

    Args:
        input_file: Audio file to master
        output_dir: Output directory
        metadata: Track metadata
        mixing_algorithm: Algorithm for stereo→mono conversion

    Returns:
        WorkflowEngine with broadcast mastering pipeline
    """

    metadata['comment'] = f"{metadata.get('comment', 'Broadcast Master')}\nOptimized for radio broadcast | Mono"

    return create_music_mastering_workflow(
        input_file=input_file,
        output_dir=output_dir,
        metadata=metadata,
        quality_profile="professional",
        channel_conversion="mono",  # Broadcast requires mono
        mixing_algorithm=mixing_algorithm,
        include_flac=False,
        include_mp3=True,  # MP3 192kbps for broadcast
        generate_analysis=False  # Speed over analysis
    )


def create_mono_compatibility_workflow(
    input_file: str,
    output_dir: str,
    metadata: Dict[str, str]
) -> WorkflowEngine:
    """
    Mono compatibility testing workflow

    Creates mono version for compatibility testing (clubs, phones, mono speakers)

    Args:
        input_file: Audio file to test
        output_dir: Output directory
        metadata: Track metadata

    Returns:
        WorkflowEngine with mono compatibility test pipeline
    """

    metadata['comment'] = f"{metadata.get('comment', 'Mono Compatibility Test')}\nMono version for testing"

    return create_music_mastering_workflow(
        input_file=input_file,
        output_dir=output_dir,
        metadata=metadata,
        quality_profile="professional",
        channel_conversion="mono",  # Create mono version
        mixing_algorithm="downmix_center",
        include_flac=True,  # Keep high quality for analysis
        include_mp3=False,
        generate_analysis=True  # Compare frequency response
    )


# Workflow modes for UI
MASTERING_MODES = {
    'quick': {
        'name': 'Quick Mastering',
        'description': 'Fast MP3 conversion with basic metadata',
        'include_flac': False,
        'include_mp3': True,
        'generate_analysis': False,
        'quality_profile': 'professional'
    },
    'standard': {
        'name': 'Standard Mastering',
        'description': 'FLAC + MP3 with quality validation',
        'include_flac': True,
        'include_mp3': True,
        'generate_analysis': False,
        'quality_profile': 'professional'
    },
    'professional': {
        'name': 'Professional Mastering',
        'description': 'Full validation with frequency analysis',
        'include_flac': True,
        'include_mp3': True,
        'generate_analysis': True,
        'quality_profile': 'studio'
    },
    'streaming': {
        'name': 'Streaming Optimized',
        'description': 'MP3 320kbps for streaming platforms',
        'include_flac': False,
        'include_mp3': True,
        'generate_analysis': False,
        'quality_profile': 'professional'
    },
    'vinyl': {
        'name': 'Vinyl Preparation',
        'description': 'FLAC lossless for vinyl cutting',
        'include_flac': True,
        'include_mp3': False,
        'generate_analysis': True,
        'quality_profile': 'studio'
    }
}


def get_mastering_mode(mode_name: str) -> Dict[str, Any]:
    """
    Get mastering workflow mode configuration

    Args:
        mode_name: Mode name (quick, standard, professional, streaming, vinyl)

    Returns:
        Mode configuration dict
    """
    return MASTERING_MODES.get(mode_name, MASTERING_MODES['standard'])


if __name__ == "__main__":
    from rich.console import Console
    console = Console()

    console.print("[cyan]Professional Music Mastering Workflow Loaded[/cyan]")
    console.print(f"Available modes: {list(MASTERING_MODES.keys())}")
    console.print("✅ Multi-format mastering pipeline ready")
    console.print("✅ FLAC (lossless archive) + MP3 (distribution) support")
