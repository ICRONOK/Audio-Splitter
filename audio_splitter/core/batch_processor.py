#!/usr/bin/env python3
"""
Universal Batch Processor - Sistema unificado de procesamiento por lotes
Procesamiento batch para todos los módulos: converter, splitter, spectrogram
"""

import sys
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum

from rich.console import Console
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn, SpinnerColumn
from rich.table import Table
from rich.panel import Panel

# Imports relativos con fallback
try:
    from ..core.enhanced_converter import EnhancedAudioConverter
    from ..core.enhanced_splitter import EnhancedAudioSplitter
    from ..core.enhanced_spectrogram import EnhancedSpectrogramGenerator
    from ..core.converter import AudioConverter
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from audio_splitter.core.enhanced_converter import EnhancedAudioConverter
    from audio_splitter.core.enhanced_splitter import EnhancedAudioSplitter
    from audio_splitter.core.enhanced_spectrogram import EnhancedSpectrogramGenerator
    from audio_splitter.core.converter import AudioConverter

console = Console()


class BatchOperation(Enum):
    """Tipos de operaciones batch disponibles"""
    CONVERT = "convert"
    SPLIT = "split"
    CHANNEL = "channel"
    SPECTROGRAM = "spectrogram"
    METADATA = "metadata"


@dataclass
class BatchResult:
    """Resultado de una operación batch"""
    total_files: int
    successful: int
    failed: int
    skipped: int
    results: List[Dict[str, Any]]
    duration: float

    @property
    def success_rate(self) -> float:
        """Calcular tasa de éxito"""
        if self.total_files == 0:
            return 0.0
        return (self.successful / self.total_files) * 100


class UniversalBatchProcessor:
    """
    Procesador batch universal para todas las operaciones de audio
    """

    def __init__(self):
        self.converter = EnhancedAudioConverter()
        self.splitter = EnhancedAudioSplitter()
        self.spectrogram_generator = EnhancedSpectrogramGenerator()
        self.audio_converter = AudioConverter()  # Para channel operations

    def find_audio_files(self,
                        input_path: str,
                        recursive: bool = False,
                        extensions: Optional[List[str]] = None) -> List[Path]:
        """
        Encontrar archivos de audio en directorio

        Args:
            input_path: Directorio o archivo de entrada
            recursive: Si buscar recursivamente en subdirectorios
            extensions: Extensiones permitidas (default: wav, mp3, flac, m4a, ogg)

        Returns:
            Lista de Path de archivos encontrados
        """
        if extensions is None:
            extensions = ['.wav', '.mp3', '.flac', '.m4a', '.ogg']

        path = Path(input_path)

        # Si es archivo, retornar directamente
        if path.is_file():
            if path.suffix.lower() in extensions:
                return [path]
            else:
                console.print(f"[yellow]⚠️ File {path} is not a supported audio format[/yellow]")
                return []

        # Si es directorio, buscar archivos
        if path.is_dir():
            files = []
            pattern = "**/*" if recursive else "*"

            for ext in extensions:
                files.extend(path.glob(f"{pattern}{ext}"))

            return sorted(files)

        return []

    def batch_convert(self,
                     input_path: str,
                     output_dir: str,
                     output_format: str,
                     recursive: bool = False,
                     quality_validation: bool = False) -> BatchResult:
        """
        Conversión batch de archivos de audio

        Args:
            input_path: Directorio o archivo de entrada
            output_dir: Directorio de salida
            output_format: Formato de salida (mp3, flac, wav)
            recursive: Buscar recursivamente
            quality_validation: Validar calidad

        Returns:
            BatchResult con resultados
        """
        console.print(f"\n[bold cyan]🔄 Batch Conversion to {output_format.upper()}[/bold cyan]")

        # Encontrar archivos
        files = self.find_audio_files(input_path, recursive)

        if not files:
            console.print("[yellow]No audio files found[/yellow]")
            return BatchResult(0, 0, 0, 0, [], 0.0)

        console.print(f"[cyan]Found {len(files)} audio file(s)[/cyan]")

        # Crear directorio de salida
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Procesar archivos con progress bar
        results = []
        successful = 0
        failed = 0
        skipped = 0

        import time
        start_time = time.time()

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
            console=console
        ) as progress:
            task = progress.add_task(f"[cyan]Converting to {output_format}...", total=len(files))

            for file in files:
                progress.update(task, description=f"[cyan]Converting {file.name}...")

                # Generar output file path
                output_file = output_path / f"{file.stem}.{output_format}"

                # Skip si ya existe
                if output_file.exists():
                    results.append({
                        'file': str(file),
                        'status': 'skipped',
                        'reason': 'Output file already exists'
                    })
                    skipped += 1
                    progress.advance(task)
                    continue

                # Convertir
                try:
                    result = self.converter.convert_audio(
                        input_file=str(file),
                        output_file=str(output_file),
                        output_format=output_format,
                        quality_validation=quality_validation
                    )

                    if result.get('success', False):
                        successful += 1
                        results.append({
                            'file': str(file),
                            'output': str(output_file),
                            'status': 'success'
                        })
                    else:
                        failed += 1
                        results.append({
                            'file': str(file),
                            'status': 'failed',
                            'error': result.get('error', 'Unknown error')
                        })

                except Exception as e:
                    failed += 1
                    results.append({
                        'file': str(file),
                        'status': 'failed',
                        'error': str(e)
                    })

                progress.advance(task)

        duration = time.time() - start_time

        return BatchResult(
            total_files=len(files),
            successful=successful,
            failed=failed,
            skipped=skipped,
            results=results,
            duration=duration
        )

    def batch_split(self,
                   input_path: str,
                   output_dir: str,
                   segments: List[str],
                   recursive: bool = False,
                   quality_validation: bool = False) -> BatchResult:
        """
        División batch de archivos de audio

        Args:
            input_path: Directorio o archivo de entrada
            output_dir: Directorio de salida
            segments: Lista de segmentos (ej: ["0:00-1:00:intro"])
            recursive: Buscar recursivamente
            quality_validation: Validar calidad

        Returns:
            BatchResult con resultados
        """
        console.print(f"\n[bold cyan]✂️ Batch Audio Splitting[/bold cyan]")

        # Encontrar archivos
        files = self.find_audio_files(input_path, recursive)

        if not files:
            console.print("[yellow]No audio files found[/yellow]")
            return BatchResult(0, 0, 0, 0, [], 0.0)

        console.print(f"[cyan]Found {len(files)} audio file(s)[/cyan]")
        console.print(f"[cyan]Segments: {len(segments)}[/cyan]")

        # Crear directorio de salida
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Procesar archivos
        results = []
        successful = 0
        failed = 0

        import time
        start_time = time.time()

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
            console=console
        ) as progress:
            task = progress.add_task("[cyan]Splitting files...", total=len(files))

            for file in files:
                progress.update(task, description=f"[cyan]Splitting {file.name}...")

                # Crear subdirectorio para los segmentos de este archivo
                file_output_dir = output_path / file.stem
                file_output_dir.mkdir(exist_ok=True)

                try:
                    result = self.splitter.split_audio(
                        input_file=str(file),
                        segments=segments,
                        output_dir=str(file_output_dir),
                        quality_validation=quality_validation
                    )

                    if result.get('success', False):
                        successful += 1
                        results.append({
                            'file': str(file),
                            'output_dir': str(file_output_dir),
                            'segments': len(result.get('segment_files', [])),
                            'status': 'success'
                        })
                    else:
                        failed += 1
                        results.append({
                            'file': str(file),
                            'status': 'failed',
                            'error': result.get('error', 'Unknown error')
                        })

                except Exception as e:
                    failed += 1
                    results.append({
                        'file': str(file),
                        'status': 'failed',
                        'error': str(e)
                    })

                progress.advance(task)

        duration = time.time() - start_time

        return BatchResult(
            total_files=len(files),
            successful=successful,
            failed=failed,
            skipped=0,
            results=results,
            duration=duration
        )

    def batch_channel_convert(self,
                             input_path: str,
                             output_dir: str,
                             target_channels: int,
                             mixing_algorithm: str = "downmix_center",
                             recursive: bool = False) -> BatchResult:
        """
        Conversión batch de canales (ya implementado en AudioConverter)

        Args:
            input_path: Directorio o archivo de entrada
            output_dir: Directorio de salida
            target_channels: Canales objetivo (1=mono, 2=stereo)
            mixing_algorithm: Algoritmo de downmix
            recursive: Buscar recursivamente

        Returns:
            BatchResult con resultados
        """
        console.print(f"\n[bold cyan]🎧 Batch Channel Conversion[/bold cyan]")

        # Reutilizar método existente de AudioConverter
        try:
            successful, failed = self.audio_converter.batch_convert_channels(
                input_dir=input_path,
                output_dir=output_dir,
                target_channels=target_channels,
                mixing_algorithm=mixing_algorithm,
                recursive=recursive
            )

            import time
            return BatchResult(
                total_files=successful + failed,
                successful=successful,
                failed=failed,
                skipped=0,
                results=[],
                duration=0.0
            )

        except Exception as e:
            console.print(f"[red]Error in batch channel conversion: {e}[/red]")
            return BatchResult(0, 0, 0, 0, [], 0.0)

    def batch_spectrogram(self,
                         input_path: str,
                         output_dir: str,
                         spectrogram_type: str = "mel",
                         recursive: bool = False) -> BatchResult:
        """
        Generación batch de espectrogramas

        Args:
            input_path: Directorio o archivo de entrada
            output_dir: Directorio de salida
            spectrogram_type: Tipo de espectrograma (mel, linear, cqt, dual)
            recursive: Buscar recursivamente

        Returns:
            BatchResult con resultados
        """
        console.print(f"\n[bold cyan]📊 Batch Spectrogram Generation[/bold cyan]")

        # Encontrar archivos
        files = self.find_audio_files(input_path, recursive)

        if not files:
            console.print("[yellow]No audio files found[/yellow]")
            return BatchResult(0, 0, 0, 0, [], 0.0)

        console.print(f"[cyan]Found {len(files)} audio file(s)[/cyan]")

        # Crear directorio de salida
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Procesar archivos
        results = []
        successful = 0
        failed = 0
        skipped = 0

        import time
        start_time = time.time()

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
            console=console
        ) as progress:
            task = progress.add_task("[cyan]Generating spectrograms...", total=len(files))

            for file in files:
                progress.update(task, description=f"[cyan]Processing {file.name}...")

                # Generar output path
                output_file = output_path / f"{file.stem}_spectrogram.png"

                # Skip si ya existe
                if output_file.exists():
                    skipped += 1
                    results.append({
                        'file': str(file),
                        'status': 'skipped',
                        'reason': 'Spectrogram already exists'
                    })
                    progress.advance(task)
                    continue

                try:
                    result = self.spectrogram_generator.generate_spectrogram(
                        input_file=str(file),
                        output_path=str(output_file),
                        spectrogram_type=spectrogram_type
                    )

                    if result.get('success', False):
                        successful += 1
                        results.append({
                            'file': str(file),
                            'output': str(output_file),
                            'status': 'success'
                        })
                    else:
                        failed += 1
                        results.append({
                            'file': str(file),
                            'status': 'failed',
                            'error': result.get('error', 'Unknown error')
                        })

                except Exception as e:
                    failed += 1
                    results.append({
                        'file': str(file),
                        'status': 'failed',
                        'error': str(e)
                    })

                progress.advance(task)

        duration = time.time() - start_time

        return BatchResult(
            total_files=len(files),
            successful=successful,
            failed=failed,
            skipped=skipped,
            results=results,
            duration=duration
        )

    def display_batch_results(self, result: BatchResult, operation: str):
        """
        Mostrar resultados de operación batch
        """
        console.print("\n" + "="*60)

        # Status general
        if result.failed == 0:
            console.print(f"[bold green]✅ Batch {operation} Completed Successfully[/bold green]")
        elif result.successful > 0:
            console.print(f"[bold yellow]⚠️ Batch {operation} Partially Completed[/bold yellow]")
        else:
            console.print(f"[bold red]❌ Batch {operation} Failed[/bold red]")

        # Tabla de resultados
        table = Table(title=f"Batch {operation} Results", show_header=True, header_style="bold cyan")
        table.add_column("Métrica", style="white", width=25)
        table.add_column("Valor", style="green", width=20)

        table.add_row("Total Files", str(result.total_files))
        table.add_row("Successful", f"[green]{result.successful}[/green]")
        table.add_row("Failed", f"[red]{result.failed}[/red]" if result.failed > 0 else "0")
        table.add_row("Skipped", f"[yellow]{result.skipped}[/yellow]" if result.skipped > 0 else "0")
        table.add_row("Success Rate", f"{result.success_rate:.1f}%")
        table.add_row("Duration", f"{result.duration:.2f}s")

        console.print(table)
        console.print("="*60 + "\n")


# Helper functions
def create_batch_processor() -> UniversalBatchProcessor:
    """Factory function para crear batch processor"""
    return UniversalBatchProcessor()


if __name__ == "__main__":
    console.print("[cyan]Universal Batch Processor Module Loaded[/cyan]")
    console.print("✅ Batch operations available: convert, split, channel, spectrogram")
