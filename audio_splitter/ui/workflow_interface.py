#!/usr/bin/env python3
"""
Workflow Interface - Interfaz interactiva para Professional Workflows
Interfaz rica con Rich para ejecutar workflows de audio profesionales
"""

import sys
from pathlib import Path
from typing import Optional, Dict, Any, List

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

# Imports relativos con fallback
try:
    from ..i18n.translator import t
    from ..core.workflows.podcast_workflow import (
        create_podcast_workflow,
        create_quick_podcast_workflow,
        create_advanced_podcast_workflow,
        get_podcast_template,
        PODCAST_TEMPLATES
    )
    from ..core.workflows.music_workflow import (
        create_music_mastering_workflow,
        create_quick_music_workflow,
        create_studio_mastering_workflow,
        create_mono_mastering_workflow,
        create_stereo_upmix_workflow,
        get_mastering_template,
        MASTERING_TEMPLATES
    )
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from audio_splitter.i18n.translator import t
    from audio_splitter.core.workflows.podcast_workflow import (
        create_podcast_workflow,
        create_quick_podcast_workflow,
        create_advanced_podcast_workflow,
        get_podcast_template,
        PODCAST_TEMPLATES
    )
    from audio_splitter.core.workflows.music_workflow import (
        create_music_mastering_workflow,
        create_quick_music_workflow,
        create_studio_mastering_workflow,
        create_mono_mastering_workflow,
        create_stereo_upmix_workflow,
        get_mastering_template,
        MASTERING_TEMPLATES
    )

console = Console()


def run_professional_workflows():
    """
    Interfaz principal para Professional Workflows
    """
    console.print(Panel(
        "[bold blue]🔄 Professional Workflows[/bold blue]\n" +
        "[dim]Automatización de procesos complejos de audio[/dim]",
        title="Professional Workflows"
    ))

    while True:
        console.print("\n[cyan]🔧 Workflows Disponibles:[/cyan]")
        options = [
            "1. 🎙️  Complete Podcast Production",
            "2. 🎵 Professional Music Mastering",
            "3. 📊 Ver Templates Disponibles",
            "4. 🔙 Volver al menú principal"
        ]

        for option in options:
            console.print(f"  {option}")

        choice = Prompt.ask(
            "\nSelecciona workflow",
            choices=["1", "2", "3", "4"],
            default="1"
        )

        if choice == "1":
            run_podcast_workflow()
        elif choice == "2":
            run_music_workflow()
        elif choice == "3":
            show_workflow_templates()
        elif choice == "4":
            break

        # Preguntar si continuar
        if choice in ["1", "2"]:
            if not Confirm.ask("\n¿Ejecutar otro workflow?", default=False):
                break


def run_podcast_workflow():
    """
    Interfaz para Podcast Production Workflow
    """
    console.print("\n[bold cyan]🎙️ Complete Podcast Production Workflow[/bold cyan]")

    # Input file
    input_file = Prompt.ask("📁 Archivo de audio del podcast")

    if not Path(input_file).exists():
        console.print("[red]❌ Archivo no encontrado[/red]")
        return

    # Output directory
    output_dir = Prompt.ask("📂 Directorio de salida", default="./podcast_output")

    # Workflow type
    console.print("\n[cyan]🎯 Tipo de workflow:[/cyan]")
    console.print("  1. Quick - Rápido con configuración básica")
    console.print("  2. Standard - Configuración estándar con templates")
    console.print("  3. Advanced - Control completo con validación científica")

    workflow_type = Prompt.ask(
        "Selecciona tipo",
        choices=["1", "2", "3"],
        default="2"
    )

    if workflow_type == "1":
        # Quick workflow
        episode_title = Prompt.ask("Título del episodio", default="Podcast Episode")
        host_name = Prompt.ask("Nombre del host", default="Host")
        series_name = Prompt.ask("Nombre de la serie", default="Podcast Series")

        workflow = create_quick_podcast_workflow(
            input_file=input_file,
            output_dir=output_dir,
            episode_title=episode_title,
            host_name=host_name,
            series_name=series_name
        )

    elif workflow_type == "2":
        # Standard workflow con template
        console.print("\n[cyan]📋 Templates disponibles:[/cyan]")
        templates = list(PODCAST_TEMPLATES.keys())
        for i, template in enumerate(templates, 1):
            template_info = PODCAST_TEMPLATES[template]
            console.print(f"  {i}. {template} - {template_info['duration']}")

        template_choice = Prompt.ask(
            "Selecciona template",
            choices=[str(i) for i in range(1, len(templates) + 1)],
            default="2"
        )

        template_name = templates[int(template_choice) - 1]
        template = get_podcast_template(template_name)

        # Metadata
        title = Prompt.ask("Título del episodio")
        artist = Prompt.ask("Host/Artista")
        album = Prompt.ask("Serie/Álbum")

        metadata = {
            'title': title,
            'artist': artist,
            'album': album,
            'genre': 'Podcast'
        }

        workflow = create_podcast_workflow(
            input_file=input_file,
            output_dir=output_dir,
            segments=template['segments'],
            metadata=metadata,
            generate_spectrogram=True,
            quality_validation=False
        )

    else:
        # Advanced workflow
        console.print("\n[yellow]Modo avanzado - Configuración completa[/yellow]")

        # Custom segments
        segments = []
        console.print("\n[cyan]Configurar segmentos (formato: 0:00-1:30:intro):[/cyan]")
        console.print("[dim]Escribe 'fin' cuando termines[/dim]")

        while True:
            segment = Prompt.ask(f"Segmento {len(segments) + 1}", default="fin")
            if segment.lower() == "fin":
                break
            segments.append(segment)

        if not segments:
            console.print("[yellow]Usando segmentos por defecto[/yellow]")
            segments = None

        # Metadata completo
        title = Prompt.ask("Título")
        artist = Prompt.ask("Artista/Host")
        album = Prompt.ask("Álbum/Serie")
        year = Prompt.ask("Año", default="2025")
        genre = Prompt.ask("Género", default="Podcast")

        metadata = {
            'title': title,
            'artist': artist,
            'album': album,
            'date': year,
            'genre': genre
        }

        # Quality validation
        quality_validation = Confirm.ask(
            "¿Activar validación científica de calidad?",
            default=True
        )

        workflow = create_advanced_podcast_workflow(
            input_file=input_file,
            output_dir=output_dir,
            segments=segments or ["0:00-30:00:full"],
            metadata=metadata,
            quality_profile="professional"
        )

    # Ejecutar workflow
    console.print("\n[bold green]🚀 Ejecutando Podcast Production Workflow...[/bold green]")
    results = workflow.execute(show_progress=True)

    # Mostrar resultados
    display_workflow_results(results)


def run_music_workflow():
    """
    Interfaz para Music Mastering Workflow
    """
    console.print("\n[bold cyan]🎵 Professional Music Mastering Workflow[/bold cyan]")

    # Input file
    input_file = Prompt.ask("📁 Archivo de audio master")

    if not Path(input_file).exists():
        console.print("[red]❌ Archivo no encontrado[/red]")
        return

    # Output directory
    output_dir = Prompt.ask("📂 Directorio de salida", default="./music_output")

    # Workflow type
    console.print("\n[cyan]🎯 Tipo de mastering:[/cyan]")
    console.print("  1. Quick - Rápido (solo MP3)")
    console.print("  2. Standard - Estándar (FLAC + MP3)")
    console.print("  3. Studio - Studio Grade (máxima calidad)")
    console.print("  4. Mono Master - Para radio/broadcast")
    console.print("  5. Stereo Upmix - Convertir mono a stereo")

    workflow_type = Prompt.ask(
        "Selecciona tipo",
        choices=["1", "2", "3", "4", "5"],
        default="2"
    )

    # Metadata común
    track_title = Prompt.ask("Título del track")
    artist_name = Prompt.ask("Artista")
    album_name = Prompt.ask("Álbum")

    metadata = {
        'title': track_title,
        'artist': artist_name,
        'album': album_name,
        'date': Prompt.ask("Año", default="2025"),
        'genre': Prompt.ask("Género", default="Music")
    }

    if workflow_type == "1":
        # Quick workflow
        to_mono = Confirm.ask("¿Convertir a mono?", default=False)
        workflow = create_quick_music_workflow(
            input_file=input_file,
            output_dir=output_dir,
            track_title=track_title,
            artist_name=artist_name,
            album_name=album_name,
            to_mono=to_mono
        )

    elif workflow_type == "2":
        # Standard workflow
        console.print("\n[cyan]⚙️ Opciones:[/cyan]")

        # Channel conversion
        console.print("  Conversión de canales:")
        console.print("    1. Mantener original")
        console.print("    2. Convertir a mono")
        console.print("    3. Convertir a stereo")

        channel_choice = Prompt.ask(
            "Selecciona conversión",
            choices=["1", "2", "3"],
            default="1"
        )

        channel_conversion = None
        mixing_algorithm = "downmix_center"

        if channel_choice == "2":
            channel_conversion = "mono"
            # Preguntar algoritmo
            console.print("\n[cyan]Algoritmo de downmix:[/cyan]")
            console.print("  1. Center (L+R)/2 - Recomendado")
            console.print("  2. Left only")
            console.print("  3. Right only")
            console.print("  4. Average RMS")

            algo_choice = Prompt.ask("Selecciona algoritmo", choices=["1", "2", "3", "4"], default="1")
            algorithms = ["downmix_center", "left_only", "right_only", "average"]
            mixing_algorithm = algorithms[int(algo_choice) - 1]

        elif channel_choice == "3":
            channel_conversion = "stereo"

        workflow = create_music_mastering_workflow(
            input_file=input_file,
            output_dir=output_dir,
            metadata=metadata,
            quality_profile="professional",
            channel_conversion=channel_conversion,
            mixing_algorithm=mixing_algorithm,
            include_flac=True,
            include_mp3=True,
            generate_analysis=True
        )

    elif workflow_type == "3":
        # Studio workflow
        isrc = Prompt.ask("ISRC (opcional)", default="")
        channel_mode = None

        if Confirm.ask("¿Aplicar conversión de canales?", default=False):
            mode = Prompt.ask("Modo", choices=["mono", "stereo"])
            channel_mode = mode

        workflow = create_studio_mastering_workflow(
            input_file=input_file,
            output_dir=output_dir,
            metadata=metadata,
            channel_mode=channel_mode,
            isrc=isrc if isrc else None
        )

    elif workflow_type == "4":
        # Mono master
        console.print("\n[cyan]Algoritmo de downmix:[/cyan]")
        console.print("  1. Center (L+R)/2")
        console.print("  2. Left only")
        console.print("  3. Right only")
        console.print("  4. Average RMS")

        algo_choice = Prompt.ask("Selecciona", choices=["1", "2", "3", "4"], default="1")
        algorithms = ["downmix_center", "left_only", "right_only", "average"]
        mixing_algorithm = algorithms[int(algo_choice) - 1]

        workflow = create_mono_mastering_workflow(
            input_file=input_file,
            output_dir=output_dir,
            metadata=metadata,
            mixing_algorithm=mixing_algorithm
        )

    else:
        # Stereo upmix
        workflow = create_stereo_upmix_workflow(
            input_file=input_file,
            output_dir=output_dir,
            metadata=metadata
        )

    # Ejecutar workflow
    console.print("\n[bold green]🚀 Ejecutando Music Mastering Workflow...[/bold green]")
    results = workflow.execute(show_progress=True)

    # Mostrar resultados
    display_workflow_results(results)


def show_workflow_templates():
    """
    Mostrar templates disponibles de workflows
    """
    console.print("\n[bold cyan]📋 Templates de Workflows Disponibles[/bold cyan]")

    # Podcast templates
    console.print("\n[yellow]🎙️ Podcast Templates:[/yellow]")
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Template", style="white", width=20)
    table.add_column("Duración", style="green", width=15)
    table.add_column("Segmentos", style="dim", width=10)

    for name, info in PODCAST_TEMPLATES.items():
        table.add_row(
            name,
            info['duration'],
            str(len(info['segments']))
        )

    console.print(table)

    # Music templates
    console.print("\n[yellow]🎵 Music Mastering Templates:[/yellow]")
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Template", style="white", width=25)
    table.add_column("FLAC", style="green", width=8)
    table.add_column("MP3", style="green", width=8)
    table.add_column("Channels", style="cyan", width=10)
    table.add_column("Descripción", style="dim", width=30)

    for name, info in MASTERING_TEMPLATES.items():
        flac = "✅" if info['include_flac'] else "❌"
        mp3 = "✅" if info['include_mp3'] else "❌"
        channels = info.get('channel_conversion', 'Original') or 'Original'

        table.add_row(
            name,
            flac,
            mp3,
            channels,
            info['description']
        )

    console.print(table)


def display_workflow_results(results: Dict[str, Any]):
    """
    Mostrar resultados del workflow ejecutado
    """
    console.print("\n" + "="*60)

    if results['success']:
        console.print("[bold green]✅ Workflow Completado Exitosamente[/bold green]")
    else:
        console.print("[bold red]❌ Workflow Fallido[/bold red]")

    # Tabla de resultados
    table = Table(title="Resultados del Workflow", show_header=True, header_style="bold cyan")
    table.add_column("Métrica", style="white", width=30)
    table.add_column("Valor", style="green", width=25)

    table.add_row("Workflow", results['workflow_name'])
    table.add_row("Steps Completados", f"{results['completed_steps']}/{results['total_steps']}")
    table.add_row("Duración Total", f"{results['duration']:.2f}s")
    table.add_row("Estado Final", "✅ Exitoso" if results['success'] else "❌ Fallido")

    if results.get('failed_step'):
        table.add_row("Step Fallido", f"[red]{results['failed_step']}[/red]")

    console.print(table)

    # Detalles de steps
    if results.get('step_results'):
        console.print("\n[cyan]📊 Detalle de Steps:[/cyan]")
        for step_name, step_result in results['step_results'].items():
            status = "✅" if step_result['success'] else "❌"
            duration = step_result.get('duration', 0)
            console.print(f"  {status} {step_name} ({duration:.2f}s)")

    console.print("="*60 + "\n")


# Entry point para testing
if __name__ == "__main__":
    console.print("[cyan]Testing Workflow Interface...[/cyan]")
    run_professional_workflows()
