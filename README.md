# 🎵 Audio Splitter CLI - Minimal Distribution

Professional audio processing CLI with full functionality in minimal package.

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Test functionality
python main.py --help
python main.py

# Examples
python main.py split audio.wav --segments "0:30-1:30:intro"
python main.py convert input.wav --output output.mp3 --format mp3
python main.py metadata song.mp3 --title "Song" --artist "Artist"
```

## ✨ Features

- ✂️ Audio Splitting with precision
- 🔄 Format Conversion (WAV/MP3/FLAC)
- 🏷️ Professional Metadata Editing
- 📊 LLM-optimized Spectrograms
- 🎚️ Channel Conversion (mono/stereo)
- 🎬 Professional Workflows (Podcast, Music, Audiobook)
- 📦 Batch Processing for mass operations
- 🔬 Scientific Quality Validation (THD+N, SNR)
- 🖥️ CLI + Interactive interfaces

## 📦 Installation

```bash
pip install -e .  # Install as package
audio-splitter --help  # Now available globally
```

<!-- CLI_SECTION_START -->
## 🖥️ Command Line Interface

Audio Splitter Suite provides a powerful command-line interface for all audio processing needs.

### Quick Start

```bash
# Interactive mode (recommended for beginners)
python main.py

# Command line mode
python main.py COMMAND [OPTIONS]

# Show version
python main.py --version
```

### Available Commands

| Command | Description | Category |
|---------|-------------|----------|
| `split` | Divide audio files into segments with precision timing | Audio Processing |
| `convert` | Convert between audio formats with quality preservation | Audio Processing |
| `channel` | Convert audio channels (mono ↔ stereo) with scientific algorithms | Audio Processing |
| `metadata` | Edit audio metadata tags with professional standards support | Metadata Management |
| `spectrogram` | Generate spectrograms optimized for LLM analysis | Analysis Visualization |
| `quality_settings` | Manage user quality configuration and preferences | Configuration |


### Quick Examples

```bash
# Basic audio splitting
python main.py split audio.wav -s "0:30-1:30:intro" "1:30-3:00:main"
```



### Professional Workflows

**Complete Podcast Production Workflow:**
```bash
# End-to-end podcast episode production
python main.py split raw_recording.wav -s "0:00-45:00:episode1" "47:00-90:00:episode2" --enhanced
python main.py metadata episode1.wav --title "Episode 1: Introduction" --artist "My Podcast Show"
python main.py convert episode1.wav --output episode1.mp3 --format mp3 --quality vbr_high
python main.py spectrogram episode1.mp3 --output episode1_spectrum.png --type mel --llm-optimized

```

**Professional Music Mastering Workflow:**
```bash
# Complete mastering workflow for music albums
python main.py convert ./master_tracks --output ./archive --format flac --quality high --batch --quality-validation
python main.py convert ./archive --output ./distribution --format mp3 --quality 320k --batch
python main.py metadata track01.mp3 --title "Track 1" --artist "Artist Name" --album "Album Title"
python main.py spectrogram track01.mp3 --enhanced --show-quality-metrics --type dual --output-dir ./analysis

```

### 🎬 Automated Professional Workflows

**Access from Interactive UI:** `python main.py` → Option 7: Professional Workflows

**🎙️ Podcast Production Workflow**
- Quick Mode: Fast MP3 conversion with basic metadata
- Standard Mode: Quality checks + complete metadata
- Professional Mode: Full validation + waveform visual

**🎵 Music Mastering Workflow**
- Quick Mastering: Solo MP3 rápido
- Standard Mastering: FLAC + MP3 con validación
- Professional Mastering: Análisis completo + validación studio
- Vinyl Preparation: Stereo FLAC para cutting master
- Broadcast Mastering: Mono MP3 para radio
- Mono Compatibility Test: Testing de compatibilidad mono

**📚 Audiobook Production Workflow**
- Quick: Fast M4A conversion
- Standard: Quality checks + metadata
- Professional: Full validation for distribution

Each workflow includes:
- ✅ Automatic format conversion
- ✅ Complete metadata management
- ✅ Quality validation (THD+N, SNR)
- ✅ Channel conversion (when applicable)
- ✅ Spectrogram generation (professional modes)

### Getting Help

- **General help:** `python main.py --help`
- **Command help:** `python main.py COMMAND --help`
- **Complete reference:** See [CLI Reference Guide](docs/CLI_REFERENCE.md)
- **Examples:** See [CLI Examples](docs/CLI_EXAMPLES.md)
<!-- CLI_SECTION_END -->

**Total files: 18 | Full functionality | Ready for distribution**
