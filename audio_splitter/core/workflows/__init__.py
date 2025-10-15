"""
Workflows Module - Professional Audio Processing Workflows
Contiene workflows predefinidos para casos de uso comunes
"""

from .podcast_workflow import create_podcast_workflow
from .music_workflow import create_music_mastering_workflow

__all__ = [
    'create_podcast_workflow',
    'create_music_mastering_workflow'
]
