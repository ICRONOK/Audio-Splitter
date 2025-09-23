# CLI Examples Guide - Audio Splitter Suite

Real-world examples and use cases for Audio Splitter Suite.

## Basic Operations


### Divide audio files into segments with precision timing

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



### Convert between audio formats with quality preservation

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



### Convert audio channels (mono ↔ stereo) with scientific algorithms

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



### Edit audio metadata tags with professional standards support

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



### Generate spectrograms optimized for LLM analysis

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



### Manage user quality configuration and preferences

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




## Professional Workflows


### Complete Podcast Production Workflow

**Use Case:** End-to-end podcast episode production

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

**Use Case:** Complete mastering workflow for music albums

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



## Common Use Cases

### Podcast Production
```bash
# Complete podcast workflow
python main.py split raw_recording.wav -s "0:00-45:00:episode1" "47:00-90:00:episode2"
python main.py metadata episode1.wav --title "Episode 1" --artist "My Podcast"
python main.py convert episode1.wav -o episode1.mp3 -f mp3 --quality vbr_high
```

### Music Album Processing
```bash
# Album mastering workflow
python main.py convert ./masters --output ./archive -f flac --quality high --batch
python main.py convert ./archive --output ./distribution -f mp3 --quality 320k --batch
```

### Audio Analysis
```bash
# Generate spectrograms for analysis
python main.py spectrogram audio.wav --enhanced --show-quality-metrics
python main.py spectrogram audio.wav --type dual --output-dir ./analysis
```

## Batch Processing

### Convert Entire Directory
```bash
# Recursive conversion
python main.py convert ./audio_collection --output ./converted -f mp3 --batch --recursive
```

### Batch Metadata Update
```bash
# Apply metadata to all files in directory
for file in *.mp3; do
    python main.py metadata "$file" --album "My Album" --artist "Artist Name"
done
```

## Quality Validation

### High-Quality Processing
```bash
# Professional quality validation
python main.py convert input.wav -o output.flac -f flac --quality-validation --show-metrics
python main.py split audio.wav -s "0:00-5:00:segment" --enhanced --quality-validation
```

### Configure Quality Settings
```bash
# Set studio quality profile
python main.py quality-settings set-profile studio

# Custom thresholds
python main.py quality-settings set-thresholds --thd -80.0 --snr 100.0
```

## Advanced Tips

### Time Format Examples
```bash
# Various time formats supported
python main.py split audio.wav -s "1:30-2:45:segment1"      # MM:SS
python main.py split audio.wav -s "1:30:45-2:15:30:segment2" # HH:MM:SS
python main.py split audio.wav -s "90.5-165.75:segment3"    # Seconds
```

### Output Organization
```bash
# Organized output structure
mkdir -p output/(Undefined, Undefined, Undefined)
python main.py convert masters/ -o output/archive -f flac --batch
python main.py convert output/archive -o output/distribution -f mp3 --batch
python main.py spectrogram output/archive/*.flac --output-dir output/analysis
```

## Troubleshooting Examples


### FileNotFoundError: audio file not found

**Problem:** Check file path and ensure file exists. Use absolute paths if needed.

**Solution:**
```bash
python main.py split "/full/path/to/audio.wav" -s "0:00-1:00:test"
```


### Invalid time format in segments

**Problem:** Use format MM:SS or HH:MM:SS for time ranges

**Solution:**
```bash
Correct: "1:30-2:45:segment" | Incorrect: "90-165:segment"
```


### PermissionError: cannot write to output directory

**Problem:** Check write permissions or use a different output directory

**Solution:**
```bash
python main.py split audio.wav -s "0:00-1:00:test" -o ~/Documents/audio_output
```


### Quality validation failed with poor metrics

**Problem:** Check source audio quality or adjust quality thresholds

**Solution:**
```bash
python main.py quality-settings set-profile basic  # Use less strict validation
```



---

*Need more help? Use `python main.py COMMAND --help` for detailed command documentation.*