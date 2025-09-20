"""
Core Spectrogram Generator - LLM-Optimized Audio Visualization
Audio Signal Processing Engineer implementation with scientific accuracy
Integrates with CLI and Interactive interfaces
"""

import numpy as np
from typing import Dict, Any, Optional, Tuple, Union
from pathlib import Path
import json

# Scientific audio processing
import librosa
import soundfile as sf
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from scipy.signal import stft
from scipy.signal.windows import hann

# Image processing
from PIL import Image
import io
import base64

# Progress tracking
from audio_splitter.utils.progress_tracker import ProgressTracker

import logging
logger = logging.getLogger(__name__)


class SpectrogramGenerator:
    """
    Core spectrogram generation with scientific accuracy and LLM optimization
    Supports CLI, Interactive, and API usage
    """
    
    # LLM-optimized parameters from Audio Engineer specification
    DEFAULT_PARAMS = {
        'mel_scale': {
            'n_mels': 128,              # Perceptual frequency scale
            'fmin': 20.0,               # Minimum audible frequency
            'fmax': 8000.0,             # Upper perceptual range
            'hop_length': 512,          # 11.6ms temporal resolution @ 44.1kHz
            'n_fft': 2048,              # 46.4ms analysis window
            'window': 'hann',           # Minimal spectral leakage
            'power': 2.0                # Power spectrogram
        },
        'linear_scale': {
            'n_fft': 2048,              # Linear frequency resolution
            'hop_length': 512,          # Consistent temporal resolution
            'window': 'hann',           # Spectral accuracy
            'nperseg': 2048,            # STFT segment length
            'noverlap': 1536            # 75% overlap
        },
        'visual': {
            'figsize': (12.8, 5.12),   # 1024x512 pixels @ 80 DPI
            'dpi': 80,                  # LLM-optimal resolution
            'colormap': 'viridis',      # Perceptually uniform
            'dynamic_range_db': 80,     # Professional audio range
            'interpolation': 'bilinear', # Smooth visualization
            'save_format': 'png'        # Lossless for scientific accuracy
        }
    }
    
    def __init__(self, progress_callback=None):
        """
        Initialize spectrogram generator
        
        Args:
            progress_callback: Optional callback for progress updates
        """
        self.progress_callback = progress_callback
        self._progress_tracker = ProgressTracker(callback=progress_callback)
        
        # Set matplotlib backend for CLI compatibility
        plt.switch_backend('Agg')
        
        # Cache for performance optimization
        self._audio_cache = {}
        self._spec_cache = {}
    
    def generate_mel_spectrogram(self, input_file: Union[str, Path], 
                                output_file: Optional[Union[str, Path]] = None,
                                params: Optional[Dict[str, Any]] = None,
                                return_data: bool = False) -> Dict[str, Any]:
        """
        Generate Mel-scale spectrogram optimized for LLM perceptual analysis
        
        Args:
            input_file: Path to input audio file
            output_file: Optional output image path
            params: Custom parameters for Mel spectrogram
            return_data: Whether to return image data in result
            
        Returns:
            Generation results and metrics
        """
        self._progress_tracker.start("Generating Mel spectrogram")
        
        try:
            # Validate input
            file_path = self._validate_input_file(input_file)
            
            # Load audio with scientific accuracy
            self._progress_tracker.update(10, "Loading audio file")
            y, sr = self._load_audio(file_path)
            
            # Get Mel parameters
            mel_params = self.DEFAULT_PARAMS['mel_scale'].copy()
            if params:
                mel_params.update(params)
            
            # Generate Mel spectrogram
            self._progress_tracker.update(30, "Computing Mel spectrogram")
            mel_spec = librosa.feature.melspectrogram(
                y=y, sr=sr,
                n_mels=mel_params['n_mels'],
                fmin=mel_params['fmin'],
                fmax=mel_params['fmax'],
                hop_length=mel_params['hop_length'],
                n_fft=mel_params['n_fft'],
                window=mel_params['window'],
                power=mel_params['power']
            )
            
            # Convert to log scale (dB) for perceptual accuracy
            mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)
            
            # Create LLM-optimized visualization
            self._progress_tracker.update(60, "Creating visualization")
            image_data, image_path = self._create_spectrogram_image(
                mel_spec_db, sr, mel_params['hop_length'],
                'Mel Frequency (Hz)', mel_params['fmin'], mel_params['fmax'],
                output_file, "Mel Spectrogram"
            )
            
            # Calculate quality metrics
            self._progress_tracker.update(80, "Calculating metrics")
            metrics = self._calculate_quality_metrics(
                mel_spec_db, sr, mel_params, y
            )
            
            self._progress_tracker.complete("Mel spectrogram generated")
            
            result = {
                'status': 'success',
                'spectrogram_type': 'mel',
                'input_file': str(file_path),
                'output_file': str(image_path) if image_path else None,
                'sample_rate': sr,
                'duration_seconds': len(y) / sr,
                'parameters': mel_params,
                'quality_metrics': metrics
            }
            
            if return_data:
                result['image_data'] = image_data
            
            return result
            
        except Exception as e:
            self._progress_tracker.error(f"Mel spectrogram generation failed: {e}")
            raise e
    
    def generate_linear_spectrogram(self, input_file: Union[str, Path],
                                   output_file: Optional[Union[str, Path]] = None,
                                   params: Optional[Dict[str, Any]] = None,
                                   return_data: bool = False) -> Dict[str, Any]:
        """
        Generate linear-scale STFT spectrogram for technical analysis
        
        Args:
            input_file: Path to input audio file
            output_file: Optional output image path
            params: Custom parameters for linear spectrogram
            return_data: Whether to return image data in result
            
        Returns:
            Generation results and metrics
        """
        self._progress_tracker.start("Generating linear spectrogram")
        
        try:
            # Validate input
            file_path = self._validate_input_file(input_file)
            
            # Load audio
            self._progress_tracker.update(10, "Loading audio file")
            y, sr = self._load_audio(file_path)
            
            # Get linear parameters
            linear_params = self.DEFAULT_PARAMS['linear_scale'].copy()
            if params:
                linear_params.update(params)
            
            # Generate STFT
            self._progress_tracker.update(30, "Computing STFT")
            f, t, Zxx = stft(
                y, fs=sr,
                window=linear_params['window'],
                nperseg=linear_params['nperseg'],
                noverlap=linear_params['noverlap'],
                nfft=linear_params['n_fft']
            )
            
            # Convert to magnitude and dB
            magnitude = np.abs(Zxx)
            magnitude_db = 20 * np.log10(magnitude + 1e-10)  # Avoid log(0)
            
            # Create visualization
            self._progress_tracker.update(60, "Creating visualization")
            image_data, image_path = self._create_spectrogram_image(
                magnitude_db, sr, linear_params['n_fft']//4,
                'Frequency (Hz)', 0, sr//2,
                output_file, "Linear Spectrogram (STFT)"
            )
            
            # Calculate metrics
            self._progress_tracker.update(80, "Calculating metrics")
            metrics = self._calculate_quality_metrics(
                magnitude_db, sr, linear_params, y
            )
            
            self._progress_tracker.complete("Linear spectrogram generated")
            
            result = {
                'status': 'success',
                'spectrogram_type': 'linear',
                'input_file': str(file_path),
                'output_file': str(image_path) if image_path else None,
                'sample_rate': sr,
                'duration_seconds': len(y) / sr,
                'parameters': linear_params,
                'quality_metrics': metrics
            }
            
            if return_data:
                result['image_data'] = image_data
            
            return result
            
        except Exception as e:
            self._progress_tracker.error(f"Linear spectrogram generation failed: {e}")
            raise e
    
    def generate_cqt_spectrogram(self, input_file: Union[str, Path],
                                output_file: Optional[Union[str, Path]] = None,
                                params: Optional[Dict[str, Any]] = None,
                                return_data: bool = False) -> Dict[str, Any]:
        """
        Generate Constant-Q Transform spectrogram for musical analysis
        
        Args:
            input_file: Path to input audio file
            output_file: Optional output image path
            params: Custom parameters for CQT
            return_data: Whether to return image data in result
            
        Returns:
            Generation results and metrics
        """
        self._progress_tracker.start("Generating CQT spectrogram")
        
        try:
            # Validate input
            file_path = self._validate_input_file(input_file)
            
            # Load audio
            self._progress_tracker.update(10, "Loading audio file")
            y, sr = self._load_audio(file_path)
            
            # CQT parameters for musical analysis
            fmin = params.get('fmin', librosa.note_to_hz('C1'))  # ~32.7 Hz
            n_bins = params.get('n_bins', 84)  # 7 octaves * 12 semitones
            bins_per_octave = params.get('bins_per_octave', 12)
            hop_length = params.get('hop_length', 512)
            
            # Generate CQT
            self._progress_tracker.update(30, "Computing CQT")
            cqt = np.abs(librosa.cqt(
                y, sr=sr,
                fmin=fmin,
                n_bins=n_bins,
                bins_per_octave=bins_per_octave,
                hop_length=hop_length
            ))
            
            # Convert to dB
            cqt_db = librosa.amplitude_to_db(cqt, ref=np.max)
            
            # Create visualization with musical context
            self._progress_tracker.update(60, "Creating musical visualization")
            image_data, image_path = self._create_spectrogram_image(
                cqt_db, sr, hop_length,
                'Musical Note', fmin, fmin * (2 ** (n_bins / bins_per_octave)),
                output_file, "Constant-Q Transform (Musical)"
            )
            
            # Calculate metrics
            self._progress_tracker.update(80, "Calculating metrics")
            cqt_params = {'hop_length': hop_length, 'n_fft': 2048}
            metrics = self._calculate_quality_metrics(cqt_db, sr, cqt_params, y)
            metrics['musical_analysis'] = {
                'n_bins': n_bins,
                'bins_per_octave': bins_per_octave,
                'fmin_hz': fmin,
                'frequency_range_octaves': n_bins / bins_per_octave
            }
            
            self._progress_tracker.complete("CQT spectrogram generated")
            
            result = {
                'status': 'success',
                'spectrogram_type': 'cqt',
                'input_file': str(file_path),
                'output_file': str(image_path) if image_path else None,
                'sample_rate': sr,
                'duration_seconds': len(y) / sr,
                'parameters': {'fmin': fmin, 'n_bins': n_bins, 'bins_per_octave': bins_per_octave},
                'quality_metrics': metrics
            }
            
            if return_data:
                result['image_data'] = image_data
            
            return result
            
        except Exception as e:
            self._progress_tracker.error(f"CQT spectrogram generation failed: {e}")
            raise e
    
    def batch_generate_spectrograms(self, input_files: list,
                                   output_dir: Union[str, Path],
                                   spectrogram_types: list = ['mel'],
                                   params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate spectrograms for multiple files
        
        Args:
            input_files: List of input audio files
            output_dir: Output directory for spectrograms
            spectrogram_types: Types to generate ('mel', 'linear', 'cqt')
            params: Custom parameters
            
        Returns:
            Batch processing results
        """
        self._progress_tracker.start(f"Batch generating spectrograms for {len(input_files)} files")
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        results = {
            'status': 'success',
            'total_files': len(input_files),
            'successful': 0,
            'failed': 0,
            'results': []
        }
        
        for i, input_file in enumerate(input_files):
            try:
                file_progress = int((i / len(input_files)) * 100)
                self._progress_tracker.update(file_progress, f"Processing {i+1}/{len(input_files)}")
                
                file_path = Path(input_file)
                file_results = []
                
                for spec_type in spectrogram_types:
                    output_file = output_path / f"{file_path.stem}_{spec_type}_spectrogram.png"
                    
                    if spec_type == 'mel':
                        result = self.generate_mel_spectrogram(input_file, output_file, params)
                    elif spec_type == 'linear':
                        result = self.generate_linear_spectrogram(input_file, output_file, params)
                    elif spec_type == 'cqt':
                        result = self.generate_cqt_spectrogram(input_file, output_file, params)
                    else:
                        continue
                    
                    file_results.append(result)
                
                results['results'].append({
                    'input_file': str(input_file),
                    'status': 'success',
                    'spectrograms': file_results
                })
                results['successful'] += 1
                
            except Exception as e:
                results['results'].append({
                    'input_file': str(input_file),
                    'status': 'error',
                    'error': str(e)
                })
                results['failed'] += 1
                logger.error(f"Failed to process {input_file}: {e}")
        
        self._progress_tracker.complete("Batch spectrogram generation complete")
        return results
    
    def _validate_input_file(self, input_file: Union[str, Path]) -> Path:
        """Validate input audio file"""
        file_path = Path(input_file)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_file}")
        
        if not file_path.is_file():
            raise ValueError(f"Input path is not a file: {input_file}")
        
        # Check file extension
        valid_extensions = {'.wav', '.mp3', '.flac', '.aac', '.ogg', '.m4a'}
        if file_path.suffix.lower() not in valid_extensions:
            raise ValueError(f"Unsupported audio format: {file_path.suffix}")
        
        return file_path
    
    def _load_audio(self, file_path: Path) -> Tuple[np.ndarray, int]:
        """Load audio with caching and error handling"""
        cache_key = str(file_path)
        
        if cache_key in self._audio_cache:
            return self._audio_cache[cache_key]
        
        try:
            # Load with librosa for scientific accuracy
            y, sr = librosa.load(str(file_path), sr=None, mono=False)
            
            # Convert stereo to mono if needed
            if y.ndim > 1:
                y = librosa.to_mono(y)
            
            # Cache for reuse
            self._audio_cache[cache_key] = (y, sr)
            
            return y, sr
            
        except Exception as e:
            raise ValueError(f"Failed to load audio file {file_path}: {e}")
    
    def _create_spectrogram_image(self, spec_db: np.ndarray, sr: int, hop_length: int,
                                 ylabel: str, fmin: float, fmax: float,
                                 output_file: Optional[Path], title: str) -> Tuple[Optional[str], Optional[Path]]:
        """Create LLM-optimized spectrogram image"""
        
        # Get visual parameters
        visual_params = self.DEFAULT_PARAMS['visual']
        
        # Create figure with optimal dimensions
        fig, ax = plt.subplots(
            figsize=visual_params['figsize'],
            dpi=visual_params['dpi']
        )
        
        # Calculate time axis
        time_frames = spec_db.shape[1]
        time_axis = librosa.frames_to_time(
            np.arange(time_frames), sr=sr, hop_length=hop_length
        )
        
        # Create spectrogram visualization
        img = ax.imshow(
            spec_db,
            aspect='auto',
            origin='lower',
            cmap=visual_params['colormap'],
            vmin=np.max(spec_db) - visual_params['dynamic_range_db'],
            vmax=np.max(spec_db),
            interpolation=visual_params['interpolation'],
            extent=[time_axis[0], time_axis[-1], fmin, fmax]
        )
        
        # Configure axes for LLM comprehension
        ax.set_xlabel('Time (s)', fontsize=12, fontweight='bold')
        ax.set_ylabel(ylabel, fontsize=12, fontweight='bold')
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        # Add colorbar with dB scale
        cbar = plt.colorbar(img, ax=ax, format='%+2.0f dB')
        cbar.set_label('Magnitude (dB)', fontsize=10)
        
        # Optimize layout
        plt.tight_layout()
        
        # Save and/or return data
        image_data = None
        image_path = None
        
        if output_file:
            # Save to file
            image_path = Path(output_file)
            image_path.parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(
                str(image_path),
                format=visual_params['save_format'],
                dpi=visual_params['dpi'],
                bbox_inches='tight',
                facecolor='white',
                edgecolor='none'
            )
        else:
            # Return base64 data
            buffer = io.BytesIO()
            plt.savefig(
                buffer, format='png',
                dpi=visual_params['dpi'],
                bbox_inches='tight',
                facecolor='white',
                edgecolor='none'
            )
            buffer.seek(0)
            image_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
            buffer.close()
        
        # Cleanup
        plt.close(fig)
        
        return image_data, image_path
    
    def _calculate_quality_metrics(self, spec_db: np.ndarray, sr: int,
                                  params: Dict[str, Any], audio: np.ndarray) -> Dict[str, Any]:
        """Calculate comprehensive quality metrics"""
        
        hop_length = params.get('hop_length', 512)
        n_fft = params.get('n_fft', 2048)
        
        # Basic spectrogram metrics
        metrics = {
            'dynamic_range_db': np.max(spec_db) - np.min(spec_db),
            'frequency_resolution_hz': sr / n_fft,
            'temporal_resolution_ms': (hop_length / sr) * 1000,
            'spectral_shape': spec_db.shape,
            'max_magnitude_db': float(np.max(spec_db)),
            'min_magnitude_db': float(np.min(spec_db)),
            'mean_magnitude_db': float(np.mean(spec_db)),
            'std_magnitude_db': float(np.std(spec_db))
        }
        
        # Visual quality metrics for LLM
        metrics.update({
            'contrast_ratio': self._calculate_contrast_ratio(spec_db),
            'pattern_clarity_score': self._calculate_pattern_clarity(spec_db),
            'visual_complexity_score': self._calculate_visual_complexity(spec_db)
        })
        
        # Audio source metrics
        metrics.update({
            'audio_duration_seconds': len(audio) / sr,
            'audio_sample_rate': sr,
            'audio_rms_db': float(20 * np.log10(np.sqrt(np.mean(audio**2)) + 1e-10)),
            'audio_peak_db': float(20 * np.log10(np.max(np.abs(audio)) + 1e-10))
        })
        
        return metrics
    
    def _calculate_contrast_ratio(self, spec_db: np.ndarray) -> float:
        """Calculate image contrast ratio for LLM analysis"""
        max_val = np.max(spec_db)
        min_val = np.min(spec_db)
        if max_val + min_val == 0:
            return 0.0
        return float((max_val - min_val) / (max_val + min_val))
    
    def _calculate_pattern_clarity(self, spec_db: np.ndarray) -> float:
        """Calculate visual pattern clarity score"""
        grad_x = np.gradient(spec_db, axis=1)
        grad_y = np.gradient(spec_db, axis=0)
        gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
        
        clarity_score = np.mean(gradient_magnitude) / (np.max(spec_db) - np.min(spec_db))
        return float(min(clarity_score, 1.0))
    
    def _calculate_visual_complexity(self, spec_db: np.ndarray) -> float:
        """Calculate visual complexity for LLM processing difficulty assessment"""
        # Use entropy as complexity measure
        from scipy.stats import entropy
        
        # Flatten and normalize
        flat_spec = spec_db.flatten()
        hist, _ = np.histogram(flat_spec, bins=50, density=True)
        complexity = entropy(hist + 1e-10)  # Add small value to avoid log(0)
        
        # Normalize to 0-1 scale (approximate)
        return float(min(complexity / 4.0, 1.0))
    
    def clear_cache(self):
        """Clear audio and spectrogram caches"""
        self._audio_cache.clear()
        self._spec_cache.clear()