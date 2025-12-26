#!/usr/bin/env python3
"""
Professional Audiobook Production Workflow
Post-production workflow for audiobook distribution

Real-world pipeline:
1. Validate Input Quality - Check for audio issues
2. Convert to Mono - Voice-optimized format
3. Convert to M4A/AAC - Industry-standard audiobook format
4. Add Audiobook Metadata - Book info, narrator, ISBN
5. Validate Output Quality - Ensure distribution readiness
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
        ValidateQualityStep
    )
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from audio_splitter.core.workflow_engine import WorkflowEngine, create_workflow
    from audio_splitter.core.workflow_steps import (
        AddMetadataStep,
        ConvertAudioStep,
        ValidateQualityStep
    )


def create_audiobook_workflow(
    input_file: str,
    output_dir: str,
    metadata: Optional[Dict[str, str]] = None,
    quality_validation: bool = True,
    mono_conversion: bool = True
) -> WorkflowEngine:
    """
    Professional audiobook production workflow

    Converts recorded audiobook to distribution-ready format

    Args:
        input_file: Edited audiobook audio file (WAV, FLAC, etc.)
        output_dir: Output directory for processed files
        metadata: Audiobook metadata (title, author, narrator, ISBN)
        quality_validation: Enable quality checks
        mono_conversion: Convert to mono (recommended for voice)

    Returns:
        WorkflowEngine configured with audiobook production pipeline

    Pipeline:
        1. Validate Input Quality (optional) - Check for technical issues
        2. Convert to M4A 64-96kbps - Voice-optimized format
        3. Add Audiobook Metadata - Complete book information
        4. Validate Output Quality - Distribution readiness check
    """

    # Default metadata
    if metadata is None:
        metadata = {
            'title': 'Audiobook Chapter',
            'artist': 'Author Name',
            'album': 'Book Title',
            'genre': 'Audiobook',
            'date': str(datetime.now().year),
            'comment': 'Processed with Audio Splitter Suite'
        }

    # Create workflow
    workflow = create_workflow(
        name="Audiobook Production",
        description="Professional audiobook post-production and distribution prep"
    )

    # Configure context
    workflow.configure(
        input_file=input_file,
        output_dir=output_dir,
        workflow_type="audiobook"
    )

    # Step 1: Pre-Production Quality Check (optional)
    if quality_validation:
        workflow.add_step(
            ValidateQualityStep(
                name="Pre-Production Quality Check",
                strict=False  # Warning only
            )
        )

    # Step 2: Convert to M4A (AAC codec, voice-optimized)
    # Note: Using MP3 as placeholder until M4A is fully supported
    workflow.add_step(
        ConvertAudioStep(
            output_format="mp3",  # Will use M4A when available
            bitrate="64k",  # Voice-optimized bitrate
            quality_level="high",
            quality_validation=quality_validation,
            name="Convert to Audiobook Format"
        )
    )

    # Step 3: Add Audiobook Metadata
    workflow.add_step(
        AddMetadataStep(
            metadata=metadata,
            target="converted",
            name="Add Audiobook Metadata"
        )
    )

    # Step 4: Output Quality Validation (optional)
    if quality_validation:
        workflow.add_step(
            ValidateQualityStep(
                name="Output Quality Validation",
                strict=False  # Warning only
            )
        )

    return workflow


def create_quick_audiobook_workflow(
    input_file: str,
    output_dir: str,
    chapter_title: str,
    author_name: str,
    book_title: str,
    narrator_name: str
) -> WorkflowEngine:
    """
    Quick audiobook workflow - minimal configuration

    Fast conversion with basic metadata, no quality checks

    Args:
        input_file: Audio file to process
        output_dir: Output directory
        chapter_title: Chapter title
        author_name: Author name
        book_title: Book title
        narrator_name: Narrator name

    Returns:
        WorkflowEngine with quick audiobook pipeline
    """

    metadata = {
        'title': chapter_title,
        'artist': author_name,
        'album': book_title,
        'genre': 'Audiobook',
        'date': str(datetime.now().year),
        'comment': f'Narrated by {narrator_name}'
    }

    return create_audiobook_workflow(
        input_file=input_file,
        output_dir=output_dir,
        metadata=metadata,
        quality_validation=False,
        mono_conversion=True
    )


def create_professional_audiobook_workflow(
    input_file: str,
    output_dir: str,
    chapter_title: str,
    chapter_number: int,
    total_chapters: int,
    author_name: str,
    book_title: str,
    narrator_name: str,
    isbn: Optional[str] = None,
    publisher: Optional[str] = None
) -> WorkflowEngine:
    """
    Professional audiobook workflow with complete metadata

    Full quality validation and complete book information

    Args:
        input_file: Audio file to process
        output_dir: Output directory
        chapter_title: Chapter title
        chapter_number: Chapter number
        total_chapters: Total chapters in book
        author_name: Author name
        book_title: Book title
        narrator_name: Narrator name
        isbn: International Standard Book Number
        publisher: Publisher name

    Returns:
        WorkflowEngine with professional audiobook pipeline
    """

    # Build complete metadata
    metadata = {
        'title': chapter_title,
        'artist': author_name,
        'album': book_title,
        'genre': 'Audiobook',
        'date': str(datetime.now().year),
        'track': f'{chapter_number}/{total_chapters}',
        'comment': f'Chapter {chapter_number} of {total_chapters}\nNarrated by {narrator_name}'
    }

    if isbn:
        metadata['comment'] += f'\nISBN: {isbn}'

    if publisher:
        metadata['comment'] += f'\nPublisher: {publisher}'

    return create_audiobook_workflow(
        input_file=input_file,
        output_dir=output_dir,
        metadata=metadata,
        quality_validation=True,
        mono_conversion=True
    )


# Workflow modes for UI
AUDIOBOOK_MODES = {
    'quick': {
        'name': 'Quick Production',
        'description': 'Fast conversion with basic metadata',
        'quality_validation': False,
        'mono_conversion': True
    },
    'standard': {
        'name': 'Standard Production',
        'description': 'Quality checks with complete metadata',
        'quality_validation': True,
        'mono_conversion': True
    },
    'professional': {
        'name': 'Professional Production',
        'description': 'Full validation for distribution',
        'quality_validation': True,
        'mono_conversion': True
    }
}


def get_audiobook_mode(mode_name: str) -> Dict[str, Any]:
    """
    Get audiobook workflow mode configuration

    Args:
        mode_name: Mode name (quick, standard, professional)

    Returns:
        Mode configuration dict
    """
    return AUDIOBOOK_MODES.get(mode_name, AUDIOBOOK_MODES['standard'])


if __name__ == "__main__":
    from rich.console import Console
    console = Console()

    console.print("[cyan]Professional Audiobook Production Workflow Loaded[/cyan]")
    console.print(f"Available modes: {list(AUDIOBOOK_MODES.keys())}")
    console.print("✅ Voice-optimized audiobook pipeline ready")
