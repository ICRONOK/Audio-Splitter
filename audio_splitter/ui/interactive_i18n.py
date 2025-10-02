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
            f"7. {t('menu.artwork_manager', '🖼️  Artwork Manager - Gestión de carátulas')}",
            f"8. {t('menu.quality_settings', '⚙️  Quality Settings - Configuración de calidad científica')}",
            f"9. {t('menu.documentation', '📄 Documentación y ayuda')}",
            f"10. {t('menu.exit', '🚪 Salir')}"
        ]
        
        for option in options:
            console.print(f"  {option}")
        
        choice = Prompt.ask(f"\\n{t('menu.select_module', 'Selecciona un módulo')}", choices=["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"])
        
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
            run_artwork_manager_i18n()
        elif choice == "8":
            run_quality_settings_i18n()
        elif choice == "9":
            show_documentation_i18n()
        elif choice == "10":
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
        
        result = converter.convert_audio(
            input_file, output_file, output_format,
            quality_validation=enable_validation
        )
        
        if result.get('success', False):
            console.print(f"[green]✓ {t('converter.conversion_success', 'Conversión exitosa')}[/green]")
            
            if enable_validation and 'quality_result' in result:
                quality = result['quality_result']
                level_emoji = {"excellent": "🟢", "good": "🟡", "acceptable": "🟠", "poor": "🔴", "failed": "❌"}
                emoji = level_emoji.get(quality.overall_quality.value, "❓")
                console.print(f"[dim]{t('converter.quality_result', 'Calidad del resultado: {emoji} {level}').format(emoji=emoji, level=quality.overall_quality.value.upper())}[/dim]")
        else:
            console.print(f"[red]✗ {t('converter.conversion_error', 'Error en conversión')}[/red]")
            
    except Exception as e:
        console.print(f"[red]{t('converter.execution_error', '❌ Error: {error}').format(error=str(e))}[/red]")

def run_batch_conversion_i18n(converter: EnhancedAudioConverter):
    """Ejecuta conversión por lotes con i18n"""
    console.print(f"[yellow]{t('converter.batch_coming_soon', '📦 Conversión por lotes - Próximamente en Fase 2')}[/yellow]")

def run_audio_splitter_i18n():
    """Ejecuta el Audio Splitter con interfaz multiidioma"""
    console.print(f"[yellow]{t('splitter.coming_soon', '✂️ Audio Splitter multiidioma - Próximamente')}[/yellow]")

def run_metadata_editor_i18n():
    """Ejecuta el Metadata Editor con interfaz multiidioma"""
    console.print(f"[yellow]{t('metadata.coming_soon', '🏷️ Metadata Editor multiidioma - Próximamente')}[/yellow]")

def run_spectrogram_generator_i18n():
    """Ejecuta el Spectrogram Generator con interfaz multiidioma"""
    console.print(f"[yellow]{t('spectrogram.coming_soon', '📊 Spectrogram Generator multiidioma - Próximamente')}[/yellow]")

def run_professional_workflows_i18n():
    """Ejecuta Professional Workflows (Fase 2)"""
    console.print(f"[yellow]{t('workflows.coming_soon', '🔄 Professional Workflows - Implementación en Fase 2')}[/yellow]")

def run_artwork_manager_i18n():
    """Ejecuta el Artwork Manager con interfaz multiidioma"""
    console.print(f"[yellow]{t('artwork.coming_soon', '🖼️ Artwork Manager multiidioma - Próximamente')}[/yellow]")

def run_quality_settings_i18n():
    """Ejecuta la configuración de calidad científica con i18n"""
    try:
        settings = get_quality_settings()
        
        console.print(Panel(
            f"[bold blue]{t('quality.title', '⚙️ Configuración de Calidad Científica')}[/bold blue]\\n" +
            f"[dim]{t('quality.subtitle', 'Gestiona perfiles y preferencias de calidad')}[/dim]",
            title=t('quality.panel_title', 'Quality Settings')
        ))
        
        while True:
            console.print(f"\\n[cyan]{t('quality.options_title', '🔧 Opciones de configuración:')}:[/cyan]")
            options = [
                f"1. {t('quality.show_current', '📊 Ver configuración actual')}",
                f"2. {t('quality.change_profile', '🏆 Cambiar perfil de calidad')}",
                f"3. {t('quality.configure_preferences', '⚙️ Configurar preferencias')}",
                f"4. {t('quality.custom_thresholds', '🔧 Umbrales personalizados')}",
                f"5. {t('quality.reset_defaults', '🔄 Restablecer a valores por defecto')}",
                f"6. {t('common.back_to_menu', '🔙 Volver al menú principal')}"
            ]
            
            for option in options:
                console.print(f"  {option}")
            
            choice = Prompt.ask(
                t('quality.select_option', 'Selecciona opción'),
                choices=["1", "2", "3", "4", "5", "6"]
            )
            
            if choice == "1":
                show_current_quality_settings_i18n(settings)
            elif choice == "2":
                change_quality_profile_i18n()
            elif choice == "3":
                configure_quality_preferences_i18n()
            elif choice == "4":
                configure_custom_thresholds_i18n()
            elif choice == "5":
                reset_quality_defaults_i18n()
            elif choice == "6":
                break
                
    except Exception as e:
        console.print(f"[red]{t('quality.error_quality', '❌ Error en configuración de calidad: {error}').format(error=str(e))}[/red]")

def show_current_quality_settings_i18n(settings):
    """Muestra configuración actual con i18n"""
    console.print(f"\\n[bold cyan]{t('quality.current_settings', '📊 Configuración Actual')}:[/bold cyan]")
    
    # Profile info
    profile = settings.preferences.default_profile
    profile_emoji = {"studio": "🏆", "professional": "✅", "standard": "⚡", "basic": "📱", "custom": "🔧"}
    emoji = profile_emoji.get(profile.value, "❓")
    
    console.print(f"[white]{t('quality.active_profile', 'Perfil activo')}: {emoji} {profile.value.upper()}[/white]")
    console.print(f"[white]{t('quality.enhanced_algorithms', 'Algoritmos mejorados')}: {'✅' if settings.preferences.prefer_enhanced_algorithms else '❌'}[/white]")
    console.print(f"[white]{t('quality.validation_enabled', 'Validación activada')}: {'✅' if settings.preferences.enable_quality_validation else '❌'}[/white]")
    console.print(f"[white]{t('quality.metrics_display', 'Mostrar métricas')}: {'✅' if settings.preferences.show_detailed_metrics else '❌'}[/white]")

def change_quality_profile_i18n():
    """Cambia perfil de calidad con i18n"""
    console.print(f"[yellow]{t('quality.profile_change_coming_soon', '🏆 Cambio de perfil - Implementación completa próximamente')}[/yellow]")

def configure_quality_preferences_i18n():
    """Configura preferencias con i18n"""
    console.print(f"[yellow]{t('quality.preferences_coming_soon', '⚙️ Configuración de preferencias - Próximamente')}[/yellow]")

def configure_custom_thresholds_i18n():
    """Configura umbrales personalizados con i18n"""
    console.print(f"[yellow]{t('quality.thresholds_coming_soon', '🔧 Umbrales personalizados - Próximamente')}[/yellow]")

def reset_quality_defaults_i18n():
    """Restablece valores por defecto con i18n"""
    console.print(f"[yellow]{t('quality.reset_coming_soon', '🔄 Restablecimiento - Próximamente')}[/yellow]")

def show_documentation_i18n():
    """Muestra documentación con i18n"""
    console.print(f"[yellow]{t('documentation.coming_soon', '📄 Documentación multiidioma - Próximamente')}[/yellow]")

# Entry point principal para la versión i18n
if __name__ == "__main__":
    console.print("[cyan]Testing Interactive I18n Interface...[/cyan]")
    interactive_menu_i18n()