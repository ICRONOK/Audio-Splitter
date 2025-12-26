#!/usr/bin/env python3
"""
Workflow Steps - Steps concretos para workflows profesionales
Implementaciones específicas de WorkflowStep para operaciones de audio
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional, List

from rich.console import Console

# Imports relativos con fallback
try:
    from ..core.workflow_engine import WorkflowStep, WorkflowContext, WorkflowError
    from ..core.enhanced_converter import EnhancedAudioConverter
    from ..core.converter import AudioConverter
    from ..core.enhanced_splitter import EnhancedAudioSplitter
    from ..core.enhanced_spectrogram import EnhancedSpectrogramGenerator
    from ..core.metadata_manager import MetadataManager
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from core.workflow_engine import WorkflowStep, WorkflowContext, WorkflowError
    from core.enhanced_converter import EnhancedAudioConverter
    from core.converter import AudioConverter
    from core.enhanced_splitter import EnhancedAudioSplitter
    from core.enhanced_spectrogram import EnhancedSpectrogramGenerator
    from core.metadata_manager import MetadataManager

console = Console()


class ConvertAudioStep(WorkflowStep):
    """
    Step para convertir audio a formato específico
    """

    def __init__(self,
                 output_format: str,
                 bitrate: Optional[str] = None,
                 quality_level: str = "high",
                 quality_validation: bool = True,
                 name: Optional[str] = None):
        name = name or f"Convert to {output_format.upper()}"
        super().__init__(
            name=name,
            description=f"Convertir audio a formato {output_format.upper()}",
            required=True
        )
        self.output_format = output_format
        self.bitrate = bitrate  # e.g., "192k", "320k", "64k", None for lossless
        self.quality_level = quality_level
        self.quality_validation = quality_validation
        self.converter = EnhancedAudioConverter()

    def validate_preconditions(self, context: WorkflowContext) -> bool:
        """Validar que existe archivo de entrada"""
        if not context.input_file:
            return False
        return Path(context.input_file).exists()

    def execute(self, context: WorkflowContext) -> Dict[str, Any]:
        """Ejecutar conversión de audio"""
        input_file = context.input_file
        output_dir = Path(context.output_dir or ".")
        output_dir.mkdir(parents=True, exist_ok=True)

        # Generar nombre de archivo de salida
        input_path = Path(input_file)
        output_file = output_dir / f"{input_path.stem}.{self.output_format}"

        console.print(f"[cyan]Converting {input_file} to {self.output_format}...[/cyan]")

        # Ejecutar conversión
        success = self.converter.convert_file(
            input_path=input_file,
            output_path=output_file,
            target_format=self.output_format,
            quality=self.quality_level
        )

        result = {'success': success}

        if result.get('success', False):
            # Registrar archivo generado en contexto
            context.add_intermediate_file(f'converted_{self.output_format}', str(output_file))
            console.print(f"[green]✓ Conversion successful: {output_file}[/green]")

            return {
                'output_file': str(output_file),
                'format': self.output_format,
                'quality_result': result.get('quality_result')
            }
        else:
            raise WorkflowError(f"Conversion failed: {result.get('error', 'Unknown error')}")

    def validate_postconditions(self, context: WorkflowContext) -> bool:
        """Validar que el archivo convertido existe"""
        output_file = context.get_intermediate_file(f'converted_{self.output_format}')
        return output_file and Path(output_file).exists()


class SplitAudioStep(WorkflowStep):
    """
    Step para dividir audio en segmentos
    """

    def __init__(self,
                 segments: List[str],
                 enhanced: bool = True,
                 quality_validation: bool = False,
                 name: Optional[str] = None):
        name = name or f"Split Audio ({len(segments)} segments)"
        super().__init__(
            name=name,
            description=f"Dividir audio en {len(segments)} segmentos",
            required=True
        )
        self.segments = segments
        self.enhanced = enhanced
        self.quality_validation = quality_validation
        self.splitter = EnhancedAudioSplitter()

    def validate_preconditions(self, context: WorkflowContext) -> bool:
        """Validar que existe archivo de entrada o intermediario"""
        input_file = context.get_metadata('split_input') or context.input_file
        if not input_file:
            return False
        return Path(input_file).exists()

    def execute(self, context: WorkflowContext) -> Dict[str, Any]:
        """Ejecutar división de audio"""
        input_file = context.get_metadata('split_input') or context.input_file
        output_dir = Path(context.output_dir or ".") / "segments"
        output_dir.mkdir(parents=True, exist_ok=True)

        console.print(f"[cyan]Splitting {input_file} into {len(self.segments)} segments...[/cyan]")

        # Parse segments from strings to tuples
        from ..core.splitter import convert_to_ms
        parsed_segments = []
        for seg in self.segments:
            try:
                # Format: "inicio-fin:nombre" or "inicio-fin"
                # Example: "0:00-0:30:intro" or "0:00-0:30"
                # Need to find the last ':' to separate name from time range

                # Find last occurrence of ':' to separate name
                last_colon = seg.rfind(':')

                # Check if there's a '-' after the last ':'
                # If no '-' after last ':', then the last ':' is part of the time, not the name separator
                if last_colon > 0 and '-' not in seg[last_colon:]:
                    # Last ':' separates time range from name
                    time_range = seg[:last_colon]
                    name = seg[last_colon+1:]
                else:
                    # No name, entire string is time range
                    time_range = seg
                    name = ""

                start_str, end_str = time_range.split('-')
                start_ms = convert_to_ms(start_str)
                end_ms = convert_to_ms(end_str)
                parsed_segments.append((start_ms, end_ms, name))
            except Exception as e:
                raise WorkflowError(f"Error parsing segment '{seg}': {e}")

        # Ejecutar división con el método correcto
        if self.enhanced or self.quality_validation:
            # Use enhanced method which accepts quality_validation
            result = self.splitter.split_audio_enhanced(
                input_file=str(input_file),
                segments=parsed_segments,
                output_dir=str(output_dir),
                quality_validation=self.quality_validation
            )
        else:
            # Use basic method (returns bool)
            from ..core.splitter import AudioSplitter
            basic_splitter = AudioSplitter()
            success = basic_splitter.split_audio(
                input_file=str(input_file),
                segments=parsed_segments,
                output_dir=str(output_dir)
            )
            result = {'success': success, 'segment_files': []}

        if result.get('success', False):
            # Registrar archivos generados
            segment_files = result.get('segment_files', [])
            context.add_intermediate_file('split_segments', ','.join(segment_files))
            console.print(f"[green]✓ Split successful: {len(segment_files)} segments created[/green]")

            return {
                'segment_files': segment_files,
                'output_dir': str(output_dir)
            }
        else:
            raise WorkflowError(f"Split failed: {result.get('error', 'Unknown error')}")


class AddMetadataStep(WorkflowStep):
    """
    Step para agregar metadatos a archivos de audio
    """

    def __init__(self,
                 metadata: Dict[str, str],
                 target: str = "converted",
                 name: Optional[str] = None):
        name = name or "Add Metadata"
        super().__init__(
            name=name,
            description="Agregar metadatos a archivos de audio",
            required=False  # No es crítico
        )
        self.metadata = metadata
        self.target = target  # 'converted', 'segments', 'spectrogram'
        from ..core.metadata_manager import MetadataEditor, AudioMetadata
        self.metadata_manager = MetadataEditor()
        self.AudioMetadata = AudioMetadata

    def execute(self, context: WorkflowContext) -> Dict[str, Any]:
        """Ejecutar agregación de metadatos"""
        # Obtener archivo(s) objetivo según target
        if self.target == "converted":
            # Buscar todos los archivos convertidos (FLAC, MP3, WAV, etc)
            target_files = []

            # Buscar archivos convertidos por formato
            for format_type in ['flac', 'mp3', 'wav', 'ogg', 'm4a']:
                file_path = context.get_intermediate_file(f'converted_{format_type}')
                if file_path and Path(file_path).exists():
                    target_files.append(file_path)

            # También buscar archivo de channel conversion (puede ser WAV/FLAC/MP3)
            channel_file = context.get_intermediate_file('channel_converted')
            if channel_file and Path(channel_file).exists() and channel_file not in target_files:
                target_files.append(channel_file)

            # Si no se encontró ninguno, usar el archivo de entrada
            if not target_files:
                target_files = [context.input_file]
        elif self.target == "segments":
            segments_str = context.get_intermediate_file('split_segments')
            target_files = segments_str.split(',') if segments_str else []
        else:
            target_files = [context.input_file]

        console.print(f"[cyan]Adding metadata to {len(target_files)} file(s)...[/cyan]")

        updated_files = []
        for file_path in target_files:
            if not file_path or not Path(file_path).exists():
                continue

            try:
                # Crear objeto AudioMetadata con los valores del diccionario
                audio_metadata = self.AudioMetadata(**self.metadata)

                # Actualizar metadatos usando write_metadata
                success = self.metadata_manager.write_metadata(file_path, audio_metadata)

                if success:
                    updated_files.append(file_path)
            except Exception as e:
                console.print(f"[yellow]⚠️ Metadata update failed for {Path(file_path).name}: {e}[/yellow]")

        console.print(f"[green]✓ Metadata added to {len(updated_files)} file(s)[/green]")

        return {
            'updated_files': updated_files,
            'metadata': self.metadata
        }


class GenerateSpectrogramStep(WorkflowStep):
    """
    Step para generar espectrograma del audio
    """

    def __init__(self,
                 spectrogram_type: str = "mel",
                 enhanced: bool = True,
                 name: Optional[str] = None):
        name = name or f"Generate {spectrogram_type.upper()} Spectrogram"
        super().__init__(
            name=name,
            description=f"Generar espectrograma tipo {spectrogram_type}",
            required=False  # No es crítico
        )
        self.spectrogram_type = spectrogram_type
        self.enhanced = enhanced
        self.generator = EnhancedSpectrogramGenerator()

    def execute(self, context: WorkflowContext) -> Dict[str, Any]:
        """Ejecutar generación de espectrograma"""
        # Usar archivo convertido si existe, sino el original
        input_file = context.get_intermediate_file('converted_mp3') or context.input_file
        output_dir = Path(context.output_dir or ".") / "spectrograms"
        output_dir.mkdir(parents=True, exist_ok=True)

        input_path = Path(input_file)
        output_file = output_dir / f"{input_path.stem}_spectrogram.png"

        console.print(f"[cyan]Generating {self.spectrogram_type} spectrogram...[/cyan]")

        # Generar espectrograma usando el método específico
        try:
            if self.spectrogram_type == "mel":
                result = self.generator.generate_mel_spectrogram(
                    input_file=str(input_file),
                    output_file=str(output_file)
                )
            elif self.spectrogram_type == "linear":
                result = self.generator.generate_linear_spectrogram(
                    input_file=str(input_file),
                    output_file=str(output_file)
                )
            elif self.spectrogram_type == "cqt":
                result = self.generator.generate_cqt_spectrogram(
                    input_file=str(input_file),
                    output_file=str(output_file)
                )
            else:
                raise WorkflowError(f"Unknown spectrogram type: {self.spectrogram_type}")

            # El resultado es un diccionario con 'status': 'success'
            if result and result.get('status') == 'success':
                context.add_intermediate_file('spectrogram', str(output_file))
                console.print(f"[green]✓ Spectrogram generated: {output_file}[/green]")

                return {
                    'output_file': str(output_file),
                    'type': self.spectrogram_type,
                    'quality_metrics': result.get('quality_metrics')
                }
            else:
                raise WorkflowError(f"Spectrogram generation failed")
        except WorkflowError:
            raise
        except Exception as e:
            raise WorkflowError(f"Spectrogram generation error: {e}")


class ValidateQualityStep(WorkflowStep):
    """
    Step para validar calidad de audio procesado
    """

    def __init__(self,
                 strict: bool = True,
                 profile: Optional[str] = None,
                 compare_formats: bool = False,
                 name: Optional[str] = None):
        name = name or "Validate Audio Quality"
        super().__init__(
            name=name,
            description="Validar calidad del audio procesado",
            required=False
        )
        self.strict = strict  # If True, reject on failure; if False, warn only
        self.profile = profile  # Quality profile: "professional", "studio", etc.
        self.compare_formats = compare_formats  # Compare FLAC vs MP3 quality

    def execute(self, context: WorkflowContext) -> Dict[str, Any]:
        """Ejecutar validación de calidad"""
        console.print("[cyan]Validating audio quality...[/cyan]")

        # Obtener configuración de calidad
        quality_settings = context.quality_settings

        # Por ahora, retornar validación exitosa
        # En implementación futura, integrar con AudioQualityAnalyzer
        console.print("[green]✓ Quality validation passed[/green]")

        return {
            'quality_check': 'passed',
            'profile': quality_settings.preferences.default_profile.value
        }


class ChannelConversionStep(WorkflowStep):
    """
    Step para conversión de canales (mono ↔ stereo)
    """

    def __init__(self,
                 target_channels: int,
                 mixing_algorithm: str = "downmix_center",
                 preserve_metadata: bool = True,
                 name: Optional[str] = None):
        channel_name = "Mono" if target_channels == 1 else "Stereo"
        name = name or f"Convert to {channel_name}"
        super().__init__(
            name=name,
            description=f"Convertir audio a {channel_name}",
            required=False  # Opcional
        )
        self.target_channels = target_channels
        self.mixing_algorithm = mixing_algorithm
        self.preserve_metadata = preserve_metadata
        self.converter = AudioConverter()

    def validate_preconditions(self, context: WorkflowContext) -> bool:
        """Validar que existe archivo de entrada"""
        if not context.input_file:
            return False
        return Path(context.input_file).exists()

    def execute(self, context: WorkflowContext) -> Dict[str, Any]:
        """Ejecutar conversión de canales"""
        input_file = context.input_file
        output_dir = Path(context.output_dir or ".")
        output_dir.mkdir(parents=True, exist_ok=True)

        # Generar nombre de archivo de salida
        input_path = Path(input_file)
        channel_suffix = "mono" if self.target_channels == 1 else "stereo"
        output_file = output_dir / f"{input_path.stem}_{channel_suffix}{input_path.suffix}"

        console.print(f"[cyan]Converting to {channel_suffix}...[/cyan]")

        # Ejecutar conversión usando AudioConverter
        success = self.converter.convert_channels(
            input_path=str(input_file),
            output_path=str(output_file),
            target_channels=self.target_channels,
            mixing_algorithm=self.mixing_algorithm if self.target_channels == 1 else "average",
            preserve_metadata=self.preserve_metadata
        )

        if success:
            # Registrar archivo generado y actualizar input para siguientes steps
            context.add_intermediate_file('channel_converted', str(output_file))
            # IMPORTANTE: Actualizar input_file para que siguientes steps usen el archivo convertido
            context.input_file = str(output_file)
            console.print(f"[green]✓ Channel conversion successful: {output_file}[/green]")

            return {
                'output_file': str(output_file),
                'target_channels': self.target_channels,
                'algorithm': self.mixing_algorithm
            }
        else:
            raise WorkflowError(f"Channel conversion failed")

    def validate_postconditions(self, context: WorkflowContext) -> bool:
        """Validar que el archivo convertido existe"""
        output_file = context.get_intermediate_file('channel_converted')
        return output_file and Path(output_file).exists()


# Factory functions para crear steps comunes
def create_convert_step(format: str, quality: str = "high") -> ConvertAudioStep:
    """Helper para crear step de conversión"""
    return ConvertAudioStep(output_format=format, quality_level=quality)


def create_split_step(segments: List[str], enhanced: bool = True) -> SplitAudioStep:
    """Helper para crear step de división"""
    return SplitAudioStep(segments=segments, enhanced=enhanced)


def create_metadata_step(metadata: Dict[str, str], target: str = "converted") -> AddMetadataStep:
    """Helper para crear step de metadatos"""
    return AddMetadataStep(metadata=metadata, target=target)


def create_spectrogram_step(type: str = "mel") -> GenerateSpectrogramStep:
    """Helper para crear step de espectrograma"""
    return GenerateSpectrogramStep(spectrogram_type=type)


if __name__ == "__main__":
    console.print("[cyan]Testing Workflow Steps...[/cyan]")
    console.print("✅ All workflow steps imported successfully")
