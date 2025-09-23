# CLI Reference Guide - Audio Splitter Suite

> **Generated from cli_data.yaml** - Version 2.0.0  
> Last updated: 2025-09-23

## Overview

Professional audio processing CLI tool with modular architecture for audio splitting, format conversion, metadata editing, and spectrogram generation

## Quick Start

```bash
# Show version
python main.py --version

# Interactive mode (no arguments)
python main.py

# Command line mode
python main.py COMMAND [OPTIONS]
```

## Global Options

| Option | Description |
|--------|-------------|
| `--version, -v` | Show version information |


## Commands Reference


### `split` - Divide audio files into segments with precision timing

**Category:** Audio Processing

**Usage:**
```bash
python main.py split INPUT_FILE [OPTIONS]
```

**Arguments:**

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `INPUT_FILE` | string | ✓ | Path to audio file to split |



**Options:**

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--segments, -s` | string[] |  | Segments in format 'start-end:name' |
| `--output-dir, -o` | string | data/output | Output directory for segments |
| `--enhanced` | flag | False | Use enhanced splitter with DSP optimizations and cross-fade |
| `--fade-enabled` | flag | True | Enable cross-fade transitions (Hann window) |
| `--dither-enabled` | flag | True | Enable triangular dithering to reduce quantization noise |
| `--quality-validation` | flag | False | Validate quality of each segment |
| `--show-metrics` | flag | False | Show detailed quality metrics per segment |



**Examples:**

**Basic audio splitting:**
```bash
python main.py split audio.wav -s "0:30-1:30:intro" "1:30-3:00:main"
```
Split audio into two named segments

**Enhanced splitting with quality validation:**
```bash
python main.py split audio.wav -s "0:00-5:00:segment1" --enhanced --show-metrics
```
Use enhanced algorithms with DSP optimizations and quality metrics

**Podcast episode splitting:**
```bash
python main.py split recording.wav -s "0:00-45:00:episode" "47:00-90:00:bonus" --enhanced --quality-validation
```
Split podcast with quality validation and enhanced processing




**Workflows:**

**Complete Podcast Processing:**

Full workflow for podcast episode processing

1. Split recording into episodes:
   ```bash
   python main.py split recording.wav -s "0:00-45:00:episode1" "47:00-90:00:episode2"
   ```

2. Add metadata to episodes:
   ```bash
   python main.py metadata episode1.wav --title "Episode 1" --artist "My Podcast"
   ```

3. Convert to MP3 for distribution:
   ```bash
   python main.py convert episode1.wav --output episode1.mp3 --format mp3
   ```







---


### `convert` - Convert between audio formats with quality preservation

**Category:** Audio Processing

**Usage:**
```bash
python main.py convert INPUT [OPTIONS]
```

**Arguments:**

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `INPUT` | string | ✓ | Input file or directory path |



**Options:**

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--output, -o` | string |  | Output file or directory path |
| `--format, -f` | choice |  | Target output format |
| `--quality, -q` | string | high | Conversion quality level |
| `--batch` | flag | False | Enable batch conversion mode |
| `--recursive, -r` | flag | False | Search recursively in subdirectories |
| `--quality-validation` | flag | False | Enable scientific quality validation (THD+N, SNR) |
| `--quality-level` | choice | professional | Quality validation level |
| `--show-metrics` | flag | False | Show detailed quality metrics |



**Examples:**

**Convert single file:**
```bash
python main.py convert input.wav --output output.mp3 --format mp3
```
Convert WAV to MP3 with default quality

**High quality conversion with validation:**
```bash
python main.py convert input.wav --output output.flac --format flac --quality-validation --show-metrics
```
Convert to FLAC with quality validation and metrics

**Batch directory conversion:**
```bash
python main.py convert ./music --output ./converted --format mp3 --batch --recursive
```
Convert entire directory structure to MP3




**Workflows:**

**Album Mastering Workflow:**

Professional album mastering and distribution workflow

1. Convert masters to FLAC for archival:
   ```bash
   python main.py convert ./masters --output ./archive --format flac --quality high --batch
   ```

2. Create MP3 versions for distribution:
   ```bash
   python main.py convert ./archive --output ./distribution --format mp3 --quality 320k --batch
   ```

3. Validate quality of final masters:
   ```bash
   python main.py convert master_track.wav --output final.flac --format flac --quality-validation --show-metrics
   ```







---


### `channel` - Convert audio channels (mono ↔ stereo) with scientific algorithms

**Category:** Audio Processing

**Usage:**
```bash
python main.py channel INPUT [OPTIONS]
```

**Arguments:**

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `INPUT` | string | ✓ | Input file or directory path |



**Options:**

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--output, -o` | string |  | Output file or directory path |
| `--channels, -c` | choice |  | Target number of channels (1=mono, 2=stereo) |
| `--algorithm, -a` | choice | downmix_center | Mixing algorithm for stereo→mono conversion |
| `--batch` | flag | False | Enable batch conversion mode |
| `--recursive, -r` | flag | False | Search recursively in subdirectories |
| `--preserve-metadata` | flag | True | Preserve original metadata |
| `--analyze` | flag | False | Only analyze channel properties without converting |



**Examples:**

**Convert stereo to mono:**
```bash
python main.py channel input.wav --output output.wav --channels 1
```
Convert stereo file to mono using center downmix

**Analyze channel properties:**
```bash
python main.py channel input.wav --analyze
```
Analyze channel properties without conversion

**Batch convert directory to mono:**
```bash
python main.py channel ./stereo_files --output ./mono_files --channels 1 --batch --algorithm average
```
Convert entire directory to mono using average algorithm








---


### `metadata` - Edit audio metadata tags with professional standards support

**Category:** Metadata Management

**Usage:**
```bash
python main.py metadata FILE_PATH [OPTIONS]
```

**Arguments:**

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `FILE_PATH` | string | ✓ | Path to audio file for metadata editing |



**Options:**

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--title` | string |  | Set track title |
| `--artist` | string |  | Set artist name |
| `--album` | string |  | Set album name |
| `--genre` | string |  | Set music genre |
| `--year` | string |  | Set release year |



**Examples:**

**Set basic metadata tags:**
```bash
python main.py metadata song.mp3 --title "My Song" --artist "My Artist"
```
Set title and artist for a track

**Complete album metadata:**
```bash
python main.py metadata track.flac --title "Track 1" --artist "Artist" --album "Album" --genre "Rock" --year "2024"
```
Set complete metadata for album track








---


### `spectrogram` - Generate spectrograms optimized for LLM analysis

**Category:** Analysis Visualization

**Usage:**
```bash
python main.py spectrogram INPUT_FILE [OPTIONS]
```

**Arguments:**

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `INPUT_FILE` | string | ✓ | Path to audio file for spectrogram generation |



**Options:**

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--output, -o` | string |  | Output image file path |
| `--type, -t` | choice | mel | Type of spectrogram to generate |
| `--output-dir` | string |  | Output directory for multiple spectrogram types |
| `--mel-bins` | integer | 128 | Number of mel frequency bins |
| `--fmin` | float | 20.0 | Minimum frequency in Hz |
| `--fmax` | float | 8000.0 | Maximum frequency in Hz |
| `--duration` | float |  | Maximum duration in seconds |
| `--return-data` | flag | False | Return base64 image data for integration |
| `--enhanced` | flag | False | Use enhanced generator with scientific quality validation |
| `--quality-gates` | flag | False | Enable quality gates (temporal/frequency resolution) |
| `--llm-optimized` | flag | True | Optimize specifically for LLM analysis |
| `--show-quality-metrics` | flag | False | Show spectrogram quality metrics |



**Examples:**

**Generate mel spectrogram:**
```bash
python main.py spectrogram audio.wav --output spectrogram.png --type mel
```
Generate mel spectrogram optimized for LLM analysis

**Enhanced spectrogram with quality metrics:**
```bash
python main.py spectrogram audio.wav --enhanced --show-quality-metrics --type mel
```
Generate enhanced mel spectrogram with quality validation

**Generate dual spectrograms:**
```bash
python main.py spectrogram audio.wav --output-dir ./spectrograms --type dual
```
Generate both mel and linear spectrograms








---


### `quality_settings` - Manage user quality configuration and preferences

**Category:** Configuration

**Usage:**
```bash
python main.py quality-settings ACTION [OPTIONS]
```





**Examples:**

**Show current configuration:**
```bash
python main.py quality-settings show --detailed
```
Display detailed quality configuration

**Set studio quality profile:**
```bash
python main.py quality-settings set-profile studio
```
Activate studio quality profile with highest standards

**Set custom quality thresholds:**
```bash
python main.py quality-settings set-thresholds --thd -80.0 --snr 100.0
```
Set custom THD+N and SNR thresholds






**Subcommands:**

#### `quality_settings show`

Display current quality configuration



**Options:**
- `--detailed` - Show detailed configuration including thresholds



#### `quality_settings set_profile`

Set quality profile

**Arguments:**
- `PROFILE` (choice) - Quality profile to activate





#### `quality_settings set_thresholds`

Set custom quality thresholds



**Options:**
- `--thd` - THD+N threshold in dB (e.g., -60.0)
- `--snr` - SNR threshold in dB (e.g., 90.0)
- `--dynamic-range` - Minimum dynamic range in % (e.g., 95.0)



#### `quality_settings preferences`

Configure general preferences



**Options:**
- `--enable-validation` - Enable quality validation by default
- `--disable-validation` - Disable quality validation by default
- `--show-metrics` - Show metrics by default
- `--hide-metrics` - Hide metrics by default
- `--prefer-enhanced` - Prefer enhanced algorithms by default
- `--prefer-standard` - Prefer standard algorithms by default



#### `quality_settings reset`

Reset configuration to defaults



**Options:**
- `--confirm` - Confirm reset operation



#### `quality_settings export`

Export configuration to file

**Arguments:**
- `FILE` (string) - Output file path for configuration export





#### `quality_settings import`

Import configuration from file

**Arguments:**
- `FILE` (string) - Configuration file path to import








---



## Complete Workflows


### Complete Podcast Production Workflow

**Category:** Media Production

End-to-end podcast episode production

**Step 1:** Split raw recording into episodes
```bash
python main.py split raw_recording.wav -s "0:00-45:00:episode1" "47:00-90:00:episode2" --enhanced
```

**Step 2:** Add metadata to episodes
```bash
python main.py metadata episode1.wav --title "Episode 1: Introduction" --artist "My Podcast Show"
```

**Step 3:** Convert to MP3 for distribution
```bash
python main.py convert episode1.wav --output episode1.mp3 --format mp3 --quality vbr_high
```

**Step 4:** Generate spectrogram for analysis
```bash
python main.py spectrogram episode1.mp3 --output episode1_spectrum.png --type mel --llm-optimized
```



---


### Professional Music Mastering Workflow

**Category:** Music Production

Complete mastering workflow for music albums

**Step 1:** Convert masters to archival FLAC
```bash
python main.py convert ./master_tracks --output ./archive --format flac --quality high --batch --quality-validation
```

**Step 2:** Create distribution MP3 versions
```bash
python main.py convert ./archive --output ./distribution --format mp3 --quality 320k --batch
```

**Step 3:** Apply album metadata using templates
```bash
python main.py metadata track01.mp3 --title "Track 1" --artist "Artist Name" --album "Album Title"
```

**Step 4:** Generate spectrograms for quality analysis
```bash
python main.py spectrogram track01.mp3 --enhanced --show-quality-metrics --type dual --output-dir ./analysis
```



---



## Troubleshooting

### Common Errors


#### FileNotFoundError: audio file not found

**Solution:** Check file path and ensure file exists. Use absolute paths if needed.

**Example:**
```bash
python main.py split "/full/path/to/audio.wav" -s "0:00-1:00:test"
```


#### Invalid time format in segments

**Solution:** Use format MM:SS or HH:MM:SS for time ranges

**Example:**
```bash
Correct: "1:30-2:45:segment" | Incorrect: "90-165:segment"
```


#### PermissionError: cannot write to output directory

**Solution:** Check write permissions or use a different output directory

**Example:**
```bash
python main.py split audio.wav -s "0:00-1:00:test" -o ~/Documents/audio_output
```


#### Quality validation failed with poor metrics

**Solution:** Check source audio quality or adjust quality thresholds

**Example:**
```bash
python main.py quality-settings set-profile basic  # Use less strict validation
```



## Additional Help

For detailed examples of any command, use: python main.py COMMAND --help

See complete workflows in the CLI Reference Guide

Quality validation requires --enhanced flag for most commands

**Supported Formats:** Supported formats: WAV, MP3, FLAC, M4A (input), WAV/MP3/FLAC (output)

---

*Generated automatically from cli_data.yaml*