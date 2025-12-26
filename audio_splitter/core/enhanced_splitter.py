#!/usr/bin/env python3
"""
Enhanced Audio Splitter with Scientific DSP Optimization
Audio Signal Processing Engineer implementation

Features:
- Cross-fade transitions to eliminate boundary artifacts
- Dithering for temporal truncation
- Quality validation with THD+N measurement  
- Zero-crossing detection for optimal split points
- Psychoacoustic windowing
"""

import numpy as np
import librosa
import soundfile as sf
from pathlib import Path
from typing import List, Tuple, Union, Optional, Dict, Any
from scipy.signal import butter, filtfilt, find_peaks
from rich.console import Console

from .quality_framework import (
    AudioQualityAnalyzer,
    QualityMetrics,
    QualityLevel,
    high_quality_processing,
    basic_quality_check
)
from .splitter import AudioSplitter

console = Console()


class EnhancedAudioSplitter(AudioSplitter):
    """Audio Splitter with scientific DSP optimization and quality validation"""
    
    def __init__(self):
        super().__init__()
        self.quality_analyzer = AudioQualityAnalyzer()
        
        # DSP parameters for optimal quality
        self.fade_duration_ms = 10      # Cross-fade duration
        self.dither_amplitude = 1e-6    # Dithering level  
        self.zero_crossing_window_ms = 5 # Window for zero-crossing search
        
    @high_quality_processing
    def split_audio_enhanced(self, 
                           input_file: Union[str, Path], 
                           segments: List[Tuple[int, int, str]], 
                           output_dir: Union[str, Path] = "output",
                           fade_enabled: bool = True,
                           dither_enabled: bool = True,
                           quality_validation: bool = True) -> Dict[str, Any]:
        """
        Enhanced audio splitting with scientific DSP optimization
        
        Args:
            input_file: Path to audio file
            segments: List of (start_ms, end_ms, name) tuples
            output_dir: Output directory
            fade_enabled: Enable cross-fade transitions
            dither_enabled: Enable dithering for temporal quantization
            quality_validation: Enable quality analysis
            
        Returns:
            Dict with splitting results and quality metrics
        """
        input_path = Path(input_file)
        output_path = Path(output_dir)
        
        console.print(f"[blue]🔬 Enhanced Audio Splitting:[/blue] {input_path.name}")
        console.print(f"[cyan]   Fade: {fade_enabled} | Dither: {dither_enabled} | Quality: {quality_validation}[/cyan]")
        
        try:
            # Load audio preserving all characteristics
            audio_data, sample_rate = librosa.load(str(input_path), sr=None, mono=False)
            console.print(f"[green]✓ Audio loaded:[/green] {sample_rate}Hz, shape: {audio_data.shape}")
            
            # Create output directory
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Store original for quality reference
            original_audio = audio_data.copy()
            
            results = {
                'input_file': str(input_path),
                'output_dir': str(output_path),
                'segments_processed': 0,
                'segments_failed': 0,
                'total_segments': len(segments),
                'segment_files': [],  # Track output files
                'quality_metrics': [],
                'processing_summary': {}
            }
            
            # Process each segment with enhanced DSP
            for i, (start_ms, end_ms, name) in enumerate(segments):
                console.print(f"\n[blue]📂 Processing segment {i+1}/{len(segments)}:[/blue] {name}")
                
                segment_result = self._process_segment_enhanced(
                    audio_data=audio_data,
                    sample_rate=sample_rate,
                    start_ms=start_ms,
                    end_ms=end_ms,
                    segment_name=name,
                    output_path=output_path,
                    fade_enabled=fade_enabled,
                    dither_enabled=dither_enabled,
                    quality_validation=quality_validation,
                    reference_audio=original_audio
                )
                
                if segment_result['success']:
                    results['segments_processed'] += 1
                    output_file = segment_result['output_file']
                    results['segment_files'].append(output_file)
                    console.print(f"[green]✓ Segment created:[/green] {output_file}")

                    if quality_validation and segment_result.get('quality_metrics'):
                        results['quality_metrics'].append(segment_result['quality_metrics'])
                        self._display_segment_quality(segment_result['quality_metrics'], name)
                else:
                    results['segments_failed'] += 1
                    console.print(f"[red]✗ Segment failed:[/red] {segment_result.get('error', 'Unknown error')}")
            
            # Generate processing summary
            self._generate_processing_summary(results)

            # Add success flag based on results
            results['success'] = results['segments_processed'] > 0 and results['segments_failed'] == 0

            return results
            
        except Exception as e:
            console.print(f"[red]✗ Enhanced splitting failed:[/red] {e}")
            return {
                'success': False,
                'error': str(e),
                'segments_processed': 0,
                'segments_failed': len(segments)
            }
    
    def _process_segment_enhanced(self,
                                audio_data: np.ndarray,
                                sample_rate: int,
                                start_ms: int,
                                end_ms: int,
                                segment_name: str,
                                output_path: Path,
                                fade_enabled: bool,
                                dither_enabled: bool,
                                quality_validation: bool,
                                reference_audio: np.ndarray) -> Dict[str, Any]:
        """Process a single segment with enhanced DSP"""
        
        try:
            # Convert to samples with optimal boundary detection
            start_sample = self._ms_to_sample_optimized(start_ms, sample_rate, audio_data)
            end_sample = self._ms_to_sample_optimized(end_ms, sample_rate, audio_data)
            
            # Validate sample boundaries
            total_samples = audio_data.shape[-1] if len(audio_data.shape) > 1 else len(audio_data)
            start_sample = max(0, min(start_sample, total_samples - 1))
            end_sample = max(start_sample + 1, min(end_sample, total_samples))
            
            console.print(f"[cyan]🎯 Optimal boundaries:[/cyan] {start_sample}-{end_sample} samples")
            
            # Extract segment with proper handling of mono/stereo
            if len(audio_data.shape) == 1:
                # Mono audio
                segment = audio_data[start_sample:end_sample].copy()
            else:
                # Multi-channel audio
                segment = audio_data[:, start_sample:end_sample].copy()
            
            # Apply enhanced DSP processing
            if fade_enabled:
                segment = self._apply_perceptual_fading(segment, sample_rate)
                console.print("[cyan]✓ Perceptual fading applied[/cyan]")
            
            if dither_enabled:
                segment = self._apply_triangular_dithering(segment)
                console.print("[cyan]✓ Triangular dithering applied[/cyan]")
            
            # Determine output filename and format
            output_file = output_path / f"{segment_name}.wav"
            
            # Write segment with optimal parameters
            if len(segment.shape) == 1:
                # Mono
                sf.write(str(output_file), segment, sample_rate, subtype='PCM_24')
            else:
                # Multi-channel (transpose for soundfile)
                sf.write(str(output_file), segment.T, sample_rate, subtype='PCM_24')
            
            result = {
                'success': True,
                'output_file': str(output_file),
                'start_sample': start_sample,
                'end_sample': end_sample,
                'duration_ms': (end_sample - start_sample) / sample_rate * 1000
            }
            
            # Quality validation if enabled
            if quality_validation:
                # Extract corresponding reference segment
                if len(reference_audio.shape) == 1:
                    ref_segment = reference_audio[start_sample:end_sample]
                else:
                    ref_segment = reference_audio[:, start_sample:end_sample]
                
                # Analyze quality
                quality_metrics = self.quality_analyzer.analyze_audio_quality(
                    audio_data=segment,
                    sample_rate=sample_rate,
                    reference_data=ref_segment,
                    file_path=output_file
                )
                
                result['quality_metrics'] = quality_metrics
                
                # Check quality threshold
                if quality_metrics.quality_level == QualityLevel.FAILED:
                    result['quality_warning'] = True
                    console.print("[yellow]⚠ Quality below acceptable threshold[/yellow]")
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _ms_to_sample_optimized(self, time_ms: int, sample_rate: int, audio_data: np.ndarray) -> int:
        """Convert milliseconds to sample with zero-crossing optimization"""
        
        # Basic sample calculation
        base_sample = int((time_ms / 1000) * sample_rate)
        
        # Zero-crossing optimization window
        window_samples = int((self.zero_crossing_window_ms / 1000) * sample_rate)
        
        # Define search window
        total_samples = audio_data.shape[-1] if len(audio_data.shape) > 1 else len(audio_data)
        search_start = max(0, base_sample - window_samples // 2)
        search_end = min(total_samples, base_sample + window_samples // 2)
        
        if search_start >= search_end:
            return base_sample
        
        # Find optimal zero-crossing point
        try:
            # Use first channel for mono or stereo
            if len(audio_data.shape) == 1:
                search_signal = audio_data[search_start:search_end]
            else:
                search_signal = audio_data[0, search_start:search_end]  # First channel
            
            # Find zero-crossings
            zero_crossings = np.where(np.diff(np.signbit(search_signal)))[0]
            
            if len(zero_crossings) > 0:
                # Find closest zero-crossing to base position
                base_offset = base_sample - search_start
                distances = np.abs(zero_crossings - base_offset)
                closest_zc_idx = np.argmin(distances)
                optimal_sample = search_start + zero_crossings[closest_zc_idx]
                
                console.print(f"[green]✓ Zero-crossing optimization:[/green] {base_sample} → {optimal_sample}")
                return optimal_sample
            
        except Exception as e:
            console.print(f"[yellow]⚠ Zero-crossing optimization failed:[/yellow] {e}")
        
        return base_sample
    
    def _apply_perceptual_fading(self, audio: np.ndarray, sample_rate: int) -> np.ndarray:
        """Apply perceptual fading using Hann window for smooth transitions"""
        
        fade_samples = int((self.fade_duration_ms / 1000) * sample_rate)
        
        if len(audio.shape) == 1:
            # Mono audio
            audio_length = len(audio)
        else:
            # Multi-channel audio
            audio_length = audio.shape[1]
        
        # Don't fade if segment is too short
        if audio_length < fade_samples * 2:
            return audio
        
        # Create Hann window for smooth fading
        fade_in = np.hanning(fade_samples * 2)[:fade_samples]   # Rising edge
        fade_out = np.hanning(fade_samples * 2)[fade_samples:]  # Falling edge
        
        # Apply fading
        if len(audio.shape) == 1:
            # Mono
            faded_audio = audio.copy()
            faded_audio[:fade_samples] *= fade_in
            faded_audio[-fade_samples:] *= fade_out
        else:
            # Multi-channel
            faded_audio = audio.copy()
            for ch in range(audio.shape[0]):
                faded_audio[ch, :fade_samples] *= fade_in
                faded_audio[ch, -fade_samples:] *= fade_out
        
        return faded_audio
    
    def _apply_triangular_dithering(self, audio: np.ndarray) -> np.ndarray:
        """Apply triangular dithering to reduce quantization artifacts"""
        
        # Generate triangular probability distribution dither
        # TPDF (Triangular Probability Distribution Function)
        if len(audio.shape) == 1:
            dither_shape = audio.shape
        else:
            dither_shape = audio.shape
        
        # Generate two uniform random distributions and subtract
        # This creates triangular distribution
        uniform1 = np.random.uniform(-self.dither_amplitude, self.dither_amplitude, dither_shape)
        uniform2 = np.random.uniform(-self.dither_amplitude, self.dither_amplitude, dither_shape)
        triangular_dither = uniform1 - uniform2
        
        # Apply dither
        dithered_audio = audio + triangular_dither
        
        # Ensure no clipping
        if len(audio.shape) == 1:
            max_val = np.max(np.abs(dithered_audio))
        else:
            max_val = np.max(np.abs(dithered_audio))
        
        if max_val > 1.0:
            dithered_audio = dithered_audio / max_val * 0.99
        
        return dithered_audio
    
    def _display_segment_quality(self, metrics: QualityMetrics, segment_name: str):
        """Display quality metrics for a segment"""
        
        level_colors = {
            QualityLevel.EXCELLENT: "green",
            QualityLevel.GOOD: "blue",
            QualityLevel.ACCEPTABLE: "yellow", 
            QualityLevel.POOR: "red",
            QualityLevel.FAILED: "red bold"
        }
        
        color = level_colors.get(metrics.quality_level, "white")
        console.print(f"  [{color}]🎯 {segment_name}: {metrics.quality_level.value.upper()} ({metrics.quality_score:.1f}/100)[/{color}]")
        
        if metrics.thd_plus_n_db is not None:
            thd_color = "green" if metrics.thd_plus_n_db < -60 else "yellow"
            console.print(f"    [cyan]THD+N: {metrics.thd_plus_n_db:.1f} dB[/cyan]")
        
        if metrics.artifacts_detected:
            console.print(f"    [red]⚠ Artifacts detected[/red]")
    
    def _generate_processing_summary(self, results: Dict[str, Any]):
        """Generate comprehensive processing summary"""
        
        total_segments = results['total_segments']
        processed = results['segments_processed']
        failed = results['segments_failed']
        
        success_rate = (processed / total_segments * 100) if total_segments > 0 else 0
        
        console.print(f"\n[blue]📊 Enhanced Splitting Summary:[/blue]")
        console.print(f"[green]✓ Segments processed: {processed}/{total_segments} ({success_rate:.1f}%)[/green]")
        
        if failed > 0:
            console.print(f"[red]✗ Failed segments: {failed}[/red]")
        
        # Quality analysis summary
        if results['quality_metrics']:
            quality_levels = [m.quality_level for m in results['quality_metrics']]
            excellent_count = quality_levels.count(QualityLevel.EXCELLENT)
            good_count = quality_levels.count(QualityLevel.GOOD)
            acceptable_count = quality_levels.count(QualityLevel.ACCEPTABLE)
            poor_count = quality_levels.count(QualityLevel.POOR)
            
            console.print(f"\n[blue]🔬 Quality Distribution:[/blue]")
            if excellent_count > 0:
                console.print(f"[green]  Excellent: {excellent_count}[/green]")
            if good_count > 0:
                console.print(f"[blue]  Good: {good_count}[/blue]")
            if acceptable_count > 0:
                console.print(f"[yellow]  Acceptable: {acceptable_count}[/yellow]")
            if poor_count > 0:
                console.print(f"[red]  Poor: {poor_count}[/red]")
            
            # Average quality metrics
            avg_thd = np.mean([m.thd_plus_n_db for m in results['quality_metrics'] if m.thd_plus_n_db is not None])
            avg_snr = np.mean([m.snr_db for m in results['quality_metrics'] if m.snr_db is not None])
            avg_score = np.mean([m.quality_score for m in results['quality_metrics'] if m.quality_score is not None])
            
            if not np.isnan(avg_thd):
                console.print(f"[cyan]📊 Average THD+N: {avg_thd:.1f} dB[/cyan]")
            if not np.isnan(avg_snr):
                console.print(f"[cyan]📊 Average SNR: {avg_snr:.1f} dB[/cyan]")
            if not np.isnan(avg_score):
                console.print(f"[cyan]📊 Average Quality Score: {avg_score:.1f}/100[/cyan]")
        
        results['processing_summary'] = {
            'success_rate': success_rate,
            'quality_distribution': {
                'excellent': excellent_count if results['quality_metrics'] else 0,
                'good': good_count if results['quality_metrics'] else 0,
                'acceptable': acceptable_count if results['quality_metrics'] else 0,
                'poor': poor_count if results['quality_metrics'] else 0
            }
        }


# Factory function for enhanced splitter
def create_quality_splitter() -> EnhancedAudioSplitter:
    """Create an enhanced audio splitter with quality validation"""
    return EnhancedAudioSplitter()