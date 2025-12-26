#!/usr/bin/env python3
"""
Enhanced Audio Converter with Scientific Quality Framework
Audio Signal Processing Engineer implementation

Integrates quality validation with conversion operations
"""

import numpy as np
import librosa
import soundfile as sf
from pathlib import Path
from typing import Dict, Any, Optional, Union
from rich.console import Console

from .quality_framework import (
    AudioQualityAnalyzer, 
    QualityMetrics, 
    QualityLevel,
    high_quality_processing,
    basic_quality_check
)
from .converter import AudioConverter

console = Console()


class EnhancedAudioConverter(AudioConverter):
    """Audio Converter with integrated quality assessment"""
    
    def __init__(self):
        super().__init__()
        self.quality_analyzer = AudioQualityAnalyzer()
    
    @high_quality_processing
    def convert_with_quality_validation(self, 
                                      input_path: Union[str, Path], 
                                      output_path: Union[str, Path], 
                                      target_format: str,
                                      quality: str = 'high',
                                      preserve_metadata: bool = True) -> Dict[str, Any]:
        """
        Convert audio with comprehensive quality validation
        
        Returns:
            Dict containing conversion result and quality metrics
        """
        input_path = Path(input_path)
        output_path = Path(output_path)
        
        console.print(f"[blue]🔬 Enhanced Conversion:[/blue] {input_path.name} → {target_format.upper()}")
        
        # Load original audio for quality reference
        try:
            original_audio, sr = librosa.load(str(input_path), sr=None, mono=False)
            console.print(f"[green]✓ Original loaded:[/green] {sr}Hz, {original_audio.shape}")
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to load original: {e}",
                'quality_metrics': None
            }
        
        # Perform conversion using parent class
        conversion_success = self.convert_file(
            input_path, output_path, target_format, quality, preserve_metadata
        )
        
        if not conversion_success:
            return {
                'success': False,
                'error': "Conversion failed",
                'quality_metrics': None
            }
        
        # Load converted audio for quality analysis
        try:
            converted_audio, converted_sr = librosa.load(str(output_path), sr=None, mono=False)
            console.print(f"[green]✓ Converted loaded:[/green] {converted_sr}Hz, {converted_audio.shape}")
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to load converted audio: {e}",
                'quality_metrics': None
            }
        
        # Ensure same sample rate for comparison
        if sr != converted_sr:
            console.print(f"[yellow]⚠ Sample rate mismatch:[/yellow] {sr} → {converted_sr}")
            # Resample original for comparison
            original_audio = librosa.resample(original_audio, orig_sr=sr, target_sr=converted_sr)
            sr = converted_sr
        
        # Ensure same channel configuration
        if original_audio.shape != converted_audio.shape:
            console.print(f"[yellow]⚠ Shape mismatch:[/yellow] {original_audio.shape} → {converted_audio.shape}")
            # Handle mono/stereo conversion for comparison
            if len(original_audio.shape) == 1 and len(converted_audio.shape) > 1:
                # Original mono, converted stereo - use first channel
                converted_audio = converted_audio[0]
            elif len(original_audio.shape) > 1 and len(converted_audio.shape) == 1:
                # Original stereo, converted mono - convert original to mono
                original_audio = np.mean(original_audio, axis=0)
        
        # Align lengths for comparison using defensive copies
        min_length = min(
            original_audio.shape[-1] if len(original_audio.shape) > 1 else len(original_audio),
            converted_audio.shape[-1] if len(converted_audio.shape) > 1 else len(converted_audio)
        )
        
        # Create defensive copies for quality analysis - CRITICAL FIX
        # This prevents destructive modification of original arrays
        if len(original_audio.shape) > 1:
            original_for_analysis = original_audio[:, :min_length].copy()
            converted_for_analysis = converted_audio[:, :min_length].copy()
        else:
            original_for_analysis = original_audio[:min_length].copy()
            converted_for_analysis = converted_audio[:min_length].copy()
        
        # Perform quality analysis using defensive copies
        console.print("[blue]🔬 Analyzing quality...[/blue]")
        quality_metrics = self.quality_analyzer.analyze_audio_quality(
            audio_data=converted_for_analysis,
            sample_rate=converted_sr,
            reference_data=original_for_analysis,
            file_path=output_path
        )
        
        # Display quality results
        self._display_quality_results(quality_metrics)
        
        # Determine if quality is acceptable
        quality_acceptable = quality_metrics.quality_level != QualityLevel.FAILED
        
        return {
            'success': conversion_success and quality_acceptable,
            'quality_metrics': quality_metrics,
            'input_path': str(input_path),
            'output_path': str(output_path),
            'target_format': target_format,
            'quality_warning': quality_metrics.quality_level in [QualityLevel.POOR, QualityLevel.ACCEPTABLE]
        }
    
    def _display_quality_results(self, metrics: QualityMetrics):
        """Display quality analysis results"""
        
        # Quality level with color coding
        level_colors = {
            QualityLevel.EXCELLENT: "green",
            QualityLevel.GOOD: "blue", 
            QualityLevel.ACCEPTABLE: "yellow",
            QualityLevel.POOR: "red",
            QualityLevel.FAILED: "red bold"
        }
        
        color = level_colors.get(metrics.quality_level, "white")
        console.print(f"[{color}]🎯 Quality Level: {metrics.quality_level.value.upper()}[/{color}]")
        console.print(f"[{color}]📊 Quality Score: {metrics.quality_score:.1f}/100[/{color}]")
        
        # Scientific metrics
        if metrics.thd_plus_n_db is not None:
            thd_color = "green" if metrics.thd_plus_n_db < -60 else "yellow" if metrics.thd_plus_n_db < -40 else "red"
            console.print(f"[{thd_color}]🔬 THD+N: {metrics.thd_plus_n_db:.1f} dB[/{thd_color}]")
        
        if metrics.snr_db is not None:
            snr_color = "green" if metrics.snr_db > 90 else "yellow" if metrics.snr_db > 70 else "red"
            console.print(f"[{snr_color}]📡 SNR: {metrics.snr_db:.1f} dB[/{snr_color}]")
        
        if metrics.dynamic_range_db is not None:
            dr_color = "green" if metrics.dynamic_range_db > 95 else "yellow" if metrics.dynamic_range_db > 90 else "red"
            console.print(f"[{dr_color}]📈 Dynamic Range: {metrics.dynamic_range_db:.1f}%[/{dr_color}]")
        
        # Level measurements
        if metrics.peak_level_db is not None:
            console.print(f"[cyan]🔊 Peak Level: {metrics.peak_level_db:.1f} dB[/cyan]")
        
        if metrics.rms_level_db is not None:
            console.print(f"[cyan]📏 RMS Level: {metrics.rms_level_db:.1f} dB[/cyan]")
        
        if metrics.crest_factor_db is not None:
            console.print(f"[cyan]⚡ Crest Factor: {metrics.crest_factor_db:.1f} dB[/cyan]")
        
        # Artifacts
        if metrics.artifacts_detected:
            console.print("[red]⚠ Artifacts Detected:[/red]")
            if metrics.clipping_detected:
                console.print("  [red]✗ Digital clipping[/red]")
            if metrics.aliasing_detected:
                console.print("  [red]✗ Aliasing artifacts[/red]")
            if metrics.dc_offset_detected:
                console.print("  [red]✗ DC offset[/red]")
        else:
            console.print("[green]✓ No artifacts detected[/green]")
        
        # Performance metrics
        if metrics.processing_time_ms is not None:
            time_color = "green" if metrics.processing_time_ms < 2000 else "yellow"
            console.print(f"[{time_color}]⏱ Processing Time: {metrics.processing_time_ms:.1f} ms[/{time_color}]")
        
        if metrics.memory_usage_mb is not None:
            memory_color = "green" if metrics.memory_usage_mb < 100 else "yellow"
            console.print(f"[{memory_color}]💾 Memory Usage: {metrics.memory_usage_mb:.1f} MB[/{memory_color}]")
    
    @basic_quality_check  
    def batch_convert_with_quality(self, 
                                 input_dir: Union[str, Path],
                                 output_dir: Union[str, Path], 
                                 target_format: str,
                                 quality: str = 'high') -> Dict[str, Any]:
        """
        Batch conversion with quality monitoring
        
        Returns:
            Summary of batch conversion with aggregated quality metrics
        """
        input_dir = Path(input_dir)
        output_dir = Path(output_dir)
        
        results = []
        total_files = 0
        successful_conversions = 0
        quality_issues = 0
        
        console.print(f"[blue]🔄 Batch Conversion:[/blue] {input_dir} → {target_format.upper()}")
        
        for audio_file in input_dir.glob("**/*"):
            if audio_file.suffix.lower() in self.supported_input_formats:
                total_files += 1
                
                # Determine output path
                relative_path = audio_file.relative_to(input_dir)
                output_file = output_dir / relative_path.with_suffix(f'.{target_format}')
                output_file.parent.mkdir(parents=True, exist_ok=True)
                
                # Convert with quality validation
                result = self.convert_with_quality_validation(
                    audio_file, output_file, target_format, quality
                )
                
                results.append(result)
                
                if result['success']:
                    successful_conversions += 1
                    if result.get('quality_warning', False):
                        quality_issues += 1
                
                console.print(f"[green]✓[/green] {audio_file.name} → Quality: {result['quality_metrics'].quality_level.value}")
        
        # Summary
        success_rate = (successful_conversions / total_files * 100) if total_files > 0 else 0
        quality_rate = ((successful_conversions - quality_issues) / total_files * 100) if total_files > 0 else 0
        
        console.print(f"\n[blue]📊 Batch Conversion Summary:[/blue]")
        console.print(f"[green]✓ Files processed: {total_files}[/green]")
        console.print(f"[green]✓ Successful: {successful_conversions} ({success_rate:.1f}%)[/green]")
        console.print(f"[yellow]⚠ Quality issues: {quality_issues}[/yellow]")
        console.print(f"[blue]🎯 High quality rate: {quality_rate:.1f}%[/blue]")
        
        return {
            'total_files': total_files,
            'successful_conversions': successful_conversions,
            'quality_issues': quality_issues,
            'success_rate': success_rate,
            'quality_rate': quality_rate,
            'results': results
        }


# Factory function for enhanced converter
def create_quality_converter() -> EnhancedAudioConverter:
    """Create an enhanced audio converter with quality validation"""
    return EnhancedAudioConverter()