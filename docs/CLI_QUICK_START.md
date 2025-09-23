# Quick Start Guide - Audio Splitter Suite

Get started with Audio Splitter Suite in 5 minutes.

## Installation Check

```bash
# Verify installation
python main.py --version
# Should output: Audio Splitter Suite 2.0.0
```

## Choose Your Mode

### Interactive Mode (Recommended for Beginners)
```bash
python main.py
```
Follow the menu prompts for guided operation.

### Command Line Mode (For Advanced Users)
```bash
python main.py COMMAND [OPTIONS]
```

## Essential Commands

### 1. Divide audio files into segments with precision timing

```bash
python main.py split audio.wav -s "0:30-1:30:intro" "1:30-3:00:main"
```

### 2. Convert between audio formats with quality preservation

```bash
python main.py convert INPUT [OPTIONS]
```

### 3. Convert audio channels (mono ↔ stereo) with scientific algorithms

```bash
python main.py channel INPUT [OPTIONS]
```

### 4. Edit audio metadata tags with professional standards support

```bash
python main.py metadata FILE_PATH [OPTIONS]
```



## Your First Workflow

Let's process an audio file step by step:

```bash
# 1. Split audio into segments
python main.py split my_audio.wav -s "0:00-2:00:intro" "2:00-5:00:main"

# 2. Convert to different format
python main.py convert intro.wav -o intro.mp3 -f mp3

# 3. Add metadata
python main.py metadata intro.mp3 --title "Introduction" --artist "My Name"

# 4. Generate spectrogram for analysis
python main.py spectrogram intro.mp3 -o intro_spectrum.png
```

## Next Steps

- Read the [Complete CLI Reference](CLI_REFERENCE.md)
- Explore [Advanced Examples](CLI_EXAMPLES.md)
- Configure [Quality Settings](python main.py quality-settings show)

## Getting Help

```bash
# General help
python main.py --help

# Command-specific help
python main.py split --help
python main.py convert --help
```

Happy audio processing! 🎵