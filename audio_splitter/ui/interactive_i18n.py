"""
Interfaz interactiva multiidioma del Audio Splitter Suite 2.0
Sistema completo con soporte i18n y funcionalidades avanzadas
Incluye Channel Converter y Professional Workflows
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table

# Imports del sistema i18n
from ..i18n.translator import t

# Imports de las funcionalidades mejoradas
from ..core.enhanced_converter import EnhancedAudioConverter
from ..core.enhanced_splitter import EnhancedAudioSplitter
from ..core.enhanced_spectrogram import EnhancedSpectrogramGenerator
from ..config.quality_settings import get_quality_settings, QualityProfile
from ..ui.cli import display_quality_metrics
from ..ui.channel_interface import run_channel_converter
from ..ui.workflow_interface import run_professional_workflows
from ..ui.batch_interface import run_batch_processing

console = Console()

def interactive_menu_i18n():
    """Menú principal interactivo multiidioma del sistema Audio Splitter Suite"""
    
    console.print(Panel(
        f"[bold blue]{t('menu.title', '🎵 Audio Splitter Suite 2.0')}[/bold blue]\\n" +
        f"[dim]{t('menu.subtitle', 'Sistema completo de procesamiento de audio')}[/dim]",
        title=t('menu.panel_title', 'Audio Processing Suite')
    ))
    
    while True:
        # Mostrar estado de calidad actual
        settings = get_quality_settings()
        profile = settings.preferences.default_profile
        profile_emoji = {"studio": "🏆", "professional": "✅", "standard": "⚡", "basic": "📱", "custom": "🔧"}
        quality_emoji = profile_emoji.get(profile.value, "❓")
        enhanced_status = t('menu.enhanced_status', '🔬 MEJORADO') if settings.preferences.prefer_enhanced_algorithms else t('menu.standard_status', '⚡ ESTÁNDAR')
        
        console.print(f"\\n[dim]{t('menu.current_quality', 'Calidad actual: {quality_emoji} {profile} | Algoritmos: {enhanced_status}').format(quality_emoji=quality_emoji, profile=profile.value.upper(), enhanced_status=enhanced_status)}[/dim]")
        
        console.print(f"\\n[cyan]{t('menu.modules_available', '🎛️ Módulos disponibles:')}:[/cyan]")
        options = [
            f"1. {t('menu.audio_converter', '🔄 Audio Converter - Conversión entre formatos (WAV/MP3/FLAC)')}",
            f"2. {t('menu.audio_splitter', '✂️  Audio Splitter - División en segmentos con metadatos')}",
            f"3. {t('menu.metadata_editor', '🏷️  Metadata Editor - Editor profesional de metadatos')}",
            f"4. {t('menu.spectrogram_generator', '📊 Spectrogram Generator - Generación de espectrogramas para LLMs')}",
            f"5. {t('menu.channel_converter', '🎧 Channel Converter - Conversión mono ↔ stereo')}",
            f"6. {t('menu.workflows', '🔄 Professional Workflows - Automatización de procesos')}",
            f"7. {t('menu.batch_processing', '📦 Batch Processing - Procesamiento masivo de archivos')}",
            f"8. {t('menu.exit', '🚪 Salir')}"
        ]

        for option in options:
            console.print(f"  {option}")

        choice = Prompt.ask(f"\\n{t('menu.select_module', 'Selecciona un módulo')}", choices=["1", "2", "3", "4", "5", "6", "7", "8"])
        
        if choice == "1":
            run_audio_converter_i18n()
        elif choice == "2":
            run_audio_splitter_i18n()
        elif choice == "3":
            run_metadata_editor_i18n()
        elif choice == "4":
            run_spectrogram_generator_i18n()
        elif choice == "5":
            run_channel_converter_i18n()
        elif choice == "6":
            run_professional_workflows_i18n()
        elif choice == "7":
            run_batch_processing_i18n()
        elif choice == "8":
            console.print(f"\\n[yellow]{t('menu.goodbye', '👋 ¡Gracias por usar Audio Splitter Suite!')}[/yellow]")
            break

def run_channel_converter_i18n():
    """Ejecuta el Channel Converter con interfaz multiidioma"""
    try:
        console.print(f"\\n[bold green]✓ {t('channel.title', '🎧 Channel Converter Enhanced')}[/bold green]")
        
        # Ejecutar la interfaz de channel converter
        run_channel_converter()
        
        # Preguntar si continuar
        if not Confirm.ask(f"\\n{t('common.continue_question', '¿Realizar otra operación?')}", default=False):
            console.print(f"[cyan]{t('common.back_to_menu', '🔙 Volver al menú principal')}[/cyan]")
            
    except Exception as e:
        console.print(f"[red]{t('common.error', '❌ Error')}: {str(e)}[/red]")

def run_audio_converter_i18n():
    """Ejecuta el Audio Converter con interfaz multiidioma"""
    try:
        converter = EnhancedAudioConverter()
        
        console.print(Panel(
            f"[bold blue]{t('converter.title', '🔄 Audio Converter Enhanced')}[/bold blue]\\n" +
            f"[dim]{t('converter.subtitle', 'Conversión entre formatos con algoritmos mejorados')}[/dim]",
            title=t('converter.panel_title', 'Audio Converter')
        ))
        
        while True:
            console.print(f"\\n[cyan]{t('common.processing_mode', '🔧 Modo de procesamiento')}:[/cyan]")
            mode_options = [
                f"1. {t('common.single', 'Individual')} - {t('converter.single_desc', 'Convertir un archivo')}",
                f"2. {t('common.batch', 'Por lotes')} - {t('converter.batch_desc', 'Convertir múltiples archivos')}",
                f"3. {t('common.back_to_menu', '🔙 Volver al menú principal')}"
            ]
            
            for option in mode_options:
                console.print(f"  {option}")
            
            mode_choice = Prompt.ask(
                t('converter.select_mode', 'Selecciona modo'),
                choices=["1", "2", "3"],
                default="1"
            )
            
            if mode_choice == "1":
                run_single_conversion_i18n(converter)
            elif mode_choice == "2":
                run_batch_conversion_i18n(converter)
            elif mode_choice == "3":
                break
                
    except Exception as e:
        console.print(f"[red]{t('converter.execution_error', '❌ Error ejecutando Audio Converter: {error}').format(error=str(e))}[/red]")

def run_single_conversion_i18n(converter: EnhancedAudioConverter):
    """Ejecuta conversión individual con i18n"""
    try:
        # Input file
        input_file = Prompt.ask(f"{t('common.input_file', '🎧 Archivo de audio de entrada')}")
        
        if not Path(input_file).exists():
            console.print(f"[red]{t('common.file_not_found', '❌ Archivo no encontrado')}[/red]")
            return
        
        # Output file
        output_file = Prompt.ask(f"{t('common.output_file', '📁 Archivo de salida')}")
        
        # Format selection
        console.print(f"\\n[cyan]{t('converter.format_selection', '📁 Formato de salida')}:[/cyan]")
        formats = ["wav", "mp3", "flac"]
        for i, fmt in enumerate(formats, 1):
            console.print(f"  {i}. {fmt.upper()}")
        
        format_choice = Prompt.ask(
            t('converter.select_format', 'Selecciona formato'),
            choices=["1", "2", "3"],
            default="1"
        )
        
        format_map = {"1": "wav", "2": "mp3", "3": "flac"}
        output_format = format_map[format_choice]
        
        # Quality validation
        enable_validation = Confirm.ask(
            t('converter.enable_validation', '🔬 ¿Activar validación de calidad?'),
            default=True
        )
        
        # Convert
        console.print(f"\\n[cyan]{t('converter.starting_conversion', 'Iniciando conversión {format}...').format(format=output_format.upper())}[/cyan]")
        
        if enable_validation:
            # Use enhanced converter with quality validation
            result = converter.convert_with_quality_validation(
                input_path=input_file,
                output_path=output_file,
                target_format=output_format,
                quality='high'
            )
        else:
            # Use basic conversion (returns bool)
            success = converter.convert_file(
                input_path=input_file,
                output_path=output_file,
                target_format=output_format,
                quality='high'
            )
            result = {'success': success}
        
        if result.get('success', False):
            console.print(f"[green]✓ {t('converter.conversion_success', 'Conversión exitosa')}[/green]")

            if enable_validation and 'quality_metrics' in result:
                console.print(f"[dim]{t('converter.quality_validated', '🔬 Conversión con validación de calidad completada')}[/dim]")
        else:
            error_msg = result.get('error', 'Unknown error')
            console.print(f"[red]✗ {t('converter.conversion_error', 'Error en conversión: {error}').format(error=error_msg)}[/red]")
            
    except Exception as e:
        console.print(f"[red]{t('converter.execution_error', '❌ Error: {error}').format(error=str(e))}[/red]")

def run_batch_conversion_i18n(converter: EnhancedAudioConverter):
    """Ejecuta conversión por lotes con i18n"""
    try:
        console.print(f"\n[bold green]✓ {t('batch.title', '📦 Batch Processing')}[/bold green]")
        # Llamar a la interfaz completa de batch processing
        run_batch_processing()
    except Exception as e:
        console.print(f"[red]{t('common.error', '❌ Error')}: {str(e)}[/red]")

def run_audio_splitter_i18n():
    """Ejecuta el Audio Splitter con interfaz multiidioma"""
    try:
        # Import the working implementation from interactive.py
        from .interactive import run_audio_splitter
        console.print(f"\n[bold green]✓ {t('splitter.title', '✂️ Audio Splitter Enhanced')}[/bold green]")
        run_audio_splitter()
    except Exception as e:
        console.print(f"[red]{t('common.error', '❌ Error')}: {str(e)}[/red]")

def run_metadata_editor_i18n():
    """Ejecuta el Metadata Editor con interfaz multiidioma"""
    try:
        # Import the working implementation from interactive.py
        from .interactive import run_metadata_editor
        console.print(f"\n[bold green]✓ {t('metadata.title', '🏷️ Metadata Editor')}[/bold green]")
        run_metadata_editor()
    except Exception as e:
        console.print(f"[red]{t('common.error', '❌ Error')}: {str(e)}[/red]")

def run_spectrogram_generator_i18n():
    """Ejecuta el Spectrogram Generator con interfaz multiidioma"""
    try:
        # Import the working implementation from interactive.py
        from .interactive import run_spectrogram_generator
        console.print(f"\n[bold green]✓ {t('spectrogram.title', '📊 Spectrogram Generator')}[/bold green]")
        run_spectrogram_generator()
    except Exception as e:
        console.print(f"[red]{t('common.error', '❌ Error')}: {str(e)}[/red]")

def run_professional_workflows_i18n():
    """Ejecuta Professional Workflows con interfaz multiidioma"""
    try:
        console.print(f"\\n[bold green]✓ {t('workflows.title', '🔄 Professional Workflows')}[/bold green]")

        # Ejecutar la interfaz de workflows
        run_professional_workflows()

    except Exception as e:
        console.print(f"[red]{t('common.error', '❌ Error')}: {str(e)}[/red]")

def run_batch_processing_i18n():
    """Ejecuta Batch Processing con interfaz multiidioma"""
    try:
        console.print(f"\\n[bold green]✓ {t('batch.title', '📦 Batch Processing')}[/bold green]")

        # Ejecutar la interfaz de batch processing
        run_batch_processing()

    except Exception as e:
        console.print(f"[red]{t('common.error', '❌ Error')}: {str(e)}[/red]")

# Funciones eliminadas: run_artwork_manager_i18n(), run_quality_settings_i18n(), show_documentation_i18n()
# Sistema de quality settings sigue funcionando con defaults profesionales

# Entry point principal para la versión i18n
if __name__ == "__main__":
    console.print("[cyan]Testing Interactive I18n Interface...[/cyan]")
    interactive_menu_i18n()