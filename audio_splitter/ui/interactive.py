"""
Interfaz interactiva principal del Audio Splitter Suite
Integración con sistema de calidad científica
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table

# Imports de las funcionalidades mejoradas
from ..core.enhanced_converter import EnhancedAudioConverter
from ..core.enhanced_splitter import EnhancedAudioSplitter
from ..core.enhanced_spectrogram import EnhancedSpectrogramGenerator
from ..config.quality_settings import get_quality_settings, QualityProfile
from ..ui.cli import display_quality_metrics

console = Console()

def interactive_menu():
    """Menú principal interactivo del sistema Audio Splitter Suite"""
    
    console.print(Panel(
        "[bold blue]🎵 Audio Splitter Suite 2.0[/bold blue]\n" +
        "[dim]Sistema completo de procesamiento de audio[/dim]",
        title="Audio Processing Suite"
    ))
    
    while True:
        # Mostrar estado de calidad actual
        settings = get_quality_settings()
        profile = settings.preferences.default_profile
        profile_emoji = {"studio": "🏆", "professional": "✅", "standard": "⚡", "basic": "📱", "custom": "🔧"}
        quality_emoji = profile_emoji.get(profile.value, "❓")
        enhanced_status = "🔬 MEJORADO" if settings.preferences.prefer_enhanced_algorithms else "⚡ ESTÁNDAR"
        
        console.print(f"\n[dim]Calidad actual: {quality_emoji} {profile.value.upper()} | Algoritmos: {enhanced_status}[/dim]")
        
        console.print("\n[cyan]🎛️ Módulos disponibles:[/cyan]")
        options = [
            "1. 🔄 Audio Converter - Conversión entre formatos (WAV/MP3/FLAC)",
            "2. ✂️  Audio Splitter - División en segmentos con metadatos",
            "3. 🏷️  Metadata Editor - Editor profesional de metadatos",
            "4. 📊 Spectrogram Generator - Generación de espectrogramas para LLMs",
            "5. 🖼️  Artwork Manager - Gestión de carátulas",
            "6. ⚙️  Quality Settings - Configuración de calidad científica",
            "7. 📄 Documentación y ayuda",
            "8. 🚪 Salir"
        ]
        
        for option in options:
            console.print(f"  {option}")
        
        choice = Prompt.ask("\nSelecciona un módulo", choices=["1", "2", "3", "4", "5", "6", "7", "8"])
        
        if choice == "1":
            run_audio_converter()
        elif choice == "2":
            run_audio_splitter()
        elif choice == "3":
            run_metadata_editor()
        elif choice == "4":
            run_spectrogram_generator()
        elif choice == "5":
            run_artwork_manager()
        elif choice == "6":
            run_quality_settings()
        elif choice == "7":
            show_documentation()
        elif choice == "8":
            console.print("\n[yellow]👋 ¡Gracias por usar Audio Splitter Suite![/yellow]")
            break

def run_quality_settings():
    """Ejecuta la configuración de calidad científica"""
    try:
        settings = get_quality_settings()
        
        console.print(Panel(
            "[bold blue]⚙️ Configuración de Calidad Científica[/bold blue]\n" +
            "[dim]Gestiona perfiles y preferencias de calidad[/dim]",
            title="Quality Settings"
        ))
        
        while True:
            console.print("\n[cyan]🔧 Opciones de configuración:[/cyan]")
            options = [
                "1. 📊 Ver configuración actual",
                "2. 🏆 Cambiar perfil de calidad",
                "3. ⚙️ Configurar preferencias",
                "4. 🔧 Umbrales personalizados",
                "5. 🔄 Restablecer a valores por defecto",
                "6. 🔙 Volver al menú principal"
            ]
            
            for option in options:
                console.print(f"  {option}")
            
            choice = Prompt.ask("\nSelecciona una opción", choices=["1", "2", "3", "4", "5", "6"])
            
            if choice == "1":
                # Mostrar configuración actual
                show_current_quality_settings(settings)
            
            elif choice == "2":
                # Cambiar perfil de calidad
                change_quality_profile(settings)
            
            elif choice == "3":
                # Configurar preferencias
                configure_quality_preferences(settings)
            
            elif choice == "4":
                # Umbrales personalizados
                configure_custom_thresholds(settings)
            
            elif choice == "5":
                # Restablecer valores por defecto
                if Confirm.ask("\n⚠️ ¿Estás seguro de restablecer toda la configuración?"):
                    settings.reset_to_defaults()
                    console.print("[green]✓ Configuración restablecida a valores por defecto[/green]")
                else:
                    console.print("[yellow]Operación cancelada[/yellow]")
            
            elif choice == "6":
                break
    
    except Exception as e:
        console.print(f"[red]❌ Error en configuración de calidad: {e}[/red]")

def show_current_quality_settings(settings):
    """Muestra la configuración actual de calidad"""
    prefs = settings.preferences
    
    table = Table(title="🔧 Configuración Actual", show_header=True, header_style="bold cyan")
    table.add_column("Configuración", style="white", width=25)
    table.add_column("Valor", style="green", width=20)
    table.add_column("Descripción", style="dim", width=30)
    
    # Perfil de calidad
    profile_emoji = {"studio": "🏆", "professional": "✅", "standard": "⚡", "basic": "📱", "custom": "🔧"}
    emoji = profile_emoji.get(prefs.default_profile.value, "❓")
    table.add_row("Perfil de Calidad", f"{emoji} {prefs.default_profile.value.upper()}", "Nivel de exigencia de calidad")
    
    # Configuraciones principales
    validation_status = "✅ ACTIVADA" if prefs.enable_quality_validation else "❌ DESACTIVADA"
    table.add_row("Validación de Calidad", validation_status, "Análisis automático THD+N/SNR")
    
    metrics_status = "✅ SÍ" if prefs.show_metrics_by_default else "❌ NO"
    table.add_row("Mostrar Métricas", metrics_status, "Mostrar resultados detallados")
    
    enhanced_status = "🔬 SÍ" if prefs.prefer_enhanced_algorithms else "⚡ NO"
    table.add_row("Algoritmos Mejorados", enhanced_status, "Usar versiones científicas")
    
    fade_status = "✅ SÍ" if prefs.enable_cross_fade else "❌ NO"
    table.add_row("Cross-fade", fade_status, "Transiciones suaves en split")
    
    dither_status = "✅ SÍ" if prefs.enable_dithering else "❌ NO"
    table.add_row("Dithering", dither_status, "Reducir ruido de cuantización")
    
    console.print(table)
    
    # Mostrar umbrales
    thresholds = settings.get_quality_thresholds()
    console.print(f"\n[bold cyan]📊 Umbrales Actuales:[/bold cyan]")
    console.print(f"[white]THD+N:[/white] < {thresholds['thd_threshold']:.1f} dB")
    console.print(f"[white]SNR:[/white] > {thresholds['snr_threshold']:.1f} dB") 
    console.print(f"[white]Rango Dinámico:[/white] > {thresholds['dynamic_range_min']:.1f}%")

def change_quality_profile(settings):
    """Cambiar el perfil de calidad"""
    console.print("\n[cyan]🏆 Perfiles de Calidad Disponibles:[/cyan]")
    
    profiles = [
        ("studio", "🏆", "Studio Mastering - THD+N <-80dB, SNR >100dB - Máxima calidad"),
        ("professional", "✅", "Professional - THD+N <-60dB, SNR >90dB - Broadcast/Producción"),
        ("standard", "⚡", "Standard - THD+N <-40dB, SNR >70dB - Electrónicos de consumo"),
        ("basic", "📱", "Basic - THD+N <-30dB, SNR >60dB - Streaming web"),
        ("custom", "🔧", "Custom - Umbrales personalizados por el usuario")
    ]
    
    for i, (key, emoji, description) in enumerate(profiles, 1):
        console.print(f"  {i}. {emoji} {key.upper()} - {description}")
    
    choice = Prompt.ask("\nSelecciona un perfil", choices=["1", "2", "3", "4", "5"])
    
    profile_map = {
        "1": QualityProfile.STUDIO,
        "2": QualityProfile.PROFESSIONAL, 
        "3": QualityProfile.STANDARD,
        "4": QualityProfile.BASIC,
        "5": QualityProfile.CUSTOM
    }
    
    new_profile = profile_map[choice]
    success = settings.set_profile(new_profile)
    
    if success:
        profile_name = profiles[int(choice)-1]
        console.print(f"[green]✓ Perfil establecido: {profile_name[1]} {profile_name[0].upper()}[/green]")
    else:
        console.print("[red]❌ Error estableciendo el perfil[/red]")

def configure_quality_preferences(settings):
    """Configurar preferencias generales de calidad"""
    prefs = settings.preferences
    
    console.print("\n[cyan]⚙️ Configurar Preferencias:[/cyan]")
    
    # Validación de calidad
    enable_validation = Confirm.ask(
        f"¿Activar validación de calidad por defecto? (actual: {'SÍ' if prefs.enable_quality_validation else 'NO'})",
        default=prefs.enable_quality_validation
    )
    prefs.enable_quality_validation = enable_validation
    
    # Mostrar métricas
    show_metrics = Confirm.ask(
        f"¿Mostrar métricas detalladas por defecto? (actual: {'SÍ' if prefs.show_metrics_by_default else 'NO'})",
        default=prefs.show_metrics_by_default
    )
    prefs.show_metrics_by_default = show_metrics
    
    # Algoritmos mejorados
    prefer_enhanced = Confirm.ask(
        f"¿Preferir algoritmos mejorados? (actual: {'SÍ' if prefs.prefer_enhanced_algorithms else 'NO'})",
        default=prefs.prefer_enhanced_algorithms
    )
    prefs.prefer_enhanced_algorithms = prefer_enhanced
    
    # Cross-fade
    enable_fade = Confirm.ask(
        f"¿Activar cross-fade en división? (actual: {'SÍ' if prefs.enable_cross_fade else 'NO'})",
        default=prefs.enable_cross_fade
    )
    prefs.enable_cross_fade = enable_fade
    
    # Dithering
    enable_dither = Confirm.ask(
        f"¿Activar dithering? (actual: {'SÍ' if prefs.enable_dithering else 'NO'})",
        default=prefs.enable_dithering
    )
    prefs.enable_dithering = enable_dither
    
    # Guardar cambios
    if settings.save_preferences():
        console.print("[green]✓ Preferencias guardadas exitosamente[/green]")
    else:
        console.print("[red]❌ Error guardando preferencias[/red]")

def configure_custom_thresholds(settings):
    """Configurar umbrales personalizados"""
    console.print("\n[cyan]🔧 Umbrales Personalizados:[/cyan]")
    console.print("[yellow]Deja en blanco para mantener valor actual[/yellow]")
    
    current_thresholds = settings.get_quality_thresholds()
    
    # THD+N
    thd_input = Prompt.ask(
        f"THD+N threshold en dB (actual: {current_thresholds['thd_threshold']:.1f})",
        default=""
    )
    thd_value = float(thd_input) if thd_input else None
    
    # SNR
    snr_input = Prompt.ask(
        f"SNR threshold en dB (actual: {current_thresholds['snr_threshold']:.1f})",
        default=""
    )
    snr_value = float(snr_input) if snr_input else None
    
    # Rango dinámico
    dr_input = Prompt.ask(
        f"Rango dinámico mínimo en % (actual: {current_thresholds['dynamic_range_min']:.1f})",
        default=""
    )
    dr_value = float(dr_input) if dr_input else None
    
    # Aplicar cambios
    if any([thd_value, snr_value, dr_value]):
        success = settings.set_custom_thresholds(thd_value, snr_value, dr_value)
        if success:
            console.print("[green]✓ Umbrales personalizados establecidos (perfil CUSTOM activado)[/green]")
        else:
            console.print("[red]❌ Error estableciendo umbrales[/red]")
    else:
        console.print("[yellow]No se realizaron cambios[/yellow]")

def run_audio_converter():
    """Ejecuta el módulo de conversión de audio con opciones de calidad"""
    try:
        settings = get_quality_settings()
        
        console.print(Panel(
            "[bold blue]🔄 Audio Converter Enhanced[/bold blue]\n" +
            "[dim]Conversión entre formatos con validación de calidad científica[/dim]",
            title="Audio Converter"
        ))
        
        # Mostrar estado de calidad actual
        profile = settings.preferences.default_profile
        profile_emoji = {"studio": "🏆", "professional": "✅", "standard": "⚡", "basic": "📱", "custom": "🔧"}
        quality_emoji = profile_emoji.get(profile.value, "❓")
        console.print(f"[dim]Calidad actual: {quality_emoji} {profile.value.upper()}[/dim]")
        
        # Preguntar si usar validación de calidad
        use_enhanced = settings.preferences.prefer_enhanced_algorithms
        if not use_enhanced:
            use_enhanced = Confirm.ask("\n🔬 ¿Usar convertidor mejorado con validación de calidad?", default=False)
        else:
            console.print(f"\n[cyan]🔬 Usando convertidor mejorado (configuración por defecto)[/cyan]")
        
        # Pedir archivo de entrada
        input_file = Prompt.ask("\n🎧 Archivo de audio de entrada")
        
        if not Path(input_file).exists():
            console.print("[red]❌ Archivo no encontrado[/red]")
            return
        
        # Pedir archivo de salida
        output_file = Prompt.ask("📁 Archivo de salida")
        
        # Formato de salida
        target_format = Prompt.ask(
            "🎵 Formato de salida", 
            choices=["wav", "mp3", "flac"],
            default="flac"
        )
        
        # Calidad de conversión
        quality = Prompt.ask(
            "⚡ Calidad de conversión",
            choices=["low", "medium", "high", "highest"],
            default="high"
        )
        
        # Opciones de calidad si se usa el convertidor mejorado
        show_metrics = settings.preferences.show_metrics_by_default
        if use_enhanced and not show_metrics:
            show_metrics = Confirm.ask("📊 ¿Mostrar métricas detalladas de calidad?", default=False)
        
        # Realizar conversión
        console.print(f"\n[cyan]Iniciando conversión {target_format.upper()}...[/cyan]")
        
        if use_enhanced:
            # Usar convertidor mejorado
            converter = EnhancedAudioConverter()
            result = converter.convert_with_quality_validation(
                input_file, output_file, target_format, quality, True
            )
            
            if result['status'] == 'success':
                console.print("[green]✓ Conversión exitosa con validación de calidad[/green]")
                
                # Mostrar métricas si se solicitó
                if show_metrics and 'quality_metrics' in result:
                    display_quality_metrics(
                        result['quality_metrics'], 
                        f"📊 Métricas de Calidad - {Path(output_file).name}"
                    )
                else:
                    # Mostrar resumen básico
                    if 'quality_metrics' in result:
                        metrics = result['quality_metrics']
                        if metrics.quality_level:
                            level_emoji = {"excellent": "🏆", "good": "✅", "acceptable": "⚠️", "poor": "❌", "failed": "💥"}
                            emoji = level_emoji.get(metrics.quality_level.value, "❓")
                            console.print(f"[dim]Calidad del resultado: {emoji} {metrics.quality_level.value.upper()}[/dim]")
            else:
                console.print("[red]❌ Error en conversión mejorada[/red]")
                if 'error' in result:
                    console.print(f"[red]{result['error']}[/red]")
        else:
            # Usar convertidor estándar
            from ..core.converter import AudioConverter
            converter = AudioConverter()
            success = converter.convert_file(input_file, output_file, target_format, quality, True)
            
            if success:
                console.print("[green]✓ Conversión exitosa[/green]")
            else:
                console.print("[red]❌ Error en conversión estándar[/red]")
        
        # Preguntar si hacer otra conversión
        if Confirm.ask("\n🔄 ¿Realizar otra conversión?", default=False):
            run_audio_converter()
            
    except ImportError as e:
        console.print(f"[red]❌ Error importando Audio Converter: {e}[/red]")
    except Exception as e:
        console.print(f"[red]❌ Error ejecutando Audio Converter: {e}[/red]")

def run_audio_splitter():
    """Ejecuta el módulo de división de audio con opciones DSP mejoradas"""
    try:
        settings = get_quality_settings()
        
        console.print(Panel(
            "[bold blue]✂️ Audio Splitter Enhanced[/bold blue]\n" +
            "[dim]División de audio con cross-fade y optimizaciones DSP[/dim]",
            title="Audio Splitter"
        ))
        
        # Mostrar estado de calidad actual
        profile = settings.preferences.default_profile
        profile_emoji = {"studio": "🏆", "professional": "✅", "standard": "⚡", "basic": "📱", "custom": "🔧"}
        quality_emoji = profile_emoji.get(profile.value, "❓")
        console.print(f"[dim]Calidad actual: {quality_emoji} {profile.value.upper()}[/dim]")
        
        # Preguntar si usar divisor mejorado
        use_enhanced = settings.preferences.prefer_enhanced_algorithms
        if not use_enhanced:
            use_enhanced = Confirm.ask("\n🔬 ¿Usar divisor mejorado con optimizaciones DSP?", default=False)
        else:
            console.print(f"\n[cyan]🔬 Usando divisor mejorado (configuración por defecto)[/cyan]")
        
        # Pedir archivo de entrada
        input_file = Prompt.ask("\n🎧 Archivo de audio de entrada")
        
        if not Path(input_file).exists():
            console.print("[red]❌ Archivo no encontrado[/red]")
            return
        
        # Directorio de salida
        output_dir = Prompt.ask("📁 Directorio de salida", default="data/output")
        
        # Configurar segmentos
        console.print("\n[cyan]🎯 Configuración de Segmentos:[/cyan]")
        console.print("[dim]Formato: inicio-fin:nombre (ej: 0:30-1:30:intro)[/dim]")
        
        segments = []
        while True:
            segment_input = Prompt.ask(f"Segmento {len(segments)+1} (o 'fin' para terminar)")
            
            if segment_input.lower() in ['fin', 'done', 'finish', '']:
                break
            
            try:
                # Parsear formato "inicio-fin:nombre"
                if ':' in segment_input:
                    time_range, name = segment_input.rsplit(':', 1)
                else:
                    time_range = segment_input
                    name = f"segment_{len(segments)+1}"
                
                start_str, end_str = time_range.split('-')
                
                # Convertir a milisegundos (función simple)
                def convert_to_ms(time_str):
                    """Convertir tiempo en formato mm:ss o ss a milisegundos"""
                    if ':' in time_str:
                        parts = time_str.split(':')
                        if len(parts) == 2:  # mm:ss
                            minutes, seconds = parts
                            return int(minutes) * 60000 + int(seconds) * 1000
                        elif len(parts) == 3:  # hh:mm:ss
                            hours, minutes, seconds = parts
                            return int(hours) * 3600000 + int(minutes) * 60000 + int(seconds) * 1000
                    else:
                        return int(time_str) * 1000  # Solo segundos
                
                start_ms = convert_to_ms(start_str.strip())
                end_ms = convert_to_ms(end_str.strip())
                segments.append((start_ms, end_ms, name.strip()))
                
                console.print(f"[green]✓ Segmento agregado: {name} ({start_str}-{end_str})[/green]")
                
            except Exception as e:
                console.print(f"[red]❌ Error procesando segmento: {e}[/red]")
                console.print("[yellow]Usa formato: inicio-fin:nombre (ej: 0:30-1:30:intro)[/yellow]")
        
        if not segments:
            console.print("[red]❌ No se configuraron segmentos[/red]")
            return
        
        # Opciones de calidad DSP si se usa el divisor mejorado
        if use_enhanced:
            console.print("\n[cyan]🔧 Opciones DSP:[/cyan]")
            
            fade_enabled = settings.preferences.enable_cross_fade
            if not fade_enabled:
                fade_enabled = Confirm.ask("🎵 ¿Activar cross-fade (transiciones suaves)?", default=True)
            
            dither_enabled = settings.preferences.enable_dithering
            if not dither_enabled:
                dither_enabled = Confirm.ask("🔊 ¿Activar dithering (reducir ruido de cuantización)?", default=True)
            
            quality_validation = settings.preferences.enable_quality_validation
            if not quality_validation:
                quality_validation = Confirm.ask("📊 ¿Validar calidad de cada segmento?", default=False)
            
            show_metrics = settings.preferences.show_metrics_by_default
            if quality_validation and not show_metrics:
                show_metrics = Confirm.ask("📈 ¿Mostrar métricas detalladas por segmento?", default=False)
            
            console.print(f"\n[dim]Cross-fade: {'✓' if fade_enabled else '✗'} | "
                        f"Dithering: {'✓' if dither_enabled else '✗'} | "
                        f"Validación: {'✓' if quality_validation else '✗'}[/dim]")
        
        # Realizar división
        console.print(f"\n[cyan]Iniciando división de audio en {len(segments)} segmentos...[/cyan]")
        
        if use_enhanced:
            # Usar divisor mejorado
            splitter = EnhancedAudioSplitter()
            result = splitter.split_audio_enhanced(
                input_file=input_file,
                segments=segments,
                output_dir=output_dir,
                fade_enabled=fade_enabled,
                dither_enabled=dither_enabled,
                quality_validation=quality_validation
            )
            
            if result['status'] == 'success':
                console.print(f"[green]✓ División mejorada completada en '{output_dir}'[/green]")
                
                # Mostrar estadísticas de rendimiento
                if 'performance_stats' in result:
                    stats = result['performance_stats']
                    console.print(f"[dim]Procesados: {stats.get('total_segments', len(segments))} segmentos | "
                               f"Tiempo: {stats.get('total_time_ms', 0):.0f}ms | "
                               f"Memoria: {stats.get('peak_memory_mb', 0):.1f}MB[/dim]")
                
                # Mostrar métricas de calidad si se solicitó
                if show_metrics and 'segment_quality_metrics' in result:
                    console.print("\n[bold cyan]📊 Métricas de Calidad por Segmento:[/bold cyan]")
                    
                    for i, metrics in enumerate(result['segment_quality_metrics']):
                        segment_name = segments[i][2] if segments[i][2] else f"segmento_{i+1}"
                        console.print(f"\n[bold white]{segment_name}:[/bold white]")
                        
                        if hasattr(metrics, 'quality_level') and metrics.quality_level:
                            level_emoji = {"excellent": "🏆", "good": "✅", "acceptable": "⚠️", "poor": "❌", "failed": "💥"}
                            emoji = level_emoji.get(metrics.quality_level.value, "❓")
                            console.print(f"[dim]  Calidad: {emoji} {metrics.quality_level.value.upper()}[/dim]")
                        
                        if hasattr(metrics, 'thd_plus_n_db') and hasattr(metrics, 'snr_db') and metrics.thd_plus_n_db and metrics.snr_db:
                            console.print(f"[dim]  THD+N: {metrics.thd_plus_n_db:.1f}dB | SNR: {metrics.snr_db:.1f}dB[/dim]")
            else:
                console.print("[red]❌ Error en división mejorada[/red]")
                if 'error' in result:
                    console.print(f"[red]{result['error']}[/red]")
        else:
            # Usar divisor estándar
            from ..core.splitter import split_audio
            success = split_audio(input_file, segments, output_dir)
            
            if success:
                console.print(f"[green]✓ División completada en '{output_dir}'[/green]")
            else:
                console.print("[red]❌ Error en división estándar[/red]")
        
        # Preguntar si hacer otra división
        if Confirm.ask("\n🔄 ¿Realizar otra división?", default=False):
            run_audio_splitter()
            
    except ImportError as e:
        console.print(f"[red]❌ Error importando Audio Splitter: {e}[/red]")
    except Exception as e:
        console.print(f"[red]❌ Error ejecutando Audio Splitter: {e}[/red]")

def run_metadata_editor():
    """Ejecuta el editor de metadatos"""
    try:
        from ..core.metadata_manager import interactive_mode
        console.print("\n[blue]🏷️ Iniciando Metadata Editor...[/blue]")
        interactive_mode()
    except ImportError as e:
        console.print(f"[red]❌ Error importando Metadata Editor: {e}[/red]")
    except Exception as e:
        console.print(f"[red]❌ Error ejecutando Metadata Editor: {e}[/red]")

def run_spectrogram_generator():
    """Ejecuta el generador de espectrogramas mejorado para LLMs"""
    try:
        settings = get_quality_settings()
        
        console.print(Panel(
            "[bold blue]📊 Spectrogram Generator Enhanced[/bold blue]\n" +
            "[dim]Generación de espectrogramas con puertas de calidad científica[/dim]",
            title="Spectrogram Generator"
        ))
        
        # Mostrar estado de calidad actual
        profile = settings.preferences.default_profile
        profile_emoji = {"studio": "🏆", "professional": "✅", "standard": "⚡", "basic": "📱", "custom": "🔧"}
        quality_emoji = profile_emoji.get(profile.value, "❓")
        console.print(f"[dim]Calidad actual: {quality_emoji} {profile.value.upper()}[/dim]")
        
        # Preguntar si usar generador mejorado
        use_enhanced = settings.preferences.prefer_enhanced_algorithms
        if not use_enhanced:
            use_enhanced = Confirm.ask("\n🔬 ¿Usar generador mejorado con puertas de calidad?", default=False)
        else:
            console.print(f"\n[cyan]🔬 Usando generador mejorado (configuración por defecto)[/cyan]")
        
        # Pedir archivo de entrada
        input_file = Prompt.ask("\n🎧 Archivo de audio de entrada")
        
        if not Path(input_file).exists():
            console.print("[red]❌ Archivo no encontrado[/red]")
            return
        
        # Tipo de espectrograma
        spectrogram_type = Prompt.ask(
            "\n📈 Tipo de espectrograma",
            choices=["mel", "linear", "cqt", "dual"],
            default="mel"
        )
        
        # Archivo de salida
        default_output = str(Path(input_file).with_suffix('.png'))
        output_file = Prompt.ask(
            "\n🖼️ Archivo de salida",
            default=default_output
        )
        
        # Opciones avanzadas para generador mejorado
        if use_enhanced:
            console.print("\n[cyan]🔧 Opciones de Calidad:[/cyan]")
            
            quality_gates = Confirm.ask("🚪 ¿Activar puertas de calidad (resolución temporal/frecuencial)?", default=True)
            llm_optimized = Confirm.ask("🤖 ¿Optimización específica para LLMs?", default=True)
            
            show_metrics = settings.preferences.show_metrics_by_default
            if not show_metrics:
                show_metrics = Confirm.ask("📊 ¿Mostrar métricas de calidad del espectrograma?", default=False)
            
            console.print(f"\n[dim]Puertas de calidad: {'✓' if quality_gates else '✗'} | "
                        f"LLM optimizado: {'✓' if llm_optimized else '✗'} | "
                        f"Métricas: {'✓' if show_metrics else '✗'}[/dim]")
        
        # Parámetros personalizados
        if spectrogram_type in ["mel", "cqt"]:
            mel_bins = int(Prompt.ask("🎵 Número de bins Mel/CQT", default="128"))
            fmin = float(Prompt.ask("📉 Frecuencia mínima (Hz)", default="20"))
            fmax = float(Prompt.ask("📈 Frecuencia máxima (Hz)", default="8000"))
            
            custom_params = {
                'n_mels': mel_bins if spectrogram_type == "mel" else None,
                'n_bins': mel_bins if spectrogram_type == "cqt" else None,
                'fmin': fmin,
                'fmax': fmax
            }
            if spectrogram_type == "cqt":
                custom_params['bins_per_octave'] = 12
        else:
            custom_params = {}
        
        # Generar espectrograma
        console.print(f"\n[cyan]Generando espectrograma {spectrogram_type.upper()}...[/cyan]")
        
        if use_enhanced:
            # Usar generador mejorado
            generator = EnhancedSpectrogramGenerator(
                progress_callback=lambda current, total, msg: 
                console.print(f"[cyan]Progreso: {current}/{total} - {msg}[/cyan]")
            )
            
            # Configurar opciones de calidad
            generator.quality_gates_enabled = quality_gates
            generator.llm_optimized = llm_optimized
            
        else:
            # Usar generador estándar
            from ..core.spectrogram_generator import SpectrogramGenerator
            generator = SpectrogramGenerator(
                progress_callback=lambda current, total, msg: 
                console.print(f"[cyan]Progreso: {current}/{total} - {msg}[/cyan]")
            )
        
        # Generar según el tipo
        if spectrogram_type == "mel":
            if use_enhanced:
                result = generator.generate_mel_spectrogram_enhanced(input_file, output_file, custom_params)
            else:
                result = generator.generate_mel_spectrogram(input_file, output_file, custom_params)
        elif spectrogram_type == "linear":
            if use_enhanced:
                result = generator.generate_linear_spectrogram_enhanced(input_file, output_file, custom_params)
            else:
                result = generator.generate_linear_spectrogram(input_file, output_file, custom_params)
        elif spectrogram_type == "cqt":
            if use_enhanced:
                result = generator.generate_cqt_spectrogram_enhanced(input_file, output_file, custom_params)
            else:
                result = generator.generate_cqt_spectrogram(input_file, output_file, custom_params)
        elif spectrogram_type == "dual":
            # Para dual, necesitamos un directorio
            output_dir = Path(output_file).parent
            input_path = Path(input_file)
            
            mel_output = output_dir / f"{input_path.stem}_mel_spectrogram.png"
            linear_output = output_dir / f"{input_path.stem}_linear_spectrogram.png"
            
            console.print("[cyan]Generando espectrograma Mel...[/cyan]")
            if use_enhanced:
                mel_result = generator.generate_mel_spectrogram_enhanced(input_file, mel_output, custom_params)
            else:
                mel_result = generator.generate_mel_spectrogram(input_file, mel_output, custom_params)
            
            console.print("[cyan]Generando espectrograma Linear...[/cyan]")
            if use_enhanced:
                linear_result = generator.generate_linear_spectrogram_enhanced(input_file, linear_output, {})
            else:
                linear_result = generator.generate_linear_spectrogram(input_file, linear_output, {})
            
            result = {
                'status': 'success' if mel_result.get('status') == 'success' and linear_result.get('status') == 'success' else 'error',
                'spectrogram_type': 'dual',
                'mel_result': mel_result,
                'linear_result': linear_result
            }
        
        # Mostrar resultados
        if result.get('status') == 'success':
            console.print(f"[green]✓ Espectrograma {spectrogram_type.upper()} generado exitosamente[/green]")
            
            # Mostrar métricas de calidad científica si se usó el generador mejorado
            if use_enhanced and show_metrics and 'quality_metrics' in result:
                display_quality_metrics(
                    result['quality_metrics'], 
                    f"📊 Métricas de Calidad del Espectrograma - {spectrogram_type.upper()}"
                )
            
            # Mostrar métricas básicas
            if 'quality_metrics' in result:
                metrics = result['quality_metrics']
                
                if use_enhanced and hasattr(metrics, 'quality_level'):
                    level_emoji = {"excellent": "🏆", "good": "✅", "acceptable": "⚠️", "poor": "❌", "failed": "💥"}
                    emoji = level_emoji.get(metrics.quality_level.value, "❓")
                    console.print(f"[dim]Calidad científica: {emoji} {metrics.quality_level.value.upper()}[/dim]")
                
                # Mostrar resolución y características
                if hasattr(metrics, 'temporal_resolution_ms') and hasattr(metrics, 'frequency_resolution_hz'):
                    console.print(f"[dim]Resolución: {metrics.temporal_resolution_ms:.1f}ms temporal, {metrics.frequency_resolution_hz:.1f}Hz frecuencial[/dim]")
                elif 'temporal_resolution_ms' in metrics and 'frequency_resolution_hz' in metrics:
                    console.print(f"[dim]Resolución: {metrics['temporal_resolution_ms']:.1f}ms temporal, {metrics['frequency_resolution_hz']:.1f}Hz frecuencial[/dim]")
                
                # Información adicional
                duration = result.get('duration_seconds', metrics.get('duration_seconds'))
                sample_rate = result.get('sample_rate', metrics.get('sample_rate'))
                if duration and sample_rate:
                    console.print(f"[dim]Audio: {duration:.2f}s, {sample_rate}Hz[/dim]")
            
            # Información para uso con LLMs
            console.print("\n[bold yellow]🤖 Información para LLM Context:[/bold yellow]")
            console.print(f"[dim]• Tipo: {spectrogram_type.upper()} - Optimizado para análisis visual[/dim]")
            console.print(f"[dim]• Archivo generado: {output_file}[/dim]")
            if use_enhanced:
                console.print(f"[dim]• Calidad científica validada con puertas de calidad[/dim]")
            console.print(f"[dim]• Resolución: 1024x512 pixels (óptimo para vision models)[/dim]")
            console.print(f"[dim]• Colormap: viridis (perceptualmente uniforme)[/dim]")
            
        else:
            console.print(f"[red]❌ Error generando espectrograma {spectrogram_type.upper()}[/red]")
            if 'error' in result:
                console.print(f"[red]{result['error']}[/red]")
        
        # Preguntar si generar otro espectrograma
        if Confirm.ask("\n🔄 ¿Generar otro espectrograma?", default=False):
            run_spectrogram_generator()
    
    except ImportError as e:
        console.print(f"[red]❌ Error importando Spectrogram Generator: {e}[/red]")
    except Exception as e:
        console.print(f"[red]❌ Error ejecutando Spectrogram Generator: {e}[/red]")

def run_artwork_manager():
    """Ejecuta el gestor de carátulas"""
    console.print("\n[yellow]🖼️ Artwork Manager integrado en Metadata Editor[/yellow]")
    console.print("[dim]Usa el Metadata Editor para gestionar carátulas[/dim]")
    run_metadata_editor()

def show_documentation():
    """Muestra documentación y ayuda"""
    console.print("\n[cyan]📄 Documentación Audio Splitter Suite 2.0[/cyan]")
    
    docs = {
        "🔄 Audio Converter": [
            "• Convierte entre formatos WAV, MP3, FLAC",
            "• Preserva metadatos automáticamente", 
            "• Configuración de calidad personalizable",
            "• Conversión por lotes con progreso visual"
        ],
        "✂️ Audio Splitter": [
            "• División precisa con milisegundos",
            "• Soporte múltiples formatos de entrada",
            "• Preservación de metadatos en segmentos",
            "• Modo interactivo y línea de comandos"
        ],
        "🏷️ Metadata Editor": [
            "• Editor profesional ID3v2.4, Vorbis, iTunes",
            "• Plantillas de metadatos guardables",
            "• Edición por lotes",
            "• Gestión completa de carátulas"
        ],
        "📊 Spectrogram Generator": [
            "• Espectrogramas optimizados para análisis con LLMs",
            "• Múltiples tipos: Mel-scale, Linear, Constant-Q",
            "• Resolución 1024x512 (ideal para vision models)",
            "• Parámetros científicos ajustables"
        ],
        "🖼️ Artwork Manager": [
            "• Embedding en MP3, FLAC, M4A",
            "• Redimensionado automático",
            "• Extracción de carátulas existentes",
            "• Soporte JPEG, PNG"
        ]
    }
    
    for module, features in docs.items():
        console.print(f"\n[bold]{module}[/bold]")
        for feature in features:
            console.print(f"  {feature}")
    
    console.print(f"\n[cyan]📁 Archivos de documentación:[/cyan]")
    console.print("  • docs/README.md - Guía de uso")
    console.print("  • docs/architecture.md - Documentación técnica")
    console.print("  • docs/product_requirements.md - Especificaciones")
    console.print("  • docs/implementation.md - Detalles de implementación")
    
    console.print(f"\n[cyan]🛠️ Línea de comandos:[/cyan]")
    console.print("  • python -m audio_splitter.ui.cli split <archivo> --segments '1:30-2:45:intro'")
    console.print("  • python -m audio_splitter.ui.cli convert <archivo> -f mp3 -q high")
    console.print("  • python -m audio_splitter.ui.cli metadata <archivo> --title 'Mi Canción'")

if __name__ == "__main__":
    interactive_menu()
