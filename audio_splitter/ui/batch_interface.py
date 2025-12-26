#!/usr/bin/env python3
"""
Batch Processing Interface - Interfaz interactiva para procesamiento por lotes
UI rica para operaciones batch en todos los módulos
"""

import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table

# Imports relativos con fallback
try:
    from ..i18n.translator import t
    from ..core.batch_processor import UniversalBatchProcessor, BatchOperation
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from audio_splitter.i18n.translator import t
    from audio_splitter.core.batch_processor import UniversalBatchProcessor, BatchOperation

console = Console()


def run_batch_processing():
    """
    Interfaz principal para Batch Processing
    """
    console.print(Panel(
        "[bold blue]📦 Universal Batch Processing[/bold blue]\n" +
        "[dim]Procesamiento masivo de archivos de audio[/dim]",
        title="Batch Processing"
    ))

    processor = UniversalBatchProcessor()

    while True:
        console.print("\n[cyan]🔧 Operaciones Batch Disponibles:[/cyan]")
        options = [
            "1. 🔄 Batch Conversion - Convertir múltiples archivos",
            "2. 🎧 Batch Channel Conversion - Convertir canales",
            "3. 📊 Batch Spectrogram - Generar espectrogramas",
            "4. 🔙 Volver al menú principal"
        ]

        for option in options:
            console.print(f"  {option}")

        choice = Prompt.ask(
            "\nSelecciona operación",
            choices=["1", "2", "3", "4"],
            default="1"
        )

        if choice == "1":
            run_batch_conversion(processor)
        elif choice == "2":
            run_batch_channel_conversion(processor)
        elif choice == "3":
            run_batch_spectrogram(processor)
        elif choice == "4":
            break

        if choice in ["1", "2", "3"]:
            if not Confirm.ask("\n¿Realizar otra operación batch?", default=False):
                break


def run_batch_conversion(processor: UniversalBatchProcessor):
    """
    Interfaz para batch conversion
    """
    console.print("\n[bold cyan]🔄 Batch Audio Conversion[/bold cyan]")

    # Input path
    input_path = Prompt.ask("📁 Directorio o archivo de entrada")

    if not Path(input_path).exists():
        console.print("[red]❌ Path no encontrado[/red]")
        return

    # Output directory
    output_dir = Prompt.ask("📂 Directorio de salida", default="./batch_converted")

    # Output format
    console.print("\n[cyan]Formato de salida:[/cyan]")
    console.print("  1. MP3")
    console.print("  2. FLAC")
    console.print("  3. WAV")

    format_choice = Prompt.ask("Selecciona formato", choices=["1", "2", "3"], default="1")
    format_map = {"1": "mp3", "2": "flac", "3": "wav"}
    output_format = format_map[format_choice]

    # Recursive
    recursive = Confirm.ask("¿Buscar en subdirectorios?", default=False)

    # Quality validation
    quality_validation = Confirm.ask("¿Activar validación de calidad?", default=False)

    # Ejecutar
    console.print(f"\n[green]🚀 Iniciando batch conversion...[/green]")

    result = processor.batch_convert(
        input_path=input_path,
        output_dir=output_dir,
        output_format=output_format,
        recursive=recursive,
        quality_validation=quality_validation
    )

    processor.display_batch_results(result, "Conversion")


def run_batch_splitting(processor: UniversalBatchProcessor):
    """
    Interfaz para batch splitting
    """
    console.print("\n[bold cyan]✂️ Batch Audio Splitting[/bold cyan]")

    # Input path
    input_path = Prompt.ask("📁 Directorio o archivo de entrada")

    if not Path(input_path).exists():
        console.print("[red]❌ Path no encontrado[/red]")
        return

    # Output directory
    output_dir = Prompt.ask("📂 Directorio de salida", default="./batch_split")

    # Segments
    console.print("\n[cyan]Configurar segmentos:[/cyan]")
    console.print("[dim]Formato: 0:00-1:30:nombre[/dim]")
    console.print("[dim]Escribe 'fin' cuando termines[/dim]")

    segments = []
    while True:
        segment = Prompt.ask(f"Segmento {len(segments) + 1}", default="fin")
        if segment.lower() == "fin":
            break
        segments.append(segment)

    if not segments:
        console.print("[yellow]Usando segmento por defecto (archivo completo)[/yellow]")
        segments = ["0:00-end:full"]

    # Recursive
    recursive = Confirm.ask("¿Buscar en subdirectorios?", default=False)

    # Quality validation
    quality_validation = Confirm.ask("¿Activar validación de calidad?", default=False)

    # Ejecutar
    console.print(f"\n[green]🚀 Iniciando batch splitting...[/green]")

    result = processor.batch_split(
        input_path=input_path,
        output_dir=output_dir,
        segments=segments,
        recursive=recursive,
        quality_validation=quality_validation
    )

    processor.display_batch_results(result, "Splitting")


def run_batch_channel_conversion(processor: UniversalBatchProcessor):
    """
    Interfaz para batch channel conversion
    """
    console.print("\n[bold cyan]🎧 Batch Channel Conversion[/bold cyan]")

    # Input path
    input_path = Prompt.ask("📁 Directorio o archivo de entrada")

    if not Path(input_path).exists():
        console.print("[red]❌ Path no encontrado[/red]")
        return

    # Output directory
    output_dir = Prompt.ask("📂 Directorio de salida", default="./batch_channel")

    # Target channels
    console.print("\n[cyan]Canales objetivo:[/cyan]")
    console.print("  1. Mono (1 canal)")
    console.print("  2. Stereo (2 canales)")

    channel_choice = Prompt.ask("Selecciona", choices=["1", "2"], default="1")
    target_channels = 1 if channel_choice == "1" else 2

    # Mixing algorithm (solo para stereo → mono)
    mixing_algorithm = "downmix_center"
    if target_channels == 1:
        console.print("\n[cyan]Algoritmo de downmix:[/cyan]")
        console.print("  1. Center (L+R)/2 - Recomendado")
        console.print("  2. Left only")
        console.print("  3. Right only")
        console.print("  4. Average RMS")

        algo_choice = Prompt.ask("Selecciona algoritmo", choices=["1", "2", "3", "4"], default="1")
        algorithms = ["downmix_center", "left_only", "right_only", "average"]
        mixing_algorithm = algorithms[int(algo_choice) - 1]

    # Recursive
    recursive = Confirm.ask("¿Buscar en subdirectorios?", default=False)

    # Ejecutar
    console.print(f"\n[green]🚀 Iniciando batch channel conversion...[/green]")

    result = processor.batch_channel_convert(
        input_path=input_path,
        output_dir=output_dir,
        target_channels=target_channels,
        mixing_algorithm=mixing_algorithm,
        recursive=recursive
    )

    processor.display_batch_results(result, "Channel Conversion")


def run_batch_spectrogram(processor: UniversalBatchProcessor):
    """
    Interfaz para batch spectrogram generation
    """
    console.print("\n[bold cyan]📊 Batch Spectrogram Generation[/bold cyan]")

    # Input path
    input_path = Prompt.ask("📁 Directorio o archivo de entrada")

    if not Path(input_path).exists():
        console.print("[red]❌ Path no encontrado[/red]")
        return

    # Output directory
    output_dir = Prompt.ask("📂 Directorio de salida", default="./batch_spectrograms")

    # Spectrogram type
    console.print("\n[cyan]Tipo de espectrograma:[/cyan]")
    console.print("  1. Mel - General purpose")
    console.print("  2. Linear - Detailed frequency")
    console.print("  3. CQT - Musical analysis")
    console.print("  4. Dual - Combined view")

    type_choice = Prompt.ask("Selecciona tipo", choices=["1", "2", "3", "4"], default="1")
    type_map = {"1": "mel", "2": "linear", "3": "cqt", "4": "dual"}
    spectrogram_type = type_map[type_choice]

    # Recursive
    recursive = Confirm.ask("¿Buscar en subdirectorios?", default=False)

    # Ejecutar
    console.print(f"\n[green]🚀 Iniciando batch spectrogram generation...[/green]")

    result = processor.batch_spectrogram(
        input_path=input_path,
        output_dir=output_dir,
        spectrogram_type=spectrogram_type,
        recursive=recursive
    )

    processor.display_batch_results(result, "Spectrogram Generation")


# Entry point para testing
if __name__ == "__main__":
    console.print("[cyan]Testing Batch Processing Interface...[/cyan]")
    run_batch_processing()
