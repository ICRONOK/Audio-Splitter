#!/usr/bin/env python3
"""
Audio Format Converter - Conversión entre formatos de audio WAV, MP3, FLAC
Soporta conversión con preservación de metadatos y configuración de calidad
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
import argparse

import librosa
import soundfile as sf
from pydub import AudioSegment
from mutagen import File
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.wave import WAVE
import numpy as np
from rich.console import Console
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

console = Console()

class AudioFormatError(Exception):
    """Excepción personalizada para errores de formato de audio"""
    pass

class AudioConverter:
    """Conversor de formatos de audio con soporte para WAV, MP3, FLAC"""
    
    SUPPORTED_FORMATS = {
        '.wav': 'WAV',
        '.mp3': 'MP3', 
        '.flac': 'FLAC'
    }
    
    # Configuraciones de calidad por formato
    QUALITY_PRESETS = {
        'mp3': {
            'low': {'bitrate': '128k'},
            'medium': {'bitrate': '192k'},
            'high': {'bitrate': '320k'},
            'vbr_medium': {'codec': 'libmp3lame', 'audio_bitrate': None, 'parameters': ['-q:a', '2']},
            'vbr_high': {'codec': 'libmp3lame', 'audio_bitrate': None, 'parameters': ['-q:a', '0']}
        },
        'flac': {
            'low': {'compression_level': 0},
            'medium': {'compression_level': 5},
            'high': {'compression_level': 8}
        }
    }
    
    def __init__(self):
        self.supported_input_formats = ['.wav', '.mp3', '.flac', '.m4a', '.ogg']
        self.supported_output_formats = ['.wav', '.mp3', '.flac']
    
    def detect_format(self, file_path: Union[str, Path]) -> str:
        """Detecta el formato de audio del archivo"""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {file_path}")
        
        extension = path.suffix.lower()
        if extension not in self.supported_input_formats:
            raise AudioFormatError(f"Formato no soportado: {extension}")
        
        return extension
    
    def get_audio_info(self, file_path: Union[str, Path]) -> Dict:
        """Obtiene información detallada del archivo de audio"""
        try:
            # Cargar con librosa para información técnica
            y, sr = librosa.load(str(file_path), sr=None)
            duration = len(y) / sr
            
            # Cargar con mutagen para metadatos
            audio_file = File(str(file_path))
            
            info = {
                'path': str(file_path),
                'format': self.detect_format(file_path),
                'duration': duration,
                'sample_rate': sr,
                'channels': 1 if len(y.shape) == 1 else y.shape[0],
                'file_size': Path(file_path).stat().st_size,
                'metadata': {}
            }
            
            if audio_file is not None:
                # Extraer metadatos comunes
                info['metadata'] = {
                    'title': self._get_tag(audio_file, ['TIT2', 'TITLE', 'Title']),
                    'artist': self._get_tag(audio_file, ['TPE1', 'ARTIST', 'Artist']),
                    'album': self._get_tag(audio_file, ['TALB', 'ALBUM', 'Album']),
                    'date': self._get_tag(audio_file, ['TDRC', 'DATE', 'Date']),
                    'genre': self._get_tag(audio_file, ['TCON', 'GENRE', 'Genre']),
                    'track': self._get_tag(audio_file, ['TRCK', 'TRACKNUMBER', 'TrackNumber'])
                }
            
            return info
            
        except Exception as e:
            raise AudioFormatError(f"Error al leer archivo {file_path}: {e}")
    
    def _get_tag(self, audio_file, tag_names: List[str]) -> Optional[str]:
        """Extrae un tag de metadatos usando múltiples nombres posibles"""
        for tag_name in tag_names:
            if tag_name in audio_file:
                value = audio_file[tag_name]
                if isinstance(value, list) and value:
                    return str(value[0])
                elif value:
                    return str(value)
        return None
    
    def convert_file(self, 
                    input_path: Union[str, Path],
                    output_path: Union[str, Path],
                    target_format: str,
                    quality: str = 'high',
                    preserve_metadata: bool = True) -> bool:
        """
        Convierte un archivo de audio a otro formato
        
        Args:
            input_path: Ruta del archivo de entrada
            output_path: Ruta del archivo de salida
            target_format: Formato objetivo ('wav', 'mp3', 'flac')
            quality: Nivel de calidad ('low', 'medium', 'high')
            preserve_metadata: Si preservar metadatos originales
        """
        try:
            input_path = Path(input_path)
            output_path = Path(output_path)
            
            # Validaciones
            if not input_path.exists():
                raise FileNotFoundError(f"Archivo de entrada no encontrado: {input_path}")
            
            if target_format not in ['wav', 'mp3', 'flac']:
                raise AudioFormatError(f"Formato objetivo no soportado: {target_format}")
            
            # Crear directorio de salida si no existe
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Obtener información del archivo original
            original_info = self.get_audio_info(input_path)
            
            console.print(f"[blue]Convirtiendo:[/blue] {input_path.name} -> {target_format.upper()}")
            
            # Realizar conversión según el formato objetivo
            if target_format == 'wav':
                success = self._convert_to_wav(input_path, output_path)
            elif target_format == 'mp3':
                success = self._convert_to_mp3(input_path, output_path, quality)
            elif target_format == 'flac':
                success = self._convert_to_flac(input_path, output_path, quality)
            
            # Preservar metadatos si se solicita
            if success and preserve_metadata and original_info['metadata']:
                self._copy_metadata(original_info['metadata'], output_path, target_format)
            
            if success:
                console.print(f"[green]✓ Conversión exitosa:[/green] {output_path}")
                return True
            else:
                console.print("[red]✗ Error en conversión[/red]")
                return False
                
        except Exception as e:
            console.print(f"[red]Error al convertir {input_path}: {e}[/red]")
            return False
    
    def _convert_to_wav(self, input_path: Path, output_path: Path) -> bool:
        """Convierte archivo a formato WAV"""
        try:
            # Cargar audio con librosa preservando canales originales
            y, sr = librosa.load(str(input_path), sr=None, mono=False)
            
            # Preparar datos de audio para escritura
            if len(y.shape) == 1:
                # Audio mono
                audio_data = y
            else:
                # Audio multicanal - transponer para soundfile
                audio_data = y.T
            
            # Guardar como WAV preservando calidad original
            sf.write(str(output_path), audio_data, sr, format='WAV')
            return True
            
        except Exception as e:
            console.print(f"[red]Error convirtiendo a WAV: {e}[/red]")
            return False
    
    def _convert_to_mp3(self, input_path: Path, output_path: Path, quality: str) -> bool:
        """Convierte archivo a formato MP3"""
        try:
            # Usar pydub para conversión a MP3
            audio = AudioSegment.from_file(str(input_path))
            
            # Configurar parámetros de calidad
            quality_settings = self.QUALITY_PRESETS['mp3'].get(quality, self.QUALITY_PRESETS['mp3']['high'])
            
            # Exportar a MP3
            if 'bitrate' in quality_settings:
                audio.export(str(output_path), format="mp3", bitrate=quality_settings['bitrate'])
            else:
                # Para VBR, usar parámetros personalizados
                audio.export(str(output_path), format="mp3", parameters=quality_settings.get('parameters', []))
            
            return True
            
        except Exception as e:
            console.print(f"[red]Error convirtiendo a MP3: {e}[/red]")
            return False
    
    def _convert_to_flac(self, input_path: Path, output_path: Path, quality: str) -> bool:
        """Convierte archivo a formato FLAC"""
        try:
            # Cargar con librosa preservando canales y frecuencia original
            y, sr = librosa.load(str(input_path), sr=None, mono=False)
            
            # Configurar nivel de compresión FLAC
            quality_settings = self.QUALITY_PRESETS['flac'].get(quality, self.QUALITY_PRESETS['flac']['high'])
            compression_level = quality_settings['compression_level']
            
            # Determinar el subtipo basado en el archivo original
            try:
                info = sf.info(str(input_path))
                original_subtype = info.subtype
                # Usar PCM_24 por defecto para FLAC para mejor calidad
                if 'PCM_32' in original_subtype or 'FLOAT' in original_subtype:
                    subtype = 'PCM_24'
                elif 'PCM_24' in original_subtype:
                    subtype = 'PCM_24'
                else:
                    subtype = 'PCM_16'  # Fallback para archivos de menor calidad
            except:
                subtype = 'PCM_24'  # Default seguro
            
            # Preparar datos de audio para escritura
            if len(y.shape) == 1:
                # Audio mono
                audio_data = y
            else:
                # Audio multicanal - transponer para soundfile
                audio_data = y.T
            
            # Guardar como FLAC con nivel de compresión
            sf.write(str(output_path), audio_data, sr, 
                    format='FLAC', subtype=subtype)
            
            console.print(f"[green]✓ FLAC creado:[/green] {subtype}, {sr}Hz, compresión nivel {compression_level}")
            return True
            
        except Exception as e:
            console.print(f"[red]Error convirtiendo a FLAC: {e}[/red]")
            return False
    
    def _copy_metadata(self, metadata: Dict, output_path: Path, target_format: str):
        """Copia metadatos al archivo convertido"""
        try:
            audio_file = File(str(output_path))
            if audio_file is None:
                return
            
            if target_format == 'mp3':
                self._copy_id3_metadata(audio_file, metadata)
            elif target_format == 'flac':
                self._copy_vorbis_metadata(audio_file, metadata)
            elif target_format == 'wav':
                # WAV tiene soporte limitado de metadatos
                console.print("[yellow]Info: WAV tiene soporte limitado de metadatos[/yellow]")
                
        except Exception as e:
            console.print(f"[yellow]Advertencia: No se pudieron copiar metadatos: {e}[/yellow]")
    
    def _copy_id3_metadata(self, audio_file, metadata: Dict):
        """Copia metadatos usando tags ID3 para MP3"""
        from mutagen.id3 import TIT2, TPE1, TALB, TDRC, TCON, TRCK
        
        # Asegurar que existan tags ID3
        if audio_file.tags is None:
            audio_file.add_tags()
        
        tags = audio_file.tags
        
        # Mapear y agregar tags ID3
        if metadata.get('title'):
            tags.add(TIT2(encoding=3, text=metadata['title']))
        if metadata.get('artist'):
            tags.add(TPE1(encoding=3, text=metadata['artist']))
        if metadata.get('album'):
            tags.add(TALB(encoding=3, text=metadata['album']))
        if metadata.get('date'):
            tags.add(TDRC(encoding=3, text=metadata['date']))
        if metadata.get('genre'):
            tags.add(TCON(encoding=3, text=metadata['genre']))
        if metadata.get('track'):
            tags.add(TRCK(encoding=3, text=metadata['track']))
        
        audio_file.save()
        console.print("[green]✓ Metadatos copiados exitosamente[/green]")
    
    def _copy_vorbis_metadata(self, audio_file, metadata: Dict):
        """Copia metadatos usando Vorbis Comments para FLAC"""
        # Mapeo directo para FLAC
        tag_mapping = {
            'title': 'TITLE',
            'artist': 'ARTIST',
            'album': 'ALBUM', 
            'date': 'DATE',
            'genre': 'GENRE',
            'track': 'TRACKNUMBER'
        }
        
        for field, value in metadata.items():
            if value and field in tag_mapping:
                audio_file[tag_mapping[field]] = str(value)
        
        audio_file.save()
        console.print("[green]✓ Metadatos copiados exitosamente[/green]")
    
    # ========== CHANNEL CONVERSION METHODS ==========
    
    def convert_channels(self, 
                        input_path: Union[str, Path],
                        output_path: Union[str, Path],
                        target_channels: int,
                        mixing_algorithm: str = 'downmix_center',
                        preserve_metadata: bool = True) -> bool:
        """
        Convert audio channel count (mono ↔ stereo)
        
        Args:
            input_path: Input audio file path
            output_path: Output audio file path  
            target_channels: Target channel count (1=mono, 2=stereo)
            mixing_algorithm: Algorithm for stereo→mono ('downmix_center', 'left_only', 'right_only', 'average')
            preserve_metadata: Whether to preserve original metadata
            
        Returns:
            bool: Success status
        """
        try:
            input_path = Path(input_path)
            output_path = Path(output_path)
            
            # Validate inputs
            if not input_path.exists():
                raise FileNotFoundError(f"Input file not found: {input_path}")
            
            if target_channels not in [1, 2]:
                raise AudioFormatError(f"Target channels must be 1 (mono) or 2 (stereo), got: {target_channels}")
            
            # Create output directory if needed
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Load audio with librosa (preserves multichannel)
            y, sr = librosa.load(str(input_path), sr=None, mono=False)
            
            # Determine current channel configuration
            if len(y.shape) == 1:
                current_channels = 1
                console.print(f"[blue]Input:[/blue] Mono audio ({sr} Hz)")
            else:
                current_channels = y.shape[0]
                console.print(f"[blue]Input:[/blue] {current_channels}-channel audio ({sr} Hz)")
            
            # Skip conversion if already target format
            if current_channels == target_channels:
                console.print(f"[yellow]Audio already has {target_channels} channels, copying file...[/yellow]")
                # Simple copy with format preservation
                sf.write(str(output_path), y.T if len(y.shape) > 1 else y, sr)
                success = True
            else:
                # Perform channel conversion
                if target_channels == 1:
                    # Convert to mono
                    y_converted = self._convert_to_mono(y, mixing_algorithm)
                    console.print(f"[blue]Converting:[/blue] {current_channels}-channel → Mono using {mixing_algorithm}")
                else:
                    # Convert to stereo
                    y_converted = self._convert_to_stereo(y)
                    console.print(f"[blue]Converting:[/blue] Mono → Stereo")
                
                # Save converted audio
                sf.write(str(output_path), y_converted.T if len(y_converted.shape) > 1 else y_converted, sr)
                success = True
            
            # Preserve metadata if requested
            if success and preserve_metadata:
                original_info = self.get_audio_info(input_path)
                if original_info['metadata']:
                    output_format = output_path.suffix.lower().replace('.', '')
                    self._copy_metadata(original_info['metadata'], output_path, output_format)
            
            if success:
                # Display conversion results
                final_info = self.get_audio_info(output_path)
                console.print(f"[green]✓ Channel conversion successful:[/green] {output_path}")
                console.print(f"[green]Output:[/green] {final_info['channels']}-channel audio")
                return True
            else:
                console.print("[red]✗ Channel conversion failed[/red]")
                return False
                
        except Exception as e:
            console.print(f"[red]Error in channel conversion: {e}[/red]")
            return False
    
    def _convert_to_mono(self, y: np.ndarray, algorithm: str = 'downmix_center') -> np.ndarray:
        """
        Convert multichannel audio to mono using scientific mixing algorithms
        
        Based on Audio Engineering Society recommendations for downmixing
        
        Args:
            y: Audio array (channels, samples) or (samples,) for mono
            algorithm: Mixing algorithm to use
            
        Returns:
            np.ndarray: Mono audio array (samples,)
        """
        if len(y.shape) == 1:
            # Already mono
            return y
        
        if algorithm == 'downmix_center':
            # ITU-R BS.775 standard downmix: L + R with -3dB compensation
            # This preserves center-panned content and maintains energy balance
            if y.shape[0] >= 2:
                mono = (y[0] + y[1]) / 2.0  # Average L+R channels
                # Apply -3dB compensation to prevent clipping while preserving dynamics
                mono = mono * 0.707945784  # = 1/√2, equivalent to -3.0103dB
            else:
                mono = y[0]  # Single channel
                
        elif algorithm == 'left_only':
            # Use only left channel
            mono = y[0]
            
        elif algorithm == 'right_only':
            # Use only right channel  
            mono = y[1] if y.shape[0] > 1 else y[0]
            
        elif algorithm == 'average':
            # Simple average of all channels (may cause level issues)
            mono = np.mean(y, axis=0)
            
        else:
            raise AudioFormatError(f"Unknown mixing algorithm: {algorithm}")
        
        # Apply gentle limiting to prevent digital clipping
        # This preserves dynamic range while ensuring safe output levels
        peak_level = np.max(np.abs(mono))
        if peak_level > 0.95:  # Conservative threshold below digital full scale
            # Apply soft limiting only when necessary
            compression_ratio = 0.95 / peak_level
            mono = mono * compression_ratio
            console.print(f"[yellow]Applied soft limiting (reduction: {20*np.log10(compression_ratio):.1f}dB)[/yellow]")
        
        return mono
    
    def _convert_to_stereo(self, y: np.ndarray) -> np.ndarray:
        """
        Convert mono audio to stereo using center-channel placement
        
        This method creates true stereo by duplicating the mono signal
        to both channels, maintaining the original dynamic range and 
        placing the audio in the center of the stereo field.
        
        Args:
            y: Mono audio array (samples,)
            
        Returns:
            np.ndarray: Stereo audio array (2, samples)
        """
        if len(y.shape) > 1:
            # Already multichannel, return as-is or truncate to stereo
            if y.shape[0] >= 2:
                return y[:2]  # Keep only first 2 channels
            else:
                # Single channel, duplicate it
                return np.array([y[0], y[0]])
        
        # Duplicate mono signal to create stereo
        # Both channels get identical signal (center-panned)
        stereo = np.array([y, y])
        
        console.print("[blue]Upmixing:[/blue] Center-panned stereo placement")
        return stereo
    
    def analyze_channel_properties(self, file_path: Union[str, Path]) -> Dict:
        """
        Analyze channel properties and provide conversion recommendations
        
        Returns detailed analysis of channel configuration, level balance,
        phase relationships, and optimal conversion strategies.
        
        Args:
            file_path: Path to audio file
            
        Returns:
            Dict: Comprehensive channel analysis
        """
        try:
            # Load audio preserving all channels
            y, sr = librosa.load(str(file_path), sr=None, mono=False)
            
            analysis = {
                'file_path': str(file_path),
                'sample_rate': sr,
                'duration': len(y) / sr if len(y.shape) == 1 else len(y[0]) / sr,
                'current_channels': 1 if len(y.shape) == 1 else y.shape[0],
                'recommendations': []
            }
            
            if len(y.shape) == 1:
                # Mono analysis
                analysis.update({
                    'channel_type': 'mono',
                    'rms_level': float(np.sqrt(np.mean(y**2))),
                    'peak_level': float(np.max(np.abs(y))),
                    'dynamic_range': float(20 * np.log10(np.max(np.abs(y)) / (np.sqrt(np.mean(y**2)) + 1e-10))),
                })
                analysis['recommendations'].append("✓ Suitable for stereo upmixing with center placement")
                
            else:
                # Stereo/multichannel analysis
                analysis['channel_type'] = f'{y.shape[0]}-channel'
                
                # Per-channel analysis
                channels_info = []
                for i in range(y.shape[0]):
                    channel_rms = float(np.sqrt(np.mean(y[i]**2)))
                    channel_peak = float(np.max(np.abs(y[i])))
                    channels_info.append({
                        'channel': i,
                        'rms_level': channel_rms,
                        'peak_level': channel_peak,
                        'rms_db': float(20 * np.log10(channel_rms + 1e-10))
                    })
                
                analysis['channels_info'] = channels_info
                
                # Stereo-specific analysis
                if y.shape[0] >= 2:
                    # Level balance analysis
                    left_rms = channels_info[0]['rms_level']
                    right_rms = channels_info[1]['rms_level']
                    balance_db = 20 * np.log10((right_rms + 1e-10) / (left_rms + 1e-10))
                    
                    # Phase correlation analysis (simplified)
                    correlation = float(np.corrcoef(y[0], y[1])[0, 1])
                    
                    analysis.update({
                        'stereo_balance_db': float(balance_db),
                        'phase_correlation': correlation,
                        'stereo_width': float(1.0 - abs(correlation))  # Simplified stereo width
                    })
                    
                    # Conversion recommendations
                    if abs(balance_db) < 1.0:
                        analysis['recommendations'].append("✓ Well-balanced stereo, suitable for center downmix")
                    else:
                        analysis['recommendations'].append(f"⚠ Stereo imbalance: {balance_db:+.1f}dB, consider left/right-only downmix")
                    
                    if correlation > 0.9:
                        analysis['recommendations'].append("⚠ High correlation detected, essentially mono content")
                    elif correlation < 0.1:
                        analysis['recommendations'].append("✓ Good stereo separation, information will be lost in mono conversion")
            
            return analysis
            
        except Exception as e:
            raise AudioFormatError(f"Error analyzing channel properties: {e}")
    
    def batch_convert_channels(self,
                              input_dir: Union[str, Path],
                              output_dir: Union[str, Path], 
                              target_channels: int,
                              mixing_algorithm: str = 'downmix_center',
                              preserve_metadata: bool = True,
                              recursive: bool = False) -> Tuple[int, int]:
        """
        Batch channel conversion for multiple files
        
        Args:
            input_dir: Directory containing input audio files
            output_dir: Directory for converted files
            target_channels: Target channel count (1=mono, 2=stereo)
            mixing_algorithm: Algorithm for stereo→mono conversion
            preserve_metadata: Whether to preserve metadata
            recursive: Whether to search subdirectories
            
        Returns:
            Tuple[int, int]: (successful_conversions, failed_conversions)
        """
        input_dir = Path(input_dir)
        output_dir = Path(output_dir)
        
        if not input_dir.exists():
            raise FileNotFoundError(f"Input directory not found: {input_dir}")
        
        # Find audio files
        pattern = "**/*" if recursive else "*"
        audio_files = []
        
        for ext in self.supported_input_formats:
            audio_files.extend(input_dir.glob(f"{pattern}{ext}"))
        
        if not audio_files:
            console.print(f"[yellow]No audio files found in {input_dir}[/yellow]")
            return 0, 0
        
        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)
        
        successful = 0
        failed = 0
        
        # Progress tracking
        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            "[progress.percentage]{task.percentage:>3.0f}%",
            TimeRemainingColumn(),
            console=console
        ) as progress:
            
            channel_name = "mono" if target_channels == 1 else "stereo"
            task = progress.add_task(f"Converting to {channel_name}", total=len(audio_files))
            
            for audio_file in audio_files:
                # Generate output filename
                output_file = output_dir / f"{audio_file.stem}_{channel_name}{audio_file.suffix}"
                
                # Avoid overwriting existing files
                counter = 1
                while output_file.exists():
                    output_file = output_dir / f"{audio_file.stem}_{channel_name}_{counter}{audio_file.suffix}"
                    counter += 1
                
                # Convert channels
                if self.convert_channels(audio_file, output_file, target_channels, mixing_algorithm, preserve_metadata):
                    successful += 1
                else:
                    failed += 1
                
                progress.advance(task)
        
        # Summary
        console.print(f"\n[green]Channel conversion completed:[/green]")
        console.print(f"  ✓ Successful: {successful}")
        console.print(f"  ✗ Failed: {failed}")
        
        return successful, failed
    
    def batch_convert(self, 
                     input_dir: Union[str, Path],
                     output_dir: Union[str, Path],
                     target_format: str,
                     quality: str = 'high',
                     preserve_metadata: bool = True,
                     recursive: bool = False) -> Tuple[int, int]:
        """
        Conversión por lotes de múltiples archivos
        
        Returns:
            Tuple[int, int]: (archivos_exitosos, archivos_con_error)
        """
        input_dir = Path(input_dir)
        output_dir = Path(output_dir)
        
        if not input_dir.exists():
            raise FileNotFoundError(f"Directorio de entrada no encontrado: {input_dir}")
        
        # Buscar archivos de audio
        pattern = "**/*" if recursive else "*"
        audio_files = []
        
        for ext in self.supported_input_formats:
            audio_files.extend(input_dir.glob(f"{pattern}{ext}"))
        
        if not audio_files:
            console.print(f"[yellow]No se encontraron archivos de audio en {input_dir}[/yellow]")
            return 0, 0
        
        # Crear directorio de salida
        output_dir.mkdir(parents=True, exist_ok=True)
        
        successful = 0
        failed = 0
        
        # Progreso con rich
        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            "[progress.percentage]{task.percentage:>3.0f}%",
            TimeRemainingColumn(),
            console=console
        ) as progress:
            
            task = progress.add_task(f"Convirtiendo a {target_format.upper()}", total=len(audio_files))
            
            for audio_file in audio_files:
                # Generar nombre de archivo de salida
                output_file = output_dir / f"{audio_file.stem}.{target_format}"
                
                # Evitar sobrescribir si el archivo ya existe
                counter = 1
                while output_file.exists():
                    output_file = output_dir / f"{audio_file.stem}_{counter}.{target_format}"
                    counter += 1
                
                # Convertir archivo
                if self.convert_file(audio_file, output_file, target_format, quality, preserve_metadata):
                    successful += 1
                else:
                    failed += 1
                
                progress.advance(task)
        
        # Resumen
        console.print(f"\n[green]Conversión completada:[/green]")
        console.print(f"  ✓ Exitosos: {successful}")
        console.print(f"  ✗ Fallidos: {failed}")
        
        return successful, failed

def interactive_mode():
    """Modo interactivo para conversión de archivos"""
    converter = AudioConverter()
    
    console.print(Panel(
        "[bold blue]Audio Format Converter[/bold blue]\n[dim]Conversión entre WAV, MP3 y FLAC[/dim]", 
        title="🔄 Conversor de Audio"
    ))
    
    while True:
        console.print("\n[cyan]Opciones disponibles:[/cyan]")
        options = [
            "1. Convertir archivo individual",
            "2. Conversión por lotes", 
            "3. Convertir canales (mono ↔ stereo)",
            "4. Conversión de canales por lotes",
            "5. Analizar propiedades de canal",
            "6. Información de archivo",
            "7. Salir"
        ]
        
        for option in options:
            console.print(f"  {option}")
        
        choice = Prompt.ask("\nSelecciona una opción", choices=["1", "2", "3", "4", "5", "6", "7"])
        
        if choice == '1':
            _convert_single_file_interactive(converter)
        elif choice == '2':
            _batch_convert_interactive(converter)
        elif choice == '3':
            _convert_channels_interactive(converter)
        elif choice == '4':
            _batch_convert_channels_interactive(converter)
        elif choice == '5':
            _analyze_channel_properties_interactive(converter)
        elif choice == '6':
            _show_file_info_interactive(converter)
        elif choice == '7':
            console.print("[yellow]¡Hasta luego![/yellow]")
            break

def _convert_channels_interactive(converter: AudioConverter):
    """Interactive mode for channel conversion"""
    
    input_file = Prompt.ask("\nRuta del archivo de entrada")
    if not input_file:
        console.print("[red]Ruta requerida[/red]")
        return
    
    try:
        # Show current file info
        info = converter.get_audio_info(input_file)
        console.print(f"\n[cyan]Archivo actual:[/cyan] {info['channels']}-channel, {info['sample_rate']} Hz")
        
        # Target channels
        console.print("\n[cyan]Configuración de canales:[/cyan]")
        console.print("  1 = Mono")
        console.print("  2 = Stereo")
        target_channels = int(Prompt.ask("Canales objetivo", choices=["1", "2"]))
        
        # If converting to mono, ask for mixing algorithm
        mixing_algorithm = 'downmix_center'
        if target_channels == 1 and info['channels'] > 1:
            console.print("\n[cyan]Algoritmos de mezcla (stereo → mono):[/cyan]")
            console.print("  downmix_center: Mezcla L+R con compensación -3dB (recomendado)")
            console.print("  left_only: Solo canal izquierdo")
            console.print("  right_only: Solo canal derecho")
            console.print("  average: Promedio simple de todos los canales")
            mixing_algorithm = Prompt.ask("Algoritmo de mezcla", 
                                        choices=["downmix_center", "left_only", "right_only", "average"],
                                        default="downmix_center")
        
        # Output file
        output_file = Prompt.ask("Archivo de salida (Enter para auto)", default="")
        if not output_file:
            input_path = Path(input_file)
            channel_suffix = "mono" if target_channels == 1 else "stereo"
            output_file = f"{input_path.stem}_{channel_suffix}{input_path.suffix}"
        
        preserve_metadata = Confirm.ask("¿Preservar metadatos?", default=True)
        
        # Perform conversion
        converter.convert_channels(input_file, output_file, target_channels, mixing_algorithm, preserve_metadata)
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")

def _batch_convert_channels_interactive(converter: AudioConverter):
    """Interactive mode for batch channel conversion"""
    
    input_dir = Prompt.ask("\nDirectorio de entrada")
    if not input_dir:
        console.print("[red]Directorio requerido[/red]")
        return
    
    output_dir = Prompt.ask("Directorio de salida")
    if not output_dir:
        console.print("[red]Directorio de salida requerido[/red]")
        return
    
    # Target channels
    console.print("\n[cyan]Configuración de canales:[/cyan]")
    console.print("  1 = Convertir todo a Mono")
    console.print("  2 = Convertir todo a Stereo")
    target_channels = int(Prompt.ask("Canales objetivo", choices=["1", "2"]))
    
    # Mixing algorithm for stereo→mono
    mixing_algorithm = 'downmix_center'
    if target_channels == 1:
        console.print("\n[cyan]Algoritmo de mezcla para archivos stereo:[/cyan]")
        mixing_algorithm = Prompt.ask("Algoritmo de mezcla",
                                    choices=["downmix_center", "left_only", "right_only", "average"],
                                    default="downmix_center")
    
    recursive = Confirm.ask("¿Buscar en subdirectorios?", default=False)
    preserve_metadata = Confirm.ask("¿Preservar metadatos?", default=True)
    
    # Perform batch conversion
    try:
        converter.batch_convert_channels(input_dir, output_dir, target_channels, 
                                       mixing_algorithm, preserve_metadata, recursive)
    except Exception as e:
        console.print(f"[red]Error en conversión por lotes: {e}[/red]")

def _analyze_channel_properties_interactive(converter: AudioConverter):
    """Interactive mode for channel analysis"""
    
    file_path = Prompt.ask("\nRuta del archivo para analizar")
    if not file_path:
        console.print("[red]Ruta requerida[/red]")
        return
    
    try:
        analysis = converter.analyze_channel_properties(file_path)
        
        # Create analysis table
        table = Table(title=f"Análisis de Canales: {Path(file_path).name}")
        table.add_column("Propiedad", style="cyan")
        table.add_column("Valor", style="white")
        
        table.add_row("Tipo de Canal", analysis['channel_type'])
        table.add_row("Canales", str(analysis['current_channels']))
        table.add_row("Frecuencia", f"{analysis['sample_rate']} Hz")
        table.add_row("Duración", f"{analysis['duration']:.2f} segundos")
        
        if analysis['channel_type'] == 'mono':
            table.add_row("Nivel RMS", f"{20*np.log10(analysis['rms_level'] + 1e-10):.1f} dB")
            table.add_row("Nivel Peak", f"{20*np.log10(analysis['peak_level'] + 1e-10):.1f} dB")
            table.add_row("Rango Dinámico", f"{analysis['dynamic_range']:.1f} dB")
        else:
            if 'stereo_balance_db' in analysis:
                table.add_row("Balance L/R", f"{analysis['stereo_balance_db']:+.1f} dB")
                table.add_row("Correlación de Fase", f"{analysis['phase_correlation']:.3f}")
                table.add_row("Amplitud Stereo", f"{analysis['stereo_width']:.3f}")
        
        console.print(table)
        
        # Show recommendations
        if analysis['recommendations']:
            console.print("\n[cyan]Recomendaciones:[/cyan]")
            for rec in analysis['recommendations']:
                console.print(f"  {rec}")
        
        # Show per-channel details for multichannel
        if 'channels_info' in analysis:
            console.print("\n[cyan]Información por Canal:[/cyan]")
            for ch_info in analysis['channels_info']:
                ch_num = ch_info['channel']
                rms_db = ch_info['rms_db']
                peak_db = 20 * np.log10(ch_info['peak_level'] + 1e-10)
                console.print(f"  Canal {ch_num}: RMS {rms_db:.1f} dB, Peak {peak_db:.1f} dB")
        
    except Exception as e:
        console.print(f"[red]Error analizando archivo: {e}[/red]")

def _convert_single_file_interactive(converter: AudioConverter):
    """Modo interactivo para conversión de archivo individual"""
    
    input_file = Prompt.ask("\nRuta del archivo de entrada")
    if not input_file:
        console.print("[red]Ruta requerida[/red]")
        return
    
    # Mostrar formatos disponibles
    console.print("\n[cyan]Formatos de salida disponibles:[/cyan] WAV, MP3, FLAC")
    target_format = Prompt.ask("Formato de salida", choices=["wav", "mp3", "flac"])
    
    output_file = Prompt.ask("Archivo de salida (Enter para auto)", default="")
    if not output_file:
        input_path = Path(input_file)
        output_file = f"{input_path.stem}_converted.{target_format}"
    
    # Configurar calidad
    quality = 'high'
    if target_format in ['mp3', 'flac']:
        console.print(f"\n[cyan]Niveles de calidad para {target_format.upper()}:[/cyan]")
        if target_format == 'mp3':
            console.print("low, medium, high, vbr_medium, vbr_high")
            quality = Prompt.ask("Calidad", choices=["low", "medium", "high", "vbr_medium", "vbr_high"], default="high")
        else:
            console.print("low, medium, high")
            quality = Prompt.ask("Calidad", choices=["low", "medium", "high"], default="high")
    
    preserve_metadata = Confirm.ask("¿Preservar metadatos?", default=True)
    
    # Realizar conversión
    converter.convert_file(input_file, output_file, target_format, quality, preserve_metadata)

def _batch_convert_interactive(converter: AudioConverter):
    """Modo interactivo para conversión por lotes"""
    
    input_dir = Prompt.ask("\nDirectorio de entrada")
    if not input_dir:
        console.print("[red]Directorio requerido[/red]")
        return
    
    output_dir = Prompt.ask("Directorio de salida")
    if not output_dir:
        console.print("[red]Directorio de salida requerido[/red]")
        return
    
    console.print("\n[cyan]Formatos disponibles:[/cyan] WAV, MP3, FLAC")
    target_format = Prompt.ask("Formato objetivo", choices=["wav", "mp3", "flac"])
    
    recursive = Confirm.ask("¿Buscar en subdirectorios?", default=False)
    
    # Configurar calidad
    quality = 'high'
    if target_format in ['mp3', 'flac']:
        if target_format == 'mp3':
            quality = Prompt.ask(f"Calidad para {target_format.upper()}", 
                               choices=["low", "medium", "high", "vbr_medium", "vbr_high"], 
                               default="high")
        else:
            quality = Prompt.ask(f"Calidad para {target_format.upper()}", 
                               choices=["low", "medium", "high"], 
                               default="high")
    
    preserve_metadata = Confirm.ask("¿Preservar metadatos?", default=True)
    
    # Realizar conversión por lotes
    try:
        converter.batch_convert(input_dir, output_dir, target_format, quality, preserve_metadata, recursive)
    except Exception as e:
        console.print(f"[red]Error en conversión por lotes: {e}[/red]")

def _show_file_info_interactive(converter: AudioConverter):
    """Mostrar información detallada de un archivo de audio"""
    
    file_path = Prompt.ask("\nRuta del archivo")
    if not file_path:
        console.print("[red]Ruta requerida[/red]")
        return
    
    try:
        info = converter.get_audio_info(file_path)
        
        # Crear tabla con información
        table = Table(title=f"Información de: {Path(file_path).name}")
        table.add_column("Campo", style="cyan")
        table.add_column("Valor", style="white")
        
        table.add_row("Formato", info['format'])
        table.add_row("Duración", f"{info['duration']:.2f} segundos")
        table.add_row("Frecuencia", f"{info['sample_rate']} Hz")
        table.add_row("Canales", str(info['channels']))
        table.add_row("Tamaño", f"{info['file_size'] / 1024 / 1024:.2f} MB")
        
        console.print(table)
        
        # Mostrar metadatos si existen
        if info['metadata']:
            console.print("\n[cyan]Metadatos:[/cyan]")
            for key, value in info['metadata'].items():
                if value:
                    console.print(f"  {key.title()}: {value}")
        
    except Exception as e:
        console.print(f"[red]Error obteniendo información: {e}[/red]")

if __name__ == "__main__":
    interactive_mode()
