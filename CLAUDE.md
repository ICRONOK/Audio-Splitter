# CLAUDE.md - Audio Splitter Suite Developer Guide

> **Last Updated:** 2025-12-27
> **Version:** 2.0.0
> **Status:** Production Ready

## Table of Contents
1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Project Structure](#project-structure)
4. [Core Components](#core-components)
5. [Technologies & Dependencies](#technologies--dependencies)
6. [Entry Points & Workflows](#entry-points--workflows)
7. [Configuration System](#configuration-system)
8. [Development Guidelines](#development-guidelines)
9. [Testing](#testing)
10. [Key Patterns & Conventions](#key-patterns--conventions)

---

## Project Overview

### Purpose
**Audio Splitter Suite** is a professional-grade, open-source CLI application for audio processing. It provides a comprehensive toolkit for audio file manipulation across multiple formats with scientific quality validation.

### Target Users
- Audio engineers and producers
- Podcast creators and editors
- Music producers and mastering engineers
- Content creators requiring batch audio operations
- Audio archivists

### Key Value Propositions
- **Full-featured yet minimal:** Complete audio processing in ~18 core files
- **Scientific quality:** THD+N and SNR measurements with industry-standard thresholds
- **Professional workflows:** Pre-built automation for common production scenarios
- **Multi-interface:** CLI, interactive menu, and programmatic API
- **Multi-language:** i18n support (Spanish, English, French, German, Portuguese)

### Version History
- **v0.1:** Initial audio splitting
- **v0.2:** Basic features
- **v0.3:** Audio converter + metadata editor
- **v0.4:** Interactive interface
- **v2.0.0:** Professional workflows + batch processing + quality framework

---

## Architecture

### Architectural Pattern: Layered + Modular

```
┌─────────────────────────────────────────┐
│        Presentation Layer (UI)          │
│  CLI | Interactive | Batch | Workflows │
└──────────────────┬──────────────────────┘
         ↓
┌──────────────────────────────────────────┐
│      Business Logic Layer (Core)         │
│  Splitter | Converter | Metadata | QA   │
│  Enhanced versions | Workflow Engine    │
└──────────────────┬───────────────────────┘
         ↓
┌──────────────────────────────────────────┐
│   Audio Processing Layer (Libraries)    │
│ librosa | soundfile | pydub | scipy     │
└──────────────────┬───────────────────────┘
         ↓
┌──────────────────────────────────────────┐
│      Infrastructure Layer                │
│  File I/O | Configuration | Logging      │
└──────────────────────────────────────────┘
```

### Design Principles
1. **Separation of Concerns:** Core processing logic is UI-independent
2. **Modularity:** Each component is independently testable and reusable
3. **Extensibility:** Easy to add new formats, workflows, and operations
4. **Quality-First:** Scientific validation is a first-class citizen
5. **Hybrid Library Strategy:** librosa for precision + pydub for convenience

### Key Design Patterns
- **Strategy Pattern:** Multiple audio processing algorithms (e.g., downmix strategies)
- **Decorator Pattern:** `@high_quality_processing` for quality tracking
- **Factory Pattern:** AudioQualityAnalyzer creation
- **Template Method:** Workflow step execution pipeline
- **Command Pattern:** CLI command structure
- **Chain of Responsibility:** Error handling with fallback mechanisms

---

## Project Structure

```
/Users/ochand/Dev/Audio-Splitter/
├── audio_splitter/                    # Main package
│   ├── config/                        # Configuration & quality settings
│   │   ├── settings.py               # Output directory configuration
│   │   ├── environment.py            # Environment variable handling
│   │   └── quality_settings.py       # Quality profiles & user preferences
│   │
│   ├── core/                          # Core processing modules (16 files, ~260KB)
│   │   ├── splitter.py               # Audio splitting (7.2KB)
│   │   ├── converter.py              # Format conversion (42.7KB)
│   │   ├── metadata_manager.py       # Metadata editing (29.3KB)
│   │   ├── spectrogram_generator.py  # Spectrogram creation (23.5KB)
│   │   ├── batch_processor.py        # Batch operations (23.1KB)
│   │   ├── workflow_engine.py        # Workflow automation (12.6KB)
│   │   ├── quality_framework.py      # Scientific quality assessment (21.9KB)
│   │   ├── enhanced_converter.py     # Enhanced conversion (11.9KB)
│   │   ├── enhanced_splitter.py      # Enhanced splitting (18.3KB)
│   │   ├── enhanced_spectrogram.py   # Enhanced spectrograms (31.7KB)
│   │   ├── workflow_steps.py         # Workflow step definitions (19.4KB)
│   │   └── workflows/                # Pre-built professional workflows
│   │       ├── podcast_workflow.py   # Podcast production (274 lines)
│   │       ├── music_workflow.py     # Music mastering (541 lines)
│   │       └── audiobook_workflow.py # Audiobook processing (276 lines)
│   │
│   ├── ui/                            # User Interface layer (6 files)
│   │   ├── cli.py                    # Command-line interface (910 lines)
│   │   ├── interactive.py            # Interactive menu system (845 lines)
│   │   ├── interactive_i18n.py       # Multi-language interactive (271 lines)
│   │   ├── workflow_interface.py     # Workflow UI integration (549 lines)
│   │   ├── batch_interface.py        # Batch operation UI (269 lines)
│   │   └── channel_interface.py      # Channel conversion UI (548 lines)
│   │
│   ├── i18n/                          # Internationalization
│   │   ├── translator.py             # Translation engine (248 lines)
│   │   ├── config.py                 # i18n configuration (184 lines)
│   │   └── languages/                # Language files
│   │       └── es.json               # Spanish translations
│   │
│   └── utils/                         # Utility modules (5 files)
│       ├── audio_utils.py            # Audio utility functions (135 lines)
│       ├── file_utils.py             # File operations (127 lines)
│       ├── cli_loader.py             # CLI argument parsing (414 lines)
│       ├── logging_utils.py          # Logging configuration (72 lines)
│       └── progress_tracker.py       # Progress visualization (170 lines)
│
├── main.py                            # Entry point (26 lines)
├── tests/                             # Test suite (6 test files)
│   ├── test_splitter.py
│   ├── test_converter.py
│   ├── test_batch_processing.py
│   ├── test_professional_workflows.py
│   ├── test_workflow_engine.py
│   └── test_integration_workflows_batch.py
│
├── docs/                              # Documentation (7 files)
│   ├── README.md                     # Main documentation
│   ├── CLI_REFERENCE.md              # Command reference
│   ├── CLI_EXAMPLES.md               # Usage examples
│   ├── CLI_QUICK_START.md            # Quick start guide
│   ├── architecture.md               # Software architecture
│   ├── implementation.md             # Implementation details
│   └── cli_data.yaml                 # CLI metadata
│
├── scripts/                           # Utility scripts
│   ├── update_docs.py
│   ├── test_cli_examples.py
│   └── validate_system.py
│
├── data/                              # Data directories
│   ├── output/                       # Output audio files
│   ├── sources/                      # Source audio files
│   └── templates/                    # Metadata templates
│
├── requirements.txt                  # Python dependencies (38 packages)
├── setup.py                          # Package configuration
├── verify.py                         # System verification
└── .env.template                     # Environment template

TOTAL: 37 Python files, ~12,300 lines of code
```

---

## Core Components

### 1. Audio Processing Core (`audio_splitter/core/`)

#### Splitter (`splitter.py` + `enhanced_splitter.py`)
**Purpose:** Divide audio files into named segments with precision timing

**Key Features:**
- Multiple segment definition formats (MM:SS, HH:MM:SS, seconds)
- Zero-crossing detection for optimal split points
- Cross-fade transitions (10ms Hann window) to eliminate boundary artifacts
- Triangular dithering for bit-depth reduction
- Quality validation per segment

**Usage Example:**
```python
from audio_splitter.core.enhanced_splitter import EnhancedAudioSplitter

splitter = EnhancedAudioSplitter()
segments = [("0:00", "1:30", "intro"), ("1:30", "5:00", "main")]
splitter.split_audio("input.wav", segments, "output/")
```

#### Converter (`converter.py` + `enhanced_converter.py`)
**Purpose:** Multi-format conversion with quality preservation

**Supported Formats:** WAV ↔ MP3 ↔ FLAC ↔ M4A ↔ OGG

**Quality Presets:**
- `low`: 128kbps MP3 / compression 5 FLAC
- `medium`: 192kbps MP3 / compression 8 FLAC
- `high`: 320kbps MP3 / compression 12 FLAC
- `vbr_low/medium/high`: Variable bitrate options

**Key Features:**
- Metadata preservation during conversion
- Channel-aware conversion
- Batch processing support

#### Metadata Manager (`metadata_manager.py`)
**Purpose:** Professional ID3v2.4, Vorbis, and iTunes tag management

**Supported Fields:**
- Basic: Title, Artist, Album, Album Artist, Date, Genre
- Advanced: Track, Disc, Composer, Comment
- Artwork: JPEG/PNG embedding and extraction

**Template System:**
- Save metadata configurations as JSON templates
- Apply templates to multiple files
- Batch metadata operations

#### Spectrogram Generator (`spectrogram_generator.py` + `enhanced_spectrogram.py`)
**Purpose:** Visual audio analysis with LLM optimization

**Spectrogram Types:**
- Mel spectrogram (for speech/music analysis)
- CQT (Constant-Q Transform)
- Dual spectrograms (side-by-side comparison)

**LLM Optimization:**
- High resolution output for AI analysis
- Artifact detection visualization
- Quality metrics overlay

#### Quality Framework (`quality_framework.py`)
**Purpose:** Scientific audio quality assessment

**Metrics:**
- **THD+N:** Total Harmonic Distortion + Noise
- **SNR:** Signal-to-Noise Ratio
- **Dynamic Range:** Preservation percentage
- **Peak Level:** Clipping detection
- **Artifact Detection:** Clipping, aliasing, DC offset

**Quality Levels:**
```python
EXCELLENT: THD+N < -80dB, SNR > 100dB  # Studio mastering
GOOD:      THD+N < -60dB, SNR > 90dB   # Professional broadcast
ACCEPTABLE: THD+N < -40dB, SNR > 70dB  # Consumer electronics
POOR:      Below acceptable thresholds
FAILED:    Critical failures detected
```

**Quality Profiles:**
- **STUDIO:** Maximum quality for professional mastering
- **PROFESSIONAL:** High quality for broadcast/production
- **STANDARD:** Good quality for consumer use
- **BASIC:** Acceptable quality for web streaming
- **CUSTOM:** User-defined thresholds

#### Workflow Engine (`workflow_engine.py`)
**Purpose:** Orchestrate complex multi-step audio processing pipelines

**Core Concepts:**
```python
class WorkflowStep:
    - validate_preconditions()
    - execute(context)
    - validate_postconditions()
    - rollback()

class WorkflowEngine:
    - add_step(step)
    - configure(input_file, output_dir, **kwargs)
    - execute(show_progress=True)
    - rollback()
```

**Workflow Context:**
- Shared state between steps
- Intermediate file tracking
- Metadata propagation
- Quality settings inheritance

### 2. Professional Workflows (`audio_splitter/core/workflows/`)

#### Podcast Workflow (`podcast_workflow.py`)
**Modes:** Quick, Standard, Professional

**Pipeline:**
1. ValidateQualityStep (pre-check)
2. ConvertAudioStep (→ MP3 192kbps streaming-optimized)
3. AddMetadataStep (episode information)
4. GenerateSpectrogramStep (optional waveform)

**Use Cases:**
- Podcast episode production
- Voice recording optimization
- Interview audio processing

#### Music Mastering Workflow (`music_workflow.py`)
**Modes:** Quick, Standard, Professional, Vinyl Prep, Broadcast, Mono Test

**Pipeline (Professional):**
1. ValidateQualityStep (pre-master analysis)
2. ChannelConversionStep (optional mono/stereo)
3. ConvertAudioStep (→ FLAC archival master)
4. ConvertAudioStep (→ MP3 320kbps distribution)
5. AddMetadataStep (complete track metadata)
6. GenerateSpectrogramStep (dual analysis)
7. ValidateQualityStep (post-master validation)

**Use Cases:**
- Album mastering
- Single distribution preparation
- Vinyl cutting master preparation
- Radio broadcast mastering

#### Audiobook Workflow (`audiobook_workflow.py`)
**Modes:** Quick, Standard, Professional

**Pipeline:**
1. ValidateQualityStep (quality check)
2. ConvertAudioStep (→ M4A optimization)
3. AddMetadataStep (book metadata)
4. GenerateSpectrogramStep (optional)

**Use Cases:**
- Audiobook chapter processing
- Narration optimization
- ACX/Audible distribution prep

### 3. User Interfaces (`audio_splitter/ui/`)

#### CLI (`cli.py`)
**Purpose:** Command-line interface for automation and scripting

**Command Structure:**
```bash
python main.py COMMAND [OPTIONS] [ARGS]

Commands:
  split         # Divide audio files into segments
  convert       # Convert between audio formats
  channel       # Convert audio channels (mono ↔ stereo)
  metadata      # Edit audio metadata tags
  spectrogram   # Generate spectrograms
  quality_settings  # Manage quality configuration
```

**Rich Formatting:**
- Progress bars (tqdm + rich)
- Color-coded output (success=green, error=red, info=cyan)
- Tables for structured data
- Spinners for long operations

#### Interactive Menu (`interactive.py` + `interactive_i18n.py`)
**Purpose:** User-friendly navigation for non-technical users

**Features:**
- Module selection navigation
- Context-aware help
- Real-time quality status indicator
- Multi-language support
- Rich color-coded menus

**Entry Point:**
```python
from audio_splitter.ui.interactive_i18n import interactive_menu_i18n
interactive_menu_i18n()
```

### 4. Internationalization (`audio_splitter/i18n/`)

**Supported Languages:** Spanish (default), English, French, German, Portuguese

**Translation System:**
```python
from audio_splitter.i18n.translator import Translator

t = Translator(language="es")
print(t.get("menu.main_title"))  # "Menú Principal"
```

**Fallback Mechanism:**
- If translation missing → return original English string
- If language file missing → default to English

**Translation Files:** JSON format in `audio_splitter/i18n/languages/`

### 5. Configuration System (`audio_splitter/config/`)

#### Settings (`settings.py`)
**Purpose:** Application-wide settings

```python
OUTPUT_DIR = "data/output"
SOURCES_DIR = "data/sources"
DEFAULT_QUALITY = "high"
DEFAULT_FORMAT = "mp3"
```

#### Environment (`environment.py`)
**Purpose:** Environment variable handling

**Supported Variables:**
```bash
AUDIO_SPLITTER_OUTPUT_DIR=data/output
AUDIO_SPLITTER_SOURCES_DIR=data/sources
AUDIO_SPLITTER_DEFAULT_QUALITY=high
AUDIO_SPLITTER_DEFAULT_FORMAT=mp3
AUDIO_SPLITTER_PRESERVE_METADATA=true
```

#### Quality Settings (`quality_settings.py`)
**Purpose:** User quality preferences and profiles

**Configuration File:** `~/.audio_splitter/quality_settings.json`

**User Preferences:**
```json
{
  "default_profile": "professional",
  "enable_quality_validation": true,
  "prefer_enhanced_algorithms": true,
  "enable_cross_fade": true,
  "enable_dithering": true,
  "use_emoji_indicators": true,
  "color_coded_quality": true
}
```

**API:**
```python
from audio_splitter.config.quality_settings import get_quality_settings

settings = get_quality_settings()
settings.set_profile(QualityProfile.STUDIO)
thresholds = settings.get_quality_thresholds()
```

---

## Technologies & Dependencies

### Audio Processing Core
- **librosa** (v0.10.0+): Audio loading/processing with quality preservation
- **soundfile** (v0.12.0+): Efficient WAV file I/O
- **pydub** (v0.25.0+): Audio segment manipulation and MP3 encoding
- **numpy** (v1.21.0+): Numerical array operations and DSP
- **scipy**: Scientific signal processing (filtering, FFT, DSP)

### Metadata Management
- **mutagen** (v1.47.0+): Universal metadata library (ID3v2.4, Vorbis, iTunes)
- **eyed3** (v0.9.7+): Advanced ID3 tag manipulation
- **tinytag** (v1.10.0+): Fast metadata reading

### Format Conversion
- **ffmpeg-python** (v0.2.0+): FFmpeg wrapper for format conversion
- **Pillow** (v10.0.0+): Image processing for artwork

### Analysis & Visualization
- **matplotlib** (v3.7.0+): Spectrogram generation
- **seaborn** (v0.12.0+): Statistical visualization
- **opencv-python** (v4.8.0+): Computer vision for LLM optimization

### User Interface
- **rich** (v13.0.0+): Terminal UI with colors, tables, progress bars
- **click** (v8.1.0+): CLI framework
- **tabulate** (v0.9.0+): ASCII table generation
- **colorama** (v0.4.6+): Cross-platform terminal colors
- **tqdm** (v4.64.0+): Progress bars

### Utilities
- **python-magic** (v0.4.27+): File type detection
- **requests** (v2.28.0+): HTTP for downloading artwork

### Testing & Development
- **pytest** (v7.0.0+): Testing framework
- **pytest-cov** (v4.0.0+): Code coverage
- **black** (v22.0.0+): Code formatter
- **flake8** (v5.0.0+): Linter
- **mypy** (v1.0.0+): Static type checking

---

## Entry Points & Workflows

### Primary Entry Point: `main.py`
```python
#!/usr/bin/env python3
if __name__ == "__main__":
    from audio_splitter.ui.interactive_i18n import interactive_menu_i18n
    try:
        interactive_menu_i18n()  # Multi-language interactive interface
    except KeyboardInterrupt:
        print("\n\n👋 Salida manual detectada. ¡Hasta luego!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
```

### Secondary Entry Points (via `setup.py`)
```bash
# After pip install -e .
audio-splitter            # → audio_splitter.ui.cli:main_cli
audio-splitter-gui        # → audio_splitter.ui.interactive:interactive_menu
```

### Three Operating Modes

#### 1. Interactive Mode (Default)
```bash
python main.py
```
- Shows main menu with module selection
- Context-aware help and navigation
- Multi-language support
- Best for: Non-technical users, exploration

#### 2. CLI Mode (Scripting)
```bash
python main.py split audio.wav -s "0:30-1:30:intro" "1:30-3:00:main"
python main.py convert input.wav --output output.mp3 --format mp3 --quality high
python main.py metadata song.mp3 --title "Song" --artist "Artist" --artwork cover.jpg
python main.py channel stereo.wav --output mono.wav --to mono --algorithm downmix_center
python main.py spectrogram audio.mp3 --type mel --llm-optimized
```
- Full command set with options
- Scriptable and automatable
- Best for: Power users, batch scripts, CI/CD

#### 3. Programmatic Mode (API)
```python
from audio_splitter.core.workflows.podcast_workflow import create_podcast_workflow

workflow = create_podcast_workflow(
    input_file="episode.wav",
    output_dir="output",
    metadata={'title': 'Episode 1', 'artist': 'My Podcast'},
    quality_validation=True,
    mode='professional'
)
results = workflow.execute()
```
- Direct Python API access
- Workflow automation
- Best for: Integration, custom pipelines

---

## Configuration System

### Environment Variables
Create `.env` file in project root:
```bash
AUDIO_SPLITTER_OUTPUT_DIR=data/output
AUDIO_SPLITTER_SOURCES_DIR=data/sources
AUDIO_SPLITTER_DEFAULT_QUALITY=high
AUDIO_SPLITTER_DEFAULT_FORMAT=mp3
AUDIO_SPLITTER_PRESERVE_METADATA=true
AUDIO_SPLITTER_DEFAULT_ENCODING=utf-8
```

### User Quality Settings
Location: `~/.audio_splitter/quality_settings.json`

**Example Configuration:**
```json
{
  "default_profile": "professional",
  "enable_quality_validation": true,
  "prefer_enhanced_algorithms": true,
  "enable_cross_fade": true,
  "enable_dithering": true,
  "processing_priority": "balanced",
  "use_emoji_indicators": true,
  "color_coded_quality": true
}
```

**Programmatic Access:**
```python
from audio_splitter.config.quality_settings import get_quality_settings, QualityProfile

settings = get_quality_settings()
settings.set_profile(QualityProfile.STUDIO)
settings.preferences.enable_cross_fade = True
settings.save_preferences()
```

### Language Configuration
Default: Spanish (es)

**Change Language:**
```python
from audio_splitter.i18n.translator import Translator

translator = Translator(language="en")  # English
# Available: es, en, fr, de, pt
```

---

## Development Guidelines

### Code Style
- **Formatter:** Black (line length: 100)
- **Linter:** Flake8
- **Type Checking:** mypy (optional but recommended)
- **Docstrings:** Google style docstrings

**Example:**
```python
def convert_audio(
    input_file: str,
    output_file: str,
    output_format: str = "mp3",
    quality: str = "high"
) -> bool:
    """
    Convert audio file to a different format.

    Args:
        input_file: Path to input audio file
        output_file: Path to output audio file
        output_format: Target format (mp3, flac, wav, etc.)
        quality: Quality preset (low, medium, high, vbr_high)

    Returns:
        True if conversion successful, False otherwise

    Raises:
        FileNotFoundError: If input file doesn't exist
        ValueError: If output format is not supported
    """
    pass
```

### Error Handling Philosophy
1. **Fail Fast:** Validate inputs early
2. **Informative Errors:** Clear error messages with context
3. **Graceful Degradation:** Non-critical features can fail without breaking workflow
4. **User-Friendly:** Terminal users see friendly messages, not stack traces

**Example:**
```python
try:
    audio, sr = librosa.load(input_file, sr=None)
except FileNotFoundError:
    console.print(f"[red]❌ Error: Archivo no encontrado: {input_file}[/red]")
    return False
except Exception as e:
    console.print(f"[red]❌ Error al cargar audio: {str(e)}[/red]")
    return False
```

### Performance Considerations

#### Memory Management
- **Current Strategy:** Load complete file into memory
- **Justification:** Typical audio files < 2GB, simplicity
- **Future:** Implement streaming for files > 2GB

#### Optimization Tips
```python
# GOOD: Slicing without copy
segment = audio_array[start_sample:end_sample]

# AVOID: Unnecessary copy
segment = audio_array[start_sample:end_sample].copy()

# GOOD: Load without resampling
audio, sr = librosa.load(file, sr=None)

# AVOID: Unnecessary resampling
audio, sr = librosa.load(file, sr=22050)
```

#### Complexity Analysis
| Operation | Time Complexity | Space Complexity |
|-----------|----------------|------------------|
| Audio Loading | O(n) | O(n) |
| Segment Extraction | O(k) | O(k) |
| File Writing | O(k) | O(1) |
| Time Parsing | O(1) | O(1) |
| Quality Analysis | O(n) | O(1) |

Where n = total file size, k = segment size

### Adding New Features

#### Adding a New Audio Operation
1. Create core logic in `audio_splitter/core/my_operation.py`
2. Add CLI command in `audio_splitter/ui/cli.py`
3. Add interactive menu option in `audio_splitter/ui/interactive.py`
4. Write tests in `tests/test_my_operation.py`
5. Update documentation

**Example Structure:**
```python
# audio_splitter/core/my_operation.py
class MyOperation:
    def execute(self, input_file: str, **params) -> bool:
        """Execute the operation"""
        pass

    def validate_params(self, **params) -> bool:
        """Validate parameters"""
        pass
```

#### Adding a New Workflow
1. Create workflow in `audio_splitter/core/workflows/my_workflow.py`
2. Define workflow steps using `WorkflowStep` base class
3. Register in workflow interface
4. Add documentation

**Example:**
```python
from audio_splitter.core.workflow_engine import WorkflowEngine, WorkflowStep

class MyCustomStep(WorkflowStep):
    def execute(self, context):
        # Custom logic here
        return {'success': True}

def create_my_workflow(input_file, output_dir, **kwargs):
    workflow = WorkflowEngine("My Workflow", "Custom processing pipeline")
    workflow.configure(input_file=input_file, output_dir=output_dir, **kwargs)
    workflow.add_step(MyCustomStep("Step 1", "First operation"))
    return workflow
```

#### Adding a New Format
1. Add format support in `audio_splitter/core/converter.py`
2. Update format detection logic
3. Add quality presets for the format
4. Update tests and documentation

### Testing Strategy
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=audio_splitter --cov-report=html

# Run specific test file
pytest tests/test_splitter.py

# Run specific test
pytest tests/test_splitter.py::test_basic_split
```

### Documentation Updates
```bash
# Update CLI documentation
python scripts/update_docs.py

# Test CLI examples
python scripts/test_cli_examples.py

# Validate system
python verify.py
```

---

## Testing

### Test Structure
```
tests/
├── test_splitter.py                    # Audio splitting tests
├── test_converter.py                   # Format conversion tests
├── test_batch_processing.py            # Batch operation tests
├── test_professional_workflows.py      # Workflow tests
├── test_workflow_engine.py             # Engine tests
└── test_integration_workflows_batch.py # Integration tests
```

### Test Coverage Goals
- Core modules: > 80% coverage
- UI modules: > 60% coverage
- Workflows: > 70% coverage

### Running Tests
```bash
# All tests
pytest

# Specific module
pytest tests/test_splitter.py -v

# Coverage report
pytest --cov=audio_splitter --cov-report=term-missing

# HTML coverage report
pytest --cov=audio_splitter --cov-report=html
# Open htmlcov/index.html
```

---

## Key Patterns & Conventions

### File Naming
- **Modules:** lowercase_with_underscores.py
- **Classes:** PascalCase
- **Functions:** lowercase_with_underscores
- **Constants:** UPPERCASE_WITH_UNDERSCORES

### Import Organization
```python
# Standard library
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Third-party
import numpy as np
import librosa
from rich.console import Console

# Local
from audio_splitter.config import settings
from audio_splitter.core.quality_framework import AudioQualityAnalyzer
```

### Quality Validation Pattern
```python
@high_quality_processing
def my_audio_function(audio_data, sr):
    # Processing logic
    return processed_audio
```

### Progress Tracking Pattern
```python
from rich.progress import Progress, SpinnerColumn, TextColumn

with Progress(
    SpinnerColumn(),
    TextColumn("[progress.description]{task.description}"),
    console=console
) as progress:
    task = progress.add_task("Processing...", total=total_items)
    for item in items:
        process_item(item)
        progress.advance(task)
```

### Error Handling Pattern
```python
from rich.console import Console
console = Console()

try:
    result = risky_operation()
except SpecificError as e:
    console.print(f"[red]❌ Specific error: {str(e)}[/red]")
    return False
except Exception as e:
    console.print(f"[red]❌ Unexpected error: {str(e)}[/red]")
    return False
```

### Configuration Loading Pattern
```python
from audio_splitter.config.quality_settings import get_quality_settings

settings = get_quality_settings()
config = settings.get_processing_config()

if config['enable_cross_fade']:
    # Apply cross-fade
    pass
```

---

## Common Tasks Reference

### Split Audio File
```bash
# CLI
python main.py split audio.wav -s "0:00-1:30:intro" "1:30-5:00:main"

# Python
from audio_splitter.core.enhanced_splitter import EnhancedAudioSplitter
splitter = EnhancedAudioSplitter()
splitter.split_audio("audio.wav", [("0:00", "1:30", "intro")], "output/")
```

### Convert Format
```bash
# CLI
python main.py convert input.wav --output output.mp3 --format mp3 --quality high

# Python
from audio_splitter.core.enhanced_converter import EnhancedAudioConverter
converter = EnhancedAudioConverter()
converter.convert("input.wav", "output.mp3", "mp3", quality="high")
```

### Edit Metadata
```bash
# CLI
python main.py metadata song.mp3 --title "Song Title" --artist "Artist Name"

# Python
from audio_splitter.core.metadata_manager import MetadataManager
manager = MetadataManager()
manager.update_metadata("song.mp3", title="Song Title", artist="Artist Name")
```

### Channel Conversion
```bash
# CLI
python main.py channel stereo.wav --output mono.wav --to mono --algorithm downmix_center

# Python
from audio_splitter.core.channel_converter import ChannelConverter
converter = ChannelConverter()
converter.convert_channels("stereo.wav", "mono.wav", target="mono")
```

### Run Workflow
```bash
# CLI (Interactive)
python main.py
# Select Option 7: Professional Workflows

# Python
from audio_splitter.core.workflows.podcast_workflow import create_podcast_workflow
workflow = create_podcast_workflow("episode.wav", "output/", mode='professional')
results = workflow.execute()
```

### Generate Spectrogram
```bash
# CLI
python main.py spectrogram audio.mp3 --type mel --llm-optimized

# Python
from audio_splitter.core.enhanced_spectrogram import EnhancedSpectrogramGenerator
generator = EnhancedSpectrogramGenerator()
generator.generate("audio.mp3", "output.png", spectrogram_type="mel")
```

---

## Important Notes for Claude

### When Making Changes
1. **Always read files before editing:** Use Read tool to understand current code
2. **Preserve existing patterns:** Follow established conventions in the codebase
3. **Test changes:** Run relevant tests after modifications
4. **Update documentation:** Keep docs in sync with code changes
5. **Check quality settings:** Respect user's quality preferences

### File Locations to Remember
- **Entry point:** `/Users/ochand/Dev/Audio-Splitter/main.py`
- **Core logic:** `/Users/ochand/Dev/Audio-Splitter/audio_splitter/core/`
- **UI layer:** `/Users/ochand/Dev/Audio-Splitter/audio_splitter/ui/`
- **Config:** `/Users/ochand/Dev/Audio-Splitter/audio_splitter/config/`
- **Tests:** `/Users/ochand/Dev/Audio-Splitter/tests/`
- **User config:** `~/.audio_splitter/quality_settings.json`

### Common Pitfalls to Avoid
1. **Don't use bash for file operations:** Use Read/Edit/Write tools instead
2. **Don't guess file locations:** Use Glob/Grep to find files
3. **Don't break existing workflows:** Test interactive and CLI modes
4. **Don't ignore quality validation:** It's a core feature
5. **Don't modify core algorithms without understanding:** They're scientifically tuned

### Architecture Decisions to Respect
1. **Hybrid audio library approach:** librosa for precision, pydub for convenience
2. **Quality as first-class citizen:** Always include quality validation
3. **Modular design:** Keep UI separate from core logic
4. **Multi-interface support:** Maintain CLI, interactive, and programmatic APIs
5. **i18n support:** All user-facing strings should be translatable

### Project Philosophy
- **Professional yet accessible:** Balance power with usability
- **Scientific rigor:** Measurements over guesses
- **Minimal footprint:** Maximum features, minimal dependencies
- **Extensible architecture:** Easy to add, hard to break
- **User-centric:** Serve audio engineers and casual users alike

---

## Quick Reference Card

### Project Stats
- **Lines of Code:** ~12,300
- **Python Files:** 37
- **Core Modules:** 16
- **Workflows:** 3 (Podcast, Music, Audiobook)
- **Supported Formats:** WAV, MP3, FLAC, M4A, OGG
- **Supported Languages:** 5 (es, en, fr, de, pt)

### Key Commands
```bash
# Interactive mode
python main.py

# Split audio
python main.py split FILE -s "START-END:NAME"

# Convert format
python main.py convert FILE --format FORMAT --quality QUALITY

# Edit metadata
python main.py metadata FILE --title TITLE --artist ARTIST

# Channel conversion
python main.py channel FILE --to mono/stereo

# Spectrogram
python main.py spectrogram FILE --type TYPE

# Quality settings
python main.py quality_settings
```

### Quick Install
```bash
pip install -r requirements.txt
pip install -e .
audio-splitter --help
```

---

**Last Updated:** 2025-12-27
**Maintainer:** Audio Splitter Team
**License:** MIT
**Python:** >=3.8
**Status:** Production Ready

For more details, see:
- [Architecture Documentation](docs/architecture.md)
- [Implementation Guide](docs/implementation.md)
- [CLI Reference](docs/CLI_REFERENCE.md)
- [Examples](docs/CLI_EXAMPLES.md)
