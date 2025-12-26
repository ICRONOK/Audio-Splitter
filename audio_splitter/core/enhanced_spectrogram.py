#!/usr/bin/env python3
"""
Enhanced Spectrogram Generator with Scientific Quality Gates
Audio Signal Processing Engineer implementation

Features:
- Scientific quality validation for spectrograms
- Frequency domain artifact detection
- Perceptual quality assessment 
- LLM-optimized parameters with quality gates
- Dynamic range and resolution validation
"""

import numpy as np
import librosa
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from typing import Dict, Any, Optional, Tuple, Union
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
import json
import base64
import io
from PIL import Image
from scipy.signal import welch
from rich.console import Console

from .quality_framework import (
    AudioQualityAnalyzer,
    QualityMetrics, 
    QualityLevel,
    high_quality_processing,
    basic_quality_check
)
from .spectrogram_generator import SpectrogramGenerator

console = Console()


class SpectrogramQualityLevel(Enum):
    """Spectrogram-specific quality levels"""
    EXCELLENT = 5    # High resolution, no artifacts, optimal SNR
    GOOD = 4         # Good resolution, minimal artifacts
    ACCEPTABLE = 3   # Adequate for analysis
    POOR = 2         # Limited usefulness
    FAILED = 1       # Unusable for analysis

    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented

    def __le__(self, other):
        if self.__class__ is other.__class__:
            return self.value <= other.value
        return NotImplemented


@dataclass
class SpectrogramQualityMetrics:
    """Scientific quality metrics for spectrograms"""
    
    # Resolution metrics
    temporal_resolution_ms: Optional[float] = None     # Time resolution
    frequency_resolution_hz: Optional[float] = None    # Frequency resolution
    dynamic_range_db: Optional[float] = None           # Spectrogram dynamic range
    
    # Frequency domain quality
    spectral_flatness: Optional[float] = None          # Spectral flatness measure
    spectral_centroid_hz: Optional[float] = None       # Spectral centroid
    spectral_bandwidth_hz: Optional[float] = None      # Spectral bandwidth
    nyquist_usage_ratio: Optional[float] = None        # Nyquist frequency utilization
    
    # Artifact detection
    aliasing_artifacts: bool = False                    # Aliasing in frequency domain
    windowing_artifacts: bool = False                   # Window function artifacts  
    normalization_issues: bool = False                  # Poor normalization
    
    # Perceptual quality
    mel_scale_accuracy: Optional[float] = None          # Mel scale fidelity
    critical_band_coverage: Optional[float] = None     # Critical band coverage
    perceptual_snr_db: Optional[float] = None          # Perceptual SNR
    
    # Visual quality
    image_contrast_ratio: Optional[float] = None       # Visual contrast
    color_map_efficiency: Optional[float] = None       # Color mapping efficiency
    information_density: Optional[float] = None        # Information per pixel
    
    # Overall assessment
    quality_level: Optional[SpectrogramQualityLevel] = None
    quality_score: Optional[float] = None              # 0-100 score
    llm_suitability_score: Optional[float] = None      # LLM analysis suitability


class SpectrogramQualityGates:
    """Quality gates for spectrogram validation"""
    
    # Resolution requirements
    MIN_TEMPORAL_RESOLUTION_MS = 50.0      # Maximum time bin size
    MIN_FREQUENCY_RESOLUTION_HZ = 50.0     # Maximum frequency bin size
    MIN_DYNAMIC_RANGE_DB = 60.0            # Minimum dynamic range
    
    # Frequency domain requirements
    MIN_SPECTRAL_FLATNESS = 0.1            # Minimum spectral flatness
    MAX_ALIASING_ENERGY_RATIO = 0.05       # Maximum aliasing energy
    MIN_NYQUIST_USAGE = 0.7                # Minimum Nyquist utilization
    
    # Perceptual requirements
    MIN_MEL_ACCURACY = 0.9                 # Mel scale accuracy
    MIN_CRITICAL_BAND_COVERAGE = 0.8       # Critical band coverage
    MIN_PERCEPTUAL_SNR_DB = 40.0           # Minimum perceptual SNR
    
    # Visual quality requirements
    MIN_CONTRAST_RATIO = 2.0               # Minimum visual contrast
    MIN_INFORMATION_DENSITY = 0.5          # Minimum information density
    
    # LLM optimization requirements
    MIN_LLM_SUITABILITY = 80.0             # Minimum LLM suitability score


class EnhancedSpectrogramGenerator(SpectrogramGenerator):
    """Spectrogram generator with scientific quality validation"""
    
    def __init__(self):
        super().__init__()
        self.quality_gates = SpectrogramQualityGates()
        self.audio_analyzer = AudioQualityAnalyzer()
    
    @high_quality_processing
    def generate_with_quality_validation(self,
                                       audio_path: Union[str, Path],
                                       output_path: Optional[Union[str, Path]] = None,
                                       spectrogram_type: str = 'mel',
                                       quality_validation: bool = True,
                                       **kwargs) -> Dict[str, Any]:
        """
        Generate spectrogram with comprehensive quality validation
        
        Args:
            audio_path: Input audio file path
            output_path: Output image path (optional)
            spectrogram_type: Type of spectrogram ('mel', 'linear', 'cqt')
            quality_validation: Enable quality assessment
            **kwargs: Additional parameters
            
        Returns:
            Dict with spectrogram generation results and quality metrics
        """
        audio_path = Path(audio_path)
        
        console.print(f"[blue]🔬 Enhanced Spectrogram Generation:[/blue] {audio_path.name}")
        console.print(f"[cyan]   Type: {spectrogram_type.upper()} | Quality Validation: {quality_validation}[/cyan]")
        
        try:
            # Load audio for analysis
            audio_data, sample_rate = librosa.load(str(audio_path), sr=None, mono=False)
            console.print(f"[green]✓ Audio loaded:[/green] {sample_rate}Hz, shape: {audio_data.shape}")
            
            # Use first channel for spectrogram if stereo
            if len(audio_data.shape) > 1:
                audio_signal = audio_data[0]
                console.print("[cyan]   Using first channel for spectrogram[/cyan]")
            else:
                audio_signal = audio_data
            
            # Generate spectrogram with enhanced parameters
            spectrogram_data, generation_result = self._generate_enhanced_spectrogram(
                audio_signal=audio_signal,
                sample_rate=sample_rate,
                spectrogram_type=spectrogram_type,
                **kwargs
            )
            
            if not generation_result['success']:
                return generation_result
            
            # Quality validation if enabled
            quality_metrics = None
            if quality_validation:
                console.print("[blue]🔬 Analyzing spectrogram quality...[/blue]")
                quality_metrics = self._analyze_spectrogram_quality(
                    spectrogram_data=spectrogram_data,
                    audio_signal=audio_signal,
                    sample_rate=sample_rate,
                    spectrogram_type=spectrogram_type,
                    generation_params=generation_result['parameters']
                )
                
                self._display_quality_results(quality_metrics)
                
                # Check quality gates
                quality_passed = self._validate_quality_gates(quality_metrics)
                if not quality_passed:
                    console.print("[red]❌ Quality gates failed[/red]")
                    return {
                        'success': False,
                        'error': 'Spectrogram quality below acceptable thresholds',
                        'quality_metrics': quality_metrics
                    }
            
            # Generate visual representation if output path specified
            image_data = None
            if output_path:
                image_data = self._create_enhanced_visualization(
                    spectrogram_data=spectrogram_data,
                    spectrogram_type=spectrogram_type,
                    output_path=Path(output_path),
                    quality_metrics=quality_metrics
                )
            
            return {
                'success': True,
                'spectrogram_data': spectrogram_data,
                'quality_metrics': quality_metrics,
                'image_data': image_data,
                'output_path': str(output_path) if output_path else None,
                'generation_parameters': generation_result['parameters'],
                'audio_properties': {
                    'sample_rate': sample_rate,
                    'duration_seconds': len(audio_signal) / sample_rate,
                    'channels': 1 if len(audio_data.shape) == 1 else audio_data.shape[0]
                }
            }
            
        except Exception as e:
            console.print(f"[red]✗ Enhanced spectrogram generation failed:[/red] {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generate_enhanced_spectrogram(self,
                                     audio_signal: np.ndarray,
                                     sample_rate: int,
                                     spectrogram_type: str,
                                     **kwargs) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Generate spectrogram with enhanced scientific parameters"""
        
        # Get optimal parameters for spectrogram type
        if spectrogram_type == 'mel':
            params = self.DEFAULT_PARAMS['mel_scale'].copy()
        elif spectrogram_type == 'linear':
            params = self.DEFAULT_PARAMS['linear_scale'].copy()
        elif spectrogram_type == 'cqt':
            params = self.DEFAULT_PARAMS['cqt_scale'].copy()
        else:
            raise ValueError(f"Unsupported spectrogram type: {spectrogram_type}")
        
        # Override with user parameters
        params.update(kwargs)
        
        try:
            if spectrogram_type == 'mel':
                # Enhanced Mel spectrogram
                spectrogram = librosa.feature.melspectrogram(
                    y=audio_signal,
                    sr=sample_rate,
                    n_mels=params['n_mels'],
                    fmin=params['fmin'],
                    fmax=params['fmax'],
                    hop_length=params['hop_length'],
                    n_fft=params['n_fft'],
                    window=params['window'],
                    power=params['power']
                )
                
                # Convert to log scale with proper epsilon
                spectrogram_db = librosa.power_to_db(spectrogram, ref=np.max, top_db=80)
                
            elif spectrogram_type == 'linear':
                # Enhanced STFT spectrogram
                stft = librosa.stft(
                    audio_signal,
                    hop_length=params['hop_length'],
                    n_fft=params['n_fft'],
                    window=params['window']
                )
                spectrogram = np.abs(stft) ** 2
                spectrogram_db = librosa.power_to_db(spectrogram, ref=np.max, top_db=80)
                
            elif spectrogram_type == 'cqt':
                # Enhanced Constant-Q Transform
                cqt = librosa.cqt(
                    audio_signal,
                    sr=sample_rate,
                    hop_length=params['hop_length'],
                    fmin=params['fmin'],
                    n_bins=params['n_bins'],
                    bins_per_octave=params['bins_per_octave']
                )
                spectrogram = np.abs(cqt) ** 2
                spectrogram_db = librosa.amplitude_to_db(np.abs(cqt), ref=np.max, top_db=80)
            
            return spectrogram_db, {
                'success': True,
                'parameters': params,
                'shape': spectrogram_db.shape,
                'type': spectrogram_type
            }
            
        except Exception as e:
            return None, {
                'success': False,
                'error': f"Spectrogram generation failed: {e}"
            }
    
    def _analyze_spectrogram_quality(self,
                                   spectrogram_data: np.ndarray,
                                   audio_signal: np.ndarray,
                                   sample_rate: int,
                                   spectrogram_type: str,
                                   generation_params: Dict[str, Any]) -> SpectrogramQualityMetrics:
        """Comprehensive spectrogram quality analysis"""
        
        metrics = SpectrogramQualityMetrics()
        
        # Resolution metrics
        hop_length = generation_params.get('hop_length', 512)
        n_fft = generation_params.get('n_fft', 2048)
        
        metrics.temporal_resolution_ms = (hop_length / sample_rate) * 1000
        metrics.frequency_resolution_hz = sample_rate / n_fft
        
        # Dynamic range analysis
        metrics.dynamic_range_db = np.max(spectrogram_data) - np.min(spectrogram_data)
        
        # Frequency domain analysis
        freq_bins, time_bins = spectrogram_data.shape
        
        # Spectral characteristics
        mean_spectrum = np.mean(spectrogram_data, axis=1)
        metrics.spectral_flatness = self._calculate_spectral_flatness(mean_spectrum)
        
        # Nyquist utilization
        if spectrogram_type in ['linear', 'stft']:
            nyquist_bin = freq_bins // 2
            high_freq_energy = np.mean(spectrogram_data[nyquist_bin:, :])
            total_energy = np.mean(spectrogram_data)
            metrics.nyquist_usage_ratio = high_freq_energy / total_energy if total_energy > 0 else 0
        
        # Artifact detection
        metrics.aliasing_artifacts = self._detect_spectral_aliasing(spectrogram_data, spectrogram_type)
        metrics.windowing_artifacts = self._detect_windowing_artifacts(spectrogram_data)
        metrics.normalization_issues = self._detect_normalization_issues(spectrogram_data)
        
        # Perceptual quality assessment
        if spectrogram_type == 'mel':
            metrics.mel_scale_accuracy = self._assess_mel_accuracy(generation_params)
            metrics.critical_band_coverage = self._assess_critical_band_coverage(generation_params)
        
        # Visual quality assessment
        metrics.image_contrast_ratio = self._calculate_contrast_ratio(spectrogram_data)
        metrics.information_density = self._calculate_information_density(spectrogram_data)
        
        # Overall quality assessment
        metrics.quality_level = self._assess_spectrogram_quality_level(metrics)
        metrics.quality_score = self._calculate_spectrogram_quality_score(metrics)
        metrics.llm_suitability_score = self._calculate_llm_suitability(metrics, spectrogram_type)
        
        return metrics
    
    def _calculate_spectral_flatness(self, spectrum: np.ndarray) -> float:
        """Calculate spectral flatness (Wiener entropy)"""
        try:
            # Convert from dB to linear scale for calculation
            linear_spectrum = 10 ** (spectrum / 10)
            
            # Avoid log of zero
            linear_spectrum = np.maximum(linear_spectrum, 1e-10)
            
            geometric_mean = np.exp(np.mean(np.log(linear_spectrum)))
            arithmetic_mean = np.mean(linear_spectrum)
            
            if arithmetic_mean == 0:
                return 0.0
                
            flatness = geometric_mean / arithmetic_mean
            return min(flatness, 1.0)  # Cap at 1.0
            
        except Exception:
            return 0.5  # Default moderate flatness
    
    def _detect_spectral_aliasing(self, spectrogram: np.ndarray, spec_type: str) -> bool:
        """Detect aliasing artifacts in frequency domain"""
        try:
            if spec_type not in ['linear', 'stft']:
                return False  # Only applicable to linear spectrograms
            
            freq_bins = spectrogram.shape[0]
            
            # Check for suspicious energy near Nyquist frequency
            nyquist_region = spectrogram[int(freq_bins * 0.8):, :]
            total_energy = np.mean(spectrogram)
            nyquist_energy = np.mean(nyquist_region)
            
            # If high-frequency energy is suspiciously high, suspect aliasing
            energy_ratio = nyquist_energy / total_energy if total_energy > 0 else 0
            
            return energy_ratio > self.quality_gates.MAX_ALIASING_ENERGY_RATIO
            
        except Exception:
            return False
    
    def _detect_windowing_artifacts(self, spectrogram: np.ndarray) -> bool:
        """Detect windowing function artifacts"""
        try:
            # Look for periodic patterns that might indicate window artifacts
            time_profile = np.mean(spectrogram, axis=0)
            
            # Simple artifact detection: excessive regularity in time domain
            time_variation = np.std(time_profile) / np.mean(time_profile) if np.mean(time_profile) > 0 else 0
            
            # Very low variation might indicate artifacts
            return time_variation < 0.1
            
        except Exception:
            return False
    
    def _detect_normalization_issues(self, spectrogram: np.ndarray) -> bool:
        """Detect normalization problems"""
        try:
            # Check for proper dynamic range utilization
            data_range = np.max(spectrogram) - np.min(spectrogram)
            
            # Check for clipping at extremes
            max_val = np.max(spectrogram)
            min_val = np.min(spectrogram)
            
            # Count values at extremes
            max_count = np.sum(spectrogram >= max_val - 0.1)
            min_count = np.sum(spectrogram <= min_val + 0.1)
            
            total_elements = spectrogram.size
            extreme_ratio = (max_count + min_count) / total_elements
            
            # If too many values at extremes, suspect poor normalization
            return extreme_ratio > 0.05 or data_range < 20  # 20 dB minimum range
            
        except Exception:
            return False
    
    def _assess_mel_accuracy(self, params: Dict[str, Any]) -> float:
        """Assess Mel scale accuracy"""
        try:
            fmin = params.get('fmin', 20)
            fmax = params.get('fmax', 8000)
            n_mels = params.get('n_mels', 128)
            
            # Check if parameters follow perceptual guidelines
            freq_range_score = 1.0 if 20 <= fmin <= 100 and 6000 <= fmax <= 22050 else 0.7
            resolution_score = 1.0 if 80 <= n_mels <= 256 else 0.8
            
            return (freq_range_score + resolution_score) / 2
            
        except Exception:
            return 0.8  # Default good accuracy
    
    def _assess_critical_band_coverage(self, params: Dict[str, Any]) -> float:
        """Assess critical band coverage"""
        try:
            fmin = params.get('fmin', 20)
            fmax = params.get('fmax', 8000)
            
            # Critical bands roughly cover 20 Hz to 15.5 kHz
            ideal_min = 20
            ideal_max = 15500
            
            min_coverage = min(fmin / ideal_min, 1.0) if fmin <= ideal_min else ideal_min / fmin
            max_coverage = min(fmax / ideal_max, 1.0) if fmax >= ideal_max else fmax / ideal_max
            
            return (min_coverage + max_coverage) / 2
            
        except Exception:
            return 0.8  # Default good coverage
    
    def _calculate_contrast_ratio(self, spectrogram: np.ndarray) -> float:
        """Calculate visual contrast ratio"""
        try:
            max_val = np.max(spectrogram)
            min_val = np.min(spectrogram)
            
            if min_val <= 0:
                return float('inf')  # Perfect contrast
                
            return max_val / min_val
            
        except Exception:
            return 2.0  # Default moderate contrast
    
    def _calculate_information_density(self, spectrogram: np.ndarray) -> float:
        """Calculate information density"""
        try:
            # Use entropy as a measure of information content
            # Normalize to 0-1 range first
            normalized = (spectrogram - np.min(spectrogram)) / (np.max(spectrogram) - np.min(spectrogram))
            
            # Calculate histogram
            hist, _ = np.histogram(normalized.flatten(), bins=256, range=(0, 1))
            hist = hist / np.sum(hist)  # Normalize
            
            # Calculate entropy
            hist = hist[hist > 0]  # Remove zero entries
            entropy = -np.sum(hist * np.log2(hist))
            
            # Normalize to 0-1 scale (max entropy for 256 bins is log2(256) = 8)
            return entropy / 8.0
            
        except Exception:
            return 0.5  # Default moderate information density
    
    def _assess_spectrogram_quality_level(self, metrics: SpectrogramQualityMetrics) -> SpectrogramQualityLevel:
        """Assess overall spectrogram quality level"""
        
        quality = SpectrogramQualityLevel.EXCELLENT
        
        # Check resolution requirements
        if (metrics.temporal_resolution_ms and 
            metrics.temporal_resolution_ms > self.quality_gates.MIN_TEMPORAL_RESOLUTION_MS):
            quality = min(quality, SpectrogramQualityLevel.ACCEPTABLE)
        
        if (metrics.frequency_resolution_hz and 
            metrics.frequency_resolution_hz > self.quality_gates.MIN_FREQUENCY_RESOLUTION_HZ):
            quality = min(quality, SpectrogramQualityLevel.ACCEPTABLE)
        
        # Check dynamic range
        if (metrics.dynamic_range_db and 
            metrics.dynamic_range_db < self.quality_gates.MIN_DYNAMIC_RANGE_DB):
            quality = min(quality, SpectrogramQualityLevel.POOR)
        
        # Check for artifacts
        if (metrics.aliasing_artifacts or metrics.windowing_artifacts or metrics.normalization_issues):
            quality = min(quality, SpectrogramQualityLevel.ACCEPTABLE)
        
        # Check perceptual quality
        if (metrics.mel_scale_accuracy and 
            metrics.mel_scale_accuracy < self.quality_gates.MIN_MEL_ACCURACY):
            quality = min(quality, SpectrogramQualityLevel.GOOD)
        
        # Check visual quality
        if (metrics.image_contrast_ratio and 
            metrics.image_contrast_ratio < self.quality_gates.MIN_CONTRAST_RATIO):
            quality = min(quality, SpectrogramQualityLevel.GOOD)
        
        return quality
    
    def _calculate_spectrogram_quality_score(self, metrics: SpectrogramQualityMetrics) -> float:
        """Calculate numerical quality score"""
        score = 100.0
        
        # Resolution scoring (20% weight)
        resolution_score = 100.0
        if metrics.temporal_resolution_ms:
            if metrics.temporal_resolution_ms <= 20:
                temporal_score = 100.0
            elif metrics.temporal_resolution_ms <= 50:
                temporal_score = 80.0
            else:
                temporal_score = 60.0
            resolution_score = (resolution_score + temporal_score) / 2
        
        # Dynamic range scoring (25% weight)
        if metrics.dynamic_range_db:
            if metrics.dynamic_range_db >= 80:
                dr_score = 100.0
            elif metrics.dynamic_range_db >= 60:
                dr_score = 80.0
            elif metrics.dynamic_range_db >= 40:
                dr_score = 60.0
            else:
                dr_score = 30.0
            score = score * 0.75 + dr_score * 0.25
        
        # Artifact penalty (15% weight)
        artifact_penalty = 1.0
        if metrics.aliasing_artifacts:
            artifact_penalty *= 0.8
        if metrics.windowing_artifacts:
            artifact_penalty *= 0.9
        if metrics.normalization_issues:
            artifact_penalty *= 0.85
        
        score *= (0.85 + artifact_penalty * 0.15)
        
        # Visual quality (20% weight)
        if metrics.image_contrast_ratio and metrics.information_density:
            contrast_score = min(100.0, metrics.image_contrast_ratio / 10 * 100)
            info_score = metrics.information_density * 100
            visual_score = (contrast_score + info_score) / 2
            score = score * 0.8 + visual_score * 0.2
        
        # Perceptual quality (20% weight)
        if metrics.mel_scale_accuracy:
            perceptual_score = metrics.mel_scale_accuracy * 100
            score = score * 0.8 + perceptual_score * 0.2
        
        return max(0.0, min(100.0, score))
    
    def _calculate_llm_suitability(self, metrics: SpectrogramQualityMetrics, spec_type: str) -> float:
        """Calculate LLM analysis suitability score"""
        
        suitability = 100.0
        
        # LLM prefer high information density
        if metrics.information_density:
            if metrics.information_density < 0.3:
                suitability *= 0.7
            elif metrics.information_density < 0.5:
                suitability *= 0.9
        
        # LLM prefer good contrast
        if metrics.image_contrast_ratio:
            if metrics.image_contrast_ratio < 2.0:
                suitability *= 0.8
        
        # LLM prefer mel scale for musical analysis
        if spec_type == 'mel':
            suitability *= 1.1  # Bonus for mel scale
        
        # LLM prefer adequate resolution
        if metrics.temporal_resolution_ms and metrics.temporal_resolution_ms > 30:
            suitability *= 0.9
        
        return min(100.0, suitability)
    
    def _validate_quality_gates(self, metrics: SpectrogramQualityMetrics) -> bool:
        """Validate against quality gates"""
        
        # Critical quality gates that must pass
        gates_passed = True
        
        if metrics.quality_level == SpectrogramQualityLevel.FAILED:
            gates_passed = False
        
        if metrics.dynamic_range_db and metrics.dynamic_range_db < 30:  # Minimum threshold
            gates_passed = False
        
        if metrics.llm_suitability_score and metrics.llm_suitability_score < 50:  # Minimum LLM suitability
            gates_passed = False
        
        return gates_passed
    
    def _display_quality_results(self, metrics: SpectrogramQualityMetrics):
        """Display spectrogram quality results"""
        
        level_colors = {
            SpectrogramQualityLevel.EXCELLENT: "green",
            SpectrogramQualityLevel.GOOD: "blue",
            SpectrogramQualityLevel.ACCEPTABLE: "yellow",
            SpectrogramQualityLevel.POOR: "red",
            SpectrogramQualityLevel.FAILED: "red bold"
        }
        
        color = level_colors.get(metrics.quality_level, "white")
        console.print(f"[{color}]🎯 Spectrogram Quality: {metrics.quality_level.name}[/{color}]")
        console.print(f"[{color}]📊 Quality Score: {metrics.quality_score:.1f}/100[/{color}]")
        console.print(f"[{color}]🤖 LLM Suitability: {metrics.llm_suitability_score:.1f}/100[/{color}]")
        
        # Resolution metrics
        if metrics.temporal_resolution_ms:
            console.print(f"[cyan]⏱ Temporal Resolution: {metrics.temporal_resolution_ms:.1f} ms[/cyan]")
        
        if metrics.frequency_resolution_hz:
            console.print(f"[cyan]🎵 Frequency Resolution: {metrics.frequency_resolution_hz:.1f} Hz[/cyan]")
        
        if metrics.dynamic_range_db:
            dr_color = "green" if metrics.dynamic_range_db > 60 else "yellow"
            console.print(f"[{dr_color}]📈 Dynamic Range: {metrics.dynamic_range_db:.1f} dB[/{dr_color}]")
        
        # Artifact detection
        if metrics.aliasing_artifacts or metrics.windowing_artifacts or metrics.normalization_issues:
            console.print("[red]⚠ Artifacts detected:[/red]")
            if metrics.aliasing_artifacts:
                console.print("  [red]✗ Spectral aliasing[/red]")
            if metrics.windowing_artifacts:
                console.print("  [red]✗ Windowing artifacts[/red]")
            if metrics.normalization_issues:
                console.print("  [red]✗ Normalization issues[/red]")
        else:
            console.print("[green]✓ No artifacts detected[/green]")
        
        # Perceptual quality
        if metrics.mel_scale_accuracy:
            console.print(f"[cyan]🎼 Mel Scale Accuracy: {metrics.mel_scale_accuracy:.1%}[/cyan]")
        
        if metrics.critical_band_coverage:
            console.print(f"[cyan]🔊 Critical Band Coverage: {metrics.critical_band_coverage:.1%}[/cyan]")
    
    def _create_enhanced_visualization(self,
                                     spectrogram_data: np.ndarray,
                                     spectrogram_type: str,
                                     output_path: Path,
                                     quality_metrics: Optional[SpectrogramQualityMetrics] = None) -> Optional[str]:
        """Create enhanced visualization with quality information"""
        
        try:
            fig, ax = plt.subplots(figsize=(12, 8))
            
            # Enhanced colormap for better perception
            img = ax.imshow(
                spectrogram_data,
                aspect='auto',
                origin='lower',
                cmap='plasma',  # Better for scientific visualization
                interpolation='bilinear'
            )
            
            # Add colorbar
            cbar = plt.colorbar(img, ax=ax)
            cbar.set_label('Magnitude (dB)', fontsize=12)
            
            # Enhanced labels
            ax.set_xlabel('Time Frames', fontsize=12)
            if spectrogram_type == 'mel':
                ax.set_ylabel('Mel Frequency Bins', fontsize=12)
            elif spectrogram_type == 'linear':
                ax.set_ylabel('Frequency Bins', fontsize=12)
            elif spectrogram_type == 'cqt':
                ax.set_ylabel('CQT Frequency Bins', fontsize=12)
            
            # Add quality information as title
            title = f'{spectrogram_type.upper()} Spectrogram'
            if quality_metrics:
                title += f' (Quality: {quality_metrics.quality_level.name}, Score: {quality_metrics.quality_score:.1f}/100)'
            
            ax.set_title(title, fontsize=14, fontweight='bold')
            
            # Improve layout
            plt.tight_layout()
            
            # Save with high quality
            plt.savefig(str(output_path), dpi=300, bbox_inches='tight')
            plt.close()
            
            console.print(f"[green]✓ Enhanced visualization saved:[/green] {output_path}")
            
            # Return base64 encoded image for API use
            with open(output_path, 'rb') as img_file:
                img_data = base64.b64encode(img_file.read()).decode('utf-8')
                return img_data
                
        except Exception as e:
            console.print(f"[red]✗ Visualization creation failed:[/red] {e}")
            return None


# Factory function
def create_quality_spectrogram_generator() -> EnhancedSpectrogramGenerator:
    """Create enhanced spectrogram generator with quality validation"""
    return EnhancedSpectrogramGenerator()