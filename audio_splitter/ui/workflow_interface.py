#!/usr/bin/env python3
"""
Workflow Interface - Interfaz interactiva para Professional Workflows
Interfaz rica con Rich para ejecutar workflows de audio profesionales
"""

import sys
from pathlib import Path
from typing import Optional, Dict, Any

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table

# Imports relativos con fallback
try:
    from ..core.workflows.podcast_workflow import (
        create_podcast_workflow,
        create_quick_podcast_workflow,
        create_professional_podcast_workflow
    )
    from ..core.workflows.music_workflow import (
        create_music_mastering_workflow,
        create_quick_mastering_workflow,
        create_professional_mastering_workflow
    )
    from ..core.workflows.audiobook_workflow import (
        create_audiobook_workflow,
        create_quick_audiobook_workflow,
        create_professional_audiobook_workflow
    )
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from audio_splitter.core.workflows.podcast_workflow import (
        create_podcast_workflow,
        create_quick_podcast_workflow,
        create_professional_podcast_workflow
    )
    from audio_splitter.core.workflows.music_workflow import (
        create_music_mastering_workflow,
        create_quick_mastering_workflow,
        create_professional_mastering_workflow
    )
    from audio_splitter.core.workflows.audiobook_workflow import (
        create_audiobook_workflow,
        create_quick_audiobook_workflow,
        create_professional_audiobook_workflow
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
            "1. 🎙️  Podcast Production",
            "2. 🎵 Music Mastering",
            "3. 📖 Audiobook Production",
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
            run_audiobook_workflow()
        elif choice == "4":
            break

        # Preguntar si continuar
        if choice in ["1", "2", "3"]:
            if not Confirm.ask("\n¿Ejecutar otro workflow?", default=False):
                break


def run_podcast_workflow():
    """
    Interfaz para Podcast Production Workflow
    """
    console.print("\n[bold cyan]🎙️ Podcast Production Workflow[/bold cyan]")

    # Input file
    input_file = Prompt.ask("📁 Archivo de audio del podcast")

    if not Path(input_file).exists():
        console.print("[red]❌ Archivo no encontrado[/red]")
        return

    # Output directory
    output_dir = Prompt.ask("📂 Directorio de salida", default="./podcast_output")

    # Workflow mode
    console.print("\n[cyan]🎯 Modo de workflow:[/cyan]")
    console.print("  1. Quick - Rápido sin validación")
    console.print("  2. Standard - Con validación de calidad")
    console.print("  3. Professional - Validación completa + waveform visual")

    workflow_mode = Prompt.ask(
        "Selecciona modo",
        choices=["1", "2", "3"],
        default="2"
    )

    if workflow_mode == "1":
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

    elif workflow_mode == "2":
        # Standard workflow
        episode_title = Prompt.ask("Título del episodio", default="Podcast Episode")
        host_name = Prompt.ask("Nombre del host", default="Host")
        series_name = Prompt.ask("Nombre de la serie", default="Podcast Series")

        metadata = {
            'title': episode_title,
            'artist': host_name,
            'album': series_name,
            'genre': 'Podcast'
        }

        workflow = create_podcast_workflow(
            input_file=input_file,
            output_dir=output_dir,
            metadata=metadata,
            quality_validation=True,
            generate_visual=False
        )

    else:
        # Professional workflow
        episode_title = Prompt.ask("Título del episodio", default="Podcast Episode")
        episode_number = int(Prompt.ask("Número de episodio", default="1"))
        season_number_str = Prompt.ask("Número de temporada (Enter para omitir)", default="")
        season_number = int(season_number_str) if season_number_str else None
        host_name = Prompt.ask("Nombre del host", default="Host")
        series_name = Prompt.ask("Nombre de la serie", default="Podcast Series")
        description = Prompt.ask("Descripción del episodio", default="Episode description")

        workflow = create_professional_podcast_workflow(
            input_file=input_file,
            output_dir=output_dir,
            episode_title=episode_title,
            episode_number=episode_number,
            season_number=season_number,
            host_name=host_name,
            series_name=series_name,
            description=description
        )

    # Ejecutar workflow
    console.print("\n[bold green]🚀 Ejecutando Podcast Production Workflow...[/bold green]")

    try:
        results = workflow.execute(show_progress=True)
        display_workflow_results(results)
    except Exception as e:
        console.print(f"[red]❌ Error ejecutando workflow: {e}[/red]")


def run_music_workflow():
    """
    Interfaz para Music Mastering Workflow
    """
    console.print("\n[bold cyan]🎵 Music Mastering Workflow[/bold cyan]")

    # Input file
    input_file = Prompt.ask("📁 Archivo de audio master")

    if not Path(input_file).exists():
        console.print("[red]❌ Archivo no encontrado[/red]")
        return

    # Output directory
    output_dir = Prompt.ask("📂 Directorio de salida", default="./music_masters")

    # Workflow mode
    console.print("\n[cyan]🎯 Modo de mastering:[/cyan]")
    console.print("  1. Quick - Solo MP3 rápido")
    console.print("  2. Standard - FLAC + MP3 con validación")
    console.print("  3. Professional - Análisis completo + validación studio")
    console.print("  4. Vinyl Preparation - Stereo FLAC para cutting master")
    console.print("  5. Broadcast - Mono MP3 para radio")
    console.print("  6. Mono Compatibility Test - Test de compatibilidad mono")

    workflow_mode = Prompt.ask(
        "Selecciona modo",
        choices=["1", "2", "3", "4", "5", "6"],
        default="2"
    )

    # Channel conversion option (solo para modos 1, 2, 3)
    channel_conversion = None
    mixing_algorithm = "downmix_center"

    if workflow_mode in ["1", "2", "3"]:
        console.print("\n[cyan]🎧 Conversión de canales:[/cyan]")
        console.print("  1. Mantener original (no conversión)")
        console.print("  2. Convertir a Mono (voice/broadcast)")
        console.print("  3. Convertir a Stereo (vinyl/streaming)")

        channel_choice = Prompt.ask(
            "Selecciona opción",
            choices=["1", "2", "3"],
            default="1"
        )

        if channel_choice == "2":
            channel_conversion = "mono"
            # Ask for mixing algorithm
            console.print("\n[cyan]Algoritmo de mixing (stereo→mono):[/cyan]")
            console.print("  1. Downmix Center (profesional, mantiene balance)")
            console.print("  2. Left Only (solo canal izquierdo)")
            console.print("  3. Right Only (solo canal derecho)")
            console.print("  4. Average (promedio simple L+R)")

            algo_choice = Prompt.ask(
                "Selecciona algoritmo",
                choices=["1", "2", "3", "4"],
                default="1"
            )

            algo_map = {
                "1": "downmix_center",
                "2": "left_only",
                "3": "right_only",
                "4": "average"
            }
            mixing_algorithm = algo_map[algo_choice]

        elif channel_choice == "3":
            channel_conversion = "stereo"

    if workflow_mode == "1":
        # Quick workflow
        track_title = Prompt.ask("Título del track", default="Untitled Track")
        artist_name = Prompt.ask("Nombre del artista", default="Unknown Artist")
        album_name = Prompt.ask("Nombre del álbum", default="Single")

        workflow = create_quick_mastering_workflow(
            input_file=input_file,
            output_dir=output_dir,
            track_title=track_title,
            artist_name=artist_name,
            album_name=album_name
        )

    elif workflow_mode == "2":
        # Standard workflow
        track_title = Prompt.ask("Título del track", default="Untitled Track")
        artist_name = Prompt.ask("Nombre del artista", default="Unknown Artist")
        album_name = Prompt.ask("Nombre del álbum", default="Single")
        genre = Prompt.ask("Género musical", default="Music")

        metadata = {
            'title': track_title,
            'artist': artist_name,
            'album': album_name,
            'genre': genre
        }

        workflow = create_music_mastering_workflow(
            input_file=input_file,
            output_dir=output_dir,
            metadata=metadata,
            quality_profile="professional",
            channel_conversion=channel_conversion,
            mixing_algorithm=mixing_algorithm,
            include_flac=True,
            include_mp3=True,
            generate_analysis=False
        )

    elif workflow_mode == "3":
        # Professional workflow
        track_title = Prompt.ask("Título del track", default="Untitled Track")
        artist_name = Prompt.ask("Nombre del artista", default="Unknown Artist")
        album_name = Prompt.ask("Nombre del álbum", default="Single")
        track_number = int(Prompt.ask("Número de track", default="1"))
        total_tracks = int(Prompt.ask("Total de tracks", default="1"))
        genre = Prompt.ask("Género musical", default="Music")
        isrc = Prompt.ask("ISRC (Enter para omitir)", default="")
        production_credits = Prompt.ask("Créditos de producción (Enter para omitir)", default="")

        workflow = create_professional_mastering_workflow(
            input_file=input_file,
            output_dir=output_dir,
            track_title=track_title,
            artist_name=artist_name,
            album_name=album_name,
            track_number=track_number,
            total_tracks=total_tracks,
            genre=genre,
            channel_conversion=channel_conversion,
            mixing_algorithm=mixing_algorithm,
            isrc=isrc if isrc else None,
            production_credits=production_credits if production_credits else None
        )

    elif workflow_mode == "4":
        # Vinyl Preparation workflow
        from ..core.workflows.music_workflow import create_vinyl_preparation_workflow

        track_title = Prompt.ask("Título del track", default="Untitled Track")
        artist_name = Prompt.ask("Nombre del artista", default="Unknown Artist")
        album_name = Prompt.ask("Nombre del álbum", default="Single")
        genre = Prompt.ask("Género musical", default="Music")

        metadata = {
            'title': track_title,
            'artist': artist_name,
            'album': album_name,
            'genre': genre,
            'comment': 'Vinyl Cutting Master'
        }

        workflow = create_vinyl_preparation_workflow(
            input_file=input_file,
            output_dir=output_dir,
            metadata=metadata
        )

    elif workflow_mode == "5":
        # Broadcast mastering workflow
        from ..core.workflows.music_workflow import create_broadcast_mastering_workflow

        track_title = Prompt.ask("Título del track", default="Untitled Track")
        artist_name = Prompt.ask("Nombre del artista", default="Unknown Artist")
        station_name = Prompt.ask("Nombre de la estación/emisora", default="Radio Station")

        metadata = {
            'title': track_title,
            'artist': artist_name,
            'album': station_name,
            'genre': 'Broadcast',
            'comment': 'Radio Broadcast Master'
        }

        workflow = create_broadcast_mastering_workflow(
            input_file=input_file,
            output_dir=output_dir,
            metadata=metadata,
            mixing_algorithm="downmix_center"
        )

    else:  # workflow_mode == "6"
        # Mono compatibility test workflow
        from ..core.workflows.music_workflow import create_mono_compatibility_workflow

        track_title = Prompt.ask("Título del track", default="Untitled Track")
        artist_name = Prompt.ask("Nombre del artista", default="Unknown Artist")
        album_name = Prompt.ask("Nombre del álbum", default="Single")

        metadata = {
            'title': track_title,
            'artist': artist_name,
            'album': album_name,
            'genre': 'Music',
            'comment': 'Mono Compatibility Test'
        }

        workflow = create_mono_compatibility_workflow(
            input_file=input_file,
            output_dir=output_dir,
            metadata=metadata
        )

    # Ejecutar workflow
    console.print("\n[bold green]🚀 Ejecutando Music Mastering Workflow...[/bold green]")

    try:
        results = workflow.execute(show_progress=True)
        display_workflow_results(results)
    except Exception as e:
        console.print(f"[red]❌ Error ejecutando workflow: {e}[/red]")


def run_audiobook_workflow():
    """
    Interfaz para Audiobook Production Workflow
    """
    console.print("\n[bold cyan]📖 Audiobook Production Workflow[/bold cyan]")

    # Input file
    input_file = Prompt.ask("📁 Archivo de audio del audiobook")

    if not Path(input_file).exists():
        console.print("[red]❌ Archivo no encontrado[/red]")
        return

    # Output directory
    output_dir = Prompt.ask("📂 Directorio de salida", default="./audiobook_output")

    # Workflow mode
    console.print("\n[cyan]🎯 Modo de workflow:[/cyan]")
    console.print("  1. Quick - Rápido sin validación")
    console.print("  2. Standard - Con validación de calidad")
    console.print("  3. Professional - Validación completa para distribución")

    workflow_mode = Prompt.ask(
        "Selecciona modo",
        choices=["1", "2", "3"],
        default="2"
    )

    if workflow_mode == "1":
        # Quick workflow
        chapter_title = Prompt.ask("Título del capítulo", default="Chapter 1")
        author_name = Prompt.ask("Nombre del autor", default="Author Name")
        book_title = Prompt.ask("Título del libro", default="Book Title")
        narrator_name = Prompt.ask("Nombre del narrador", default="Narrator")

        workflow = create_quick_audiobook_workflow(
            input_file=input_file,
            output_dir=output_dir,
            chapter_title=chapter_title,
            author_name=author_name,
            book_title=book_title,
            narrator_name=narrator_name
        )

    elif workflow_mode == "2":
        # Standard workflow
        chapter_title = Prompt.ask("Título del capítulo", default="Chapter 1")
        author_name = Prompt.ask("Nombre del autor", default="Author Name")
        book_title = Prompt.ask("Título del libro", default="Book Title")
        narrator_name = Prompt.ask("Nombre del narrador", default="Narrator")

        metadata = {
            'title': chapter_title,
            'artist': author_name,
            'album': book_title,
            'genre': 'Audiobook',
            'comment': f'Narrated by {narrator_name}'
        }

        workflow = create_audiobook_workflow(
            input_file=input_file,
            output_dir=output_dir,
            metadata=metadata,
            quality_validation=True,
            mono_conversion=True
        )

    else:
        # Professional workflow
        chapter_title = Prompt.ask("Título del capítulo", default="Chapter 1")
        chapter_number = int(Prompt.ask("Número de capítulo", default="1"))
        total_chapters = int(Prompt.ask("Total de capítulos", default="1"))
        author_name = Prompt.ask("Nombre del autor", default="Author Name")
        book_title = Prompt.ask("Título del libro", default="Book Title")
        narrator_name = Prompt.ask("Nombre del narrador", default="Narrator")
        isbn = Prompt.ask("ISBN (Enter para omitir)", default="")
        publisher = Prompt.ask("Editorial (Enter para omitir)", default="")

        workflow = create_professional_audiobook_workflow(
            input_file=input_file,
            output_dir=output_dir,
            chapter_title=chapter_title,
            chapter_number=chapter_number,
            total_chapters=total_chapters,
            author_name=author_name,
            book_title=book_title,
            narrator_name=narrator_name,
            isbn=isbn if isbn else None,
            publisher=publisher if publisher else None
        )

    # Ejecutar workflow
    console.print("\n[bold green]🚀 Ejecutando Audiobook Production Workflow...[/bold green]")

    try:
        results = workflow.execute(show_progress=True)
        display_workflow_results(results)
    except Exception as e:
        console.print(f"[red]❌ Error ejecutando workflow: {e}[/red]")


def display_workflow_results(results: Dict[str, Any]):
    """
    Mostrar resultados de ejecución de workflow
    """
    console.print("\n" + "="*60)

    # Status general
    if results.get('success', False):
        console.print(f"[bold green]✅ Workflow Completado Exitosamente[/bold green]")
    else:
        console.print(f"[bold red]❌ Workflow Fallido[/bold red]")

    # Tabla de resultados
    table = Table(title="Resultados del Workflow", show_header=True, header_style="bold cyan")
    table.add_column("Métrica", style="white", width=30)
    table.add_column("Valor", style="green", width=25)

    table.add_row("Workflow", results.get('workflow_name', 'Unknown'))
    table.add_row("Steps Completados", f"{results.get('steps_completed', 0)}/{results.get('total_steps', 0)}")
    table.add_row("Duración Total", f"{results.get('duration', 0):.2f}s")
    table.add_row("Estado Final", "✅ Exitoso" if results.get('success') else "❌ Fallido")

    if results.get('failed_step'):
        table.add_row("Step Fallido", results.get('failed_step', 'Unknown'))

    console.print(table)

    # Detalle de steps
    if 'steps_summary' in results:
        console.print("\n[cyan]📊 Detalle de Steps:[/cyan]")
        for step in results['steps_summary']:
            status_icon = "✓" if step.get('success') else "✗"
            status_color = "green" if step.get('success') else "red"
            duration = step.get('duration', 0)
            console.print(f"  [{status_color}]{status_icon}[/{status_color}] {step['name']} ({duration:.2f}s)")

    console.print("="*60 + "\n")


if __name__ == "__main__":
    run_professional_workflows()
