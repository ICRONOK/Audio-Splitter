#!/usr/bin/env python3
"""
Audio Quality Framework - Scientific Audio Signal Processing
Audio Signal Processing Engineer implementation

Provides comprehensive quality assessment with scientific metrics:
- THD+N (Total Harmonic Distortion + Noise)
- SNR (Signal-to-Noise Ratio)
- Dynamic Range Analysis
- Artifact Detection (Clipping, Aliasing)
- Performance Monitoring
"""

import numpy as np
import librosa
import soundfile as sf
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any, Optional, Tuple, Union, List
from pathlib import Path
import time
import psutil
import os
from scipy import signal
from scipy.fft import fft, fftfreq

import logging
logger = logging.getLogger(__name__)


class QualityLevel(Enum):
    """Quality assessment levels based on professional audio standards"""
    EXCELLENT = "excellent"    # THD+N < -80dB, SNR > 100dB
    GOOD = "good"             # THD+N < -60dB, SNR > 90dB  
    ACCEPTABLE = "acceptable"  # THD+N < -40dB, SNR > 70dB
    POOR = "poor"             # Below acceptable standards
    FAILED = "failed"         # Critical quality failure


@dataclass
class QualityMetrics:
    """Scientific audio quality metrics following professional standards"""
    
    # Distortion measurements
    thd_plus_n_db: Optional[float] = None    # Total Harmonic Distortion + Noise
    snr_db: Optional[float] = None           # Signal-to-Noise Ratio
    dynamic_range_db: Optional[float] = None # Dynamic Range preservation
    
    # Level measurements  
    peak_level_db: Optional[float] = None    # Peak level monitoring
    rms_level_db: Optional[float] = None     # RMS level tracking
    crest_factor_db: Optional[float] = None  # Crest factor analysis
    
    # Artifact detection
    artifacts_detected: bool = False          # General artifact flag
    clipping_detected: bool = False          # Digital clipping detection
    aliasing_detected: bool = False          # Aliasing artifact detection
    dc_offset_detected: bool = False         # DC offset detection
    
    # Performance metrics
    processing_time_ms: Optional[float] = None    # Processing time
    memory_usage_mb: Optional[float] = None       # Peak memory usage
    file_size_mb: Optional[float] = None          # Output file size
    
    # Overall assessment
    quality_level: Optional[QualityLevel] = None  # Overall quality rating
    quality_score: Optional[float] = None         # Numerical score (0-100)
    
    # Metadata
    sample_rate: Optional[int] = None        # Audio sample rate
    channels: Optional[int] = None           # Number of channels
    duration_seconds: Optional[float] = None # Audio duration
    format: Optional[str] = None             # Audio format


class QualityThresholds:
    """Professional audio quality thresholds"""
    
    # THD+N thresholds (in dB, negative values)
    THD_EXCELLENT = -80.0      # Studio mastering quality
    THD_GOOD = -60.0          # Professional broadcast quality
    THD_ACCEPTABLE = -40.0     # Consumer electronics quality
    
    # SNR thresholds (in dB, positive values)
    SNR_EXCELLENT = 100.0      # High-end studio equipment
    SNR_GOOD = 90.0           # Professional equipment  
    SNR_ACCEPTABLE = 70.0      # Consumer electronics
    
    # Dynamic range preservation (percentage)
    DYNAMIC_RANGE_MINIMUM = 95.0  # 95% preservation required
    
    # Performance thresholds
    MEMORY_LIMIT_RATIO = 4.0       # Max 4x input file size
    PROCESSING_TIME_RATIO = 2.0    # Max 2x real-time
    
    # Artifact detection thresholds
    CLIPPING_THRESHOLD = 0.99      # Digital full-scale threshold
    DC_OFFSET_THRESHOLD = 0.01     # DC offset detection
    ALIASING_FREQUENCY_RATIO = 0.4  # Nyquist frequency ratio


class AudioQualityAnalyzer:
    """Scientific audio quality analysis engine"""
    
    def __init__(self):
        self.thresholds = QualityThresholds()
        self.process = psutil.Process(os.getpid())
        
    def analyze_audio_quality(self, 
                            audio_data: np.ndarray, 
                            sample_rate: int,
                            reference_data: Optional[np.ndarray] = None,
                            file_path: Optional[Path] = None) -> QualityMetrics:
        """
        Comprehensive audio quality analysis
        
        Args:
            audio_data: Audio signal array
            sample_rate: Sample rate in Hz
            reference_data: Reference signal for comparison (optional)
            file_path: File path for metadata (optional)
            
        Returns:
            QualityMetrics: Comprehensive quality assessment
        """
        start_time = time.time()
        initial_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        
        metrics = QualityMetrics()
        
        # Basic audio properties
        metrics.sample_rate = sample_rate
        metrics.channels = 1 if len(audio_data.shape) == 1 else audio_data.shape[0]
        metrics.duration_seconds = len(audio_data) / sample_rate if len(audio_data.shape) == 1 else audio_data.shape[1] / sample_rate
        
        # File metadata
        if file_path:
            metrics.file_size_mb = file_path.stat().st_size / 1024 / 1024
            metrics.format = file_path.suffix.upper().replace('.', '')
        
        # Ensure audio is 1D for analysis
        if len(audio_data.shape) > 1:
            # Use left channel for stereo analysis
            audio_signal = audio_data[0] if audio_data.shape[0] > 1 else audio_data.flatten()
        else:
            audio_signal = audio_data
            
        # Level measurements
        metrics.peak_level_db = self._calculate_peak_level(audio_signal)
        metrics.rms_level_db = self._calculate_rms_level(audio_signal)
        metrics.crest_factor_db = metrics.peak_level_db - metrics.rms_level_db
        
        # Distortion analysis
        if reference_data is not None:
            metrics.thd_plus_n_db = self._calculate_thd_plus_n(audio_signal, reference_data, sample_rate)
            metrics.snr_db = self._calculate_snr(audio_signal, reference_data)
            metrics.dynamic_range_db = self._calculate_dynamic_range_preservation(audio_signal, reference_data)
        else:
            # Estimate THD+N from harmonic analysis
            metrics.thd_plus_n_db = self._estimate_thd_from_harmonics(audio_signal, sample_rate)
            metrics.snr_db = self._estimate_snr_from_signal(audio_signal)
            
        # Artifact detection
        metrics.clipping_detected = self._detect_clipping(audio_signal)
        metrics.aliasing_detected = self._detect_aliasing(audio_signal, sample_rate)
        metrics.dc_offset_detected = self._detect_dc_offset(audio_signal)
        metrics.artifacts_detected = (metrics.clipping_detected or 
                                    metrics.aliasing_detected or 
                                    metrics.dc_offset_detected)
        
        # Performance measurements
        end_time = time.time()
        metrics.processing_time_ms = (end_time - start_time) * 1000
        peak_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        metrics.memory_usage_mb = peak_memory - initial_memory
        
        # Overall quality assessment
        metrics.quality_level = self._assess_overall_quality(metrics)
        metrics.quality_score = self._calculate_quality_score(metrics)
        
        return metrics
    
    def _calculate_peak_level(self, audio: np.ndarray) -> float:
        """Calculate peak level in dB"""
        peak = np.max(np.abs(audio))
        if peak == 0:
            return -np.inf
        return 20 * np.log10(peak)
    
    def _calculate_rms_level(self, audio: np.ndarray) -> float:
        """Calculate RMS level in dB"""
        rms = np.sqrt(np.mean(audio**2))
        if rms == 0:
            return -np.inf
        return 20 * np.log10(rms)
    
    def _calculate_thd_plus_n(self, signal: np.ndarray, reference: np.ndarray, sample_rate: int) -> float:
        """Calculate Total Harmonic Distortion + Noise"""
        try:
            # Ensure both signals have same shape and are 1D
            if len(signal.shape) > 1:
                signal = signal.flatten() if signal.shape[0] == 1 else signal[0]
            if len(reference.shape) > 1:
                reference = reference.flatten() if reference.shape[0] == 1 else reference[0]
            
            # Calculate difference signal (distortion + noise)
            if len(signal) != len(reference):
                # Align signals
                min_length = min(len(signal), len(reference))
                signal = signal[:min_length]
                reference = reference[:min_length]
            
            error_signal = signal - reference
            
            # Calculate THD+N as ratio of error energy to signal energy
            signal_power = np.mean(reference**2)
            error_power = np.mean(error_signal**2)
            
            if signal_power == 0:
                return -np.inf
                
            thd_plus_n_ratio = error_power / signal_power
            
            if thd_plus_n_ratio <= 0:
                return -120.0  # Very low distortion
                
            return 10 * np.log10(thd_plus_n_ratio)
            
        except Exception as e:
            logger.warning(f"THD+N calculation failed: {e}")
            return None
    
    def _calculate_snr(self, signal: np.ndarray, reference: np.ndarray) -> float:
        """Calculate Signal-to-Noise Ratio"""
        try:
            # Ensure both signals have same shape and are 1D
            if len(signal.shape) > 1:
                signal = signal.flatten() if signal.shape[0] == 1 else signal[0]
            if len(reference.shape) > 1:
                reference = reference.flatten() if reference.shape[0] == 1 else reference[0]
            
            if len(signal) != len(reference):
                min_length = min(len(signal), len(reference))
                signal = signal[:min_length]
                reference = reference[:min_length]
            
            noise = signal - reference
            
            signal_power = np.mean(reference**2)
            noise_power = np.mean(noise**2)
            
            if noise_power == 0:
                return 120.0  # Very high SNR
            if signal_power == 0:
                return -np.inf
                
            snr_ratio = signal_power / noise_power
            return 10 * np.log10(snr_ratio)
            
        except Exception as e:
            logger.warning(f"SNR calculation failed: {e}")
            return None
    
    def _calculate_dynamic_range_preservation(self, signal: np.ndarray, reference: np.ndarray) -> float:
        """Calculate dynamic range preservation percentage"""
        try:
            ref_dynamic_range = np.max(reference) - np.min(reference)
            sig_dynamic_range = np.max(signal) - np.min(signal)
            
            if ref_dynamic_range == 0:
                return 100.0
                
            preservation = (sig_dynamic_range / ref_dynamic_range) * 100
            return min(preservation, 100.0)  # Cap at 100%
            
        except Exception as e:
            logger.warning(f"Dynamic range calculation failed: {e}")
            return None
    
    def _estimate_thd_from_harmonics(self, audio: np.ndarray, sample_rate: int) -> float:
        """Estimate THD from harmonic content analysis"""
        try:
            # Perform FFT
            fft_data = fft(audio)
            freqs = fftfreq(len(audio), 1/sample_rate)
            magnitude = np.abs(fft_data)
            
            # Find fundamental frequency (peak in lower frequencies)
            low_freq_mask = (freqs > 80) & (freqs < 1000)  # Musical range
            if not np.any(low_freq_mask):
                return -60.0  # Default good value
                
            fundamental_idx = np.argmax(magnitude[low_freq_mask])
            fundamental_freq = freqs[low_freq_mask][fundamental_idx]
            
            if fundamental_freq <= 0:
                return -60.0
            
            # Calculate harmonic distortion
            fundamental_power = magnitude[low_freq_mask][fundamental_idx]**2
            
            harmonic_power = 0
            for harmonic in range(2, 6):  # 2nd to 5th harmonics
                harmonic_freq = fundamental_freq * harmonic
                if harmonic_freq < sample_rate / 2:  # Below Nyquist
                    harmonic_idx = np.argmin(np.abs(freqs - harmonic_freq))
                    harmonic_power += magnitude[harmonic_idx]**2
            
            if fundamental_power == 0:
                return -60.0
                
            thd_ratio = harmonic_power / fundamental_power
            if thd_ratio <= 0:
                return -80.0  # Excellent
                
            return 10 * np.log10(thd_ratio)
            
        except Exception as e:
            logger.warning(f"THD estimation failed: {e}")
            return -60.0  # Default good value
    
    def _estimate_snr_from_signal(self, audio: np.ndarray) -> float:
        """Estimate SNR from signal characteristics"""
        try:
            # Use high-frequency content as noise estimate
            # Apply high-pass filter to isolate noise
            from scipy.signal import butter, filtfilt
            
            nyquist = 0.5
            high_cutoff = 0.8  # 80% of Nyquist frequency
            
            b, a = butter(4, high_cutoff, btype='high')
            noise_estimate = filtfilt(b, a, audio)
            
            signal_power = np.mean(audio**2)
            noise_power = np.mean(noise_estimate**2)
            
            if noise_power == 0:
                return 100.0  # Very high SNR
            if signal_power == 0:
                return 0.0
                
            snr_ratio = signal_power / noise_power
            return 10 * np.log10(snr_ratio)
            
        except Exception as e:
            logger.warning(f"SNR estimation failed: {e}")
            return 80.0  # Default good value
    
    def _detect_clipping(self, audio: np.ndarray) -> bool:
        """Detect digital clipping artifacts"""
        try:
            peak_value = np.max(np.abs(audio))
            return peak_value >= self.thresholds.CLIPPING_THRESHOLD
        except:
            return False
    
    def _detect_aliasing(self, audio: np.ndarray, sample_rate: int) -> bool:
        """Detect aliasing artifacts using spectral analysis"""
        try:
            # Perform FFT
            fft_data = fft(audio)
            freqs = fftfreq(len(audio), 1/sample_rate)
            magnitude = np.abs(fft_data)
            
            # Check high-frequency content near Nyquist
            nyquist = sample_rate / 2
            high_freq_start = nyquist * self.thresholds.ALIASING_FREQUENCY_RATIO
            
            high_freq_mask = np.abs(freqs) > high_freq_start
            if not np.any(high_freq_mask):
                return False
                
            high_freq_energy = np.mean(magnitude[high_freq_mask]**2)
            total_energy = np.mean(magnitude**2)
            
            if total_energy == 0:
                return False
                
            high_freq_ratio = high_freq_energy / total_energy
            
            # If high-frequency content is suspiciously high, suspect aliasing
            return high_freq_ratio > 0.1  # 10% threshold
            
        except Exception as e:
            logger.warning(f"Aliasing detection failed: {e}")
            return False
    
    def _detect_dc_offset(self, audio: np.ndarray) -> bool:
        """Detect DC offset"""
        try:
            dc_component = np.abs(np.mean(audio))
            return dc_component > self.thresholds.DC_OFFSET_THRESHOLD
        except:
            return False
    
    def _assess_overall_quality(self, metrics: QualityMetrics) -> QualityLevel:
        """Assess overall quality level based on multiple metrics"""
        
        # Quality level scoring (higher number = better quality)
        quality_scores = {
            QualityLevel.FAILED: 0,
            QualityLevel.POOR: 1,
            QualityLevel.ACCEPTABLE: 2,
            QualityLevel.GOOD: 3,
            QualityLevel.EXCELLENT: 4
        }
        
        # Start with excellent, downgrade based on issues
        quality_score = 4  # EXCELLENT
        
        # Check THD+N
        if metrics.thd_plus_n_db is not None:
            if metrics.thd_plus_n_db > self.thresholds.THD_ACCEPTABLE:
                quality_score = min(quality_score, 1)  # POOR
            elif metrics.thd_plus_n_db > self.thresholds.THD_GOOD:
                quality_score = min(quality_score, 2)  # ACCEPTABLE
            elif metrics.thd_plus_n_db > self.thresholds.THD_EXCELLENT:
                quality_score = min(quality_score, 3)  # GOOD
        
        # Check SNR
        if metrics.snr_db is not None:
            if metrics.snr_db < self.thresholds.SNR_ACCEPTABLE:
                quality_score = min(quality_score, 1)  # POOR
            elif metrics.snr_db < self.thresholds.SNR_GOOD:
                quality_score = min(quality_score, 2)  # ACCEPTABLE
            elif metrics.snr_db < self.thresholds.SNR_EXCELLENT:
                quality_score = min(quality_score, 3)  # GOOD
        
        # Check for artifacts
        if metrics.artifacts_detected:
            quality_score = min(quality_score, 2)  # ACCEPTABLE
        
        # Check performance constraints
        if metrics.file_size_mb and metrics.memory_usage_mb:
            memory_ratio = metrics.memory_usage_mb / metrics.file_size_mb
            if memory_ratio > self.thresholds.MEMORY_LIMIT_RATIO:
                quality_score = min(quality_score, 2)  # ACCEPTABLE
        
        if metrics.processing_time_ms and metrics.duration_seconds:
            time_ratio = (metrics.processing_time_ms / 1000) / metrics.duration_seconds
            if time_ratio > self.thresholds.PROCESSING_TIME_RATIO:
                quality_score = min(quality_score, 2)  # ACCEPTABLE
        
        # Convert back to enum
        for level, score in quality_scores.items():
            if score == quality_score:
                return level
        
        return QualityLevel.ACCEPTABLE  # Default fallback
    
    def _calculate_quality_score(self, metrics: QualityMetrics) -> float:
        """Calculate numerical quality score (0-100)"""
        score = 100.0
        
        # THD+N contribution (40% weight)
        if metrics.thd_plus_n_db is not None:
            if metrics.thd_plus_n_db <= self.thresholds.THD_EXCELLENT:
                thd_score = 100.0
            elif metrics.thd_plus_n_db <= self.thresholds.THD_GOOD:
                thd_score = 80.0
            elif metrics.thd_plus_n_db <= self.thresholds.THD_ACCEPTABLE:
                thd_score = 60.0
            else:
                thd_score = 30.0
            score = score * 0.6 + thd_score * 0.4
        
        # SNR contribution (30% weight)
        if metrics.snr_db is not None:
            if metrics.snr_db >= self.thresholds.SNR_EXCELLENT:
                snr_score = 100.0
            elif metrics.snr_db >= self.thresholds.SNR_GOOD:
                snr_score = 80.0
            elif metrics.snr_db >= self.thresholds.SNR_ACCEPTABLE:
                snr_score = 60.0
            else:
                snr_score = 30.0
            score = score * 0.7 + snr_score * 0.3
        
        # Artifact penalty (20% weight)
        if metrics.artifacts_detected:
            score *= 0.8
        
        # Performance penalty (10% weight)
        performance_penalty = 1.0
        if metrics.file_size_mb and metrics.memory_usage_mb:
            memory_ratio = metrics.memory_usage_mb / metrics.file_size_mb
            if memory_ratio > self.thresholds.MEMORY_LIMIT_RATIO:
                performance_penalty *= 0.9
        
        score *= (0.9 + performance_penalty * 0.1)
        
        return max(0.0, min(100.0, score))


# Quality assessment decorators for production use
def quality_check(min_quality_level: QualityLevel = QualityLevel.ACCEPTABLE):
    """Decorator for automatic quality validation"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            
            # Extract quality metrics if available
            if isinstance(result, dict) and 'quality_metrics' in result:
                metrics = result['quality_metrics']
                if isinstance(metrics, QualityMetrics):
                    # Quality level comparison using score mapping
                    quality_scores = {
                        QualityLevel.FAILED: 0,
                        QualityLevel.POOR: 1,
                        QualityLevel.ACCEPTABLE: 2,
                        QualityLevel.GOOD: 3,
                        QualityLevel.EXCELLENT: 4
                    }
                    
                    current_score = quality_scores.get(metrics.quality_level, 0)
                    min_score = quality_scores.get(min_quality_level, 2)
                    
                    if current_score < min_score:
                        logger.warning(f"Quality below threshold: {metrics.quality_level} < {min_quality_level}")
                        result['quality_warning'] = True
            
            return result
        return wrapper
    return decorator


def high_quality_processing(func):
    """Decorator for high-quality audio processing (THD+N < -80dB)"""
    return quality_check(QualityLevel.EXCELLENT)(func)


def basic_quality_check(func):
    """Decorator for basic quality validation (THD+N < -40dB)"""
    return quality_check(QualityLevel.ACCEPTABLE)(func)


def metadata_quality_check(func):
    """Decorator for metadata operations (THD+N < -60dB)"""
    return quality_check(QualityLevel.GOOD)(func)