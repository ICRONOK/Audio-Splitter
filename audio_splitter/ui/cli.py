"""
Interfaz de línea de comandos principal del Audio Splitter Suite
"""

import argparse
import sys
from pathlib import Path
import numpy as np

# Imports relativos limpios
from ..core.splitter import split_audio, convert_to_ms
from ..core.converter import AudioConverter
from ..core.metadata_manager import MetadataEditor, AudioMetadata
from ..core.spectrogram_generator import SpectrogramGenerator
from ..core.enhanced_converter import EnhancedAudioConverter
from ..core.enhanced_splitter import EnhancedAudioSplitter
from ..core.enhanced_spectrogram import EnhancedSpectrogramGenerator
from ..core.quality_framework import QualityLevel
from ..config.quality_settings import (
    get_quality_settings, 
    QualityProfile, 
    apply_user_preferences_to_args
)
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

def display_quality_metrics(metrics, title="📊 Métricas de Calidad"):
    """Mostrar métricas de calidad en formato de tabla"""
    
    table = Table(title=title, show_header=True, header_style="bold cyan")
    table.add_column("Métrica", style="white", width=25)
    table.add_column("Valor", style="green", width=15)
    table.add_column("Estado", style="bold", width=15)
    table.add_column("Estándar", style="dim", width=20)
    
    # THD+N
    if metrics.thd_plus_n_db is not None:
        thd_status = "🏆 EXCELENTE" if metrics.thd_plus_n_db < -80 else \
                    "✅ BUENO" if metrics.thd_plus_n_db < -60 else \
                    "⚠️ ACEPTABLE" if metrics.thd_plus_n_db < -40 else "❌ POBRE"
        table.add_row("THD+N", f"{metrics.thd_plus_n_db:.1f} dB", thd_status, "Studio: <-80dB")
    
    # SNR
    if metrics.snr_db is not None:
        snr_status = "🏆 EXCELENTE" if metrics.snr_db > 100 else \
                    "✅ BUENO" if metrics.snr_db > 90 else \
                    "⚠️ ACEPTABLE" if metrics.snr_db > 70 else "❌ POBRE"
        table.add_row("SNR", f"{metrics.snr_db:.1f} dB", snr_status, "Professional: >90dB")
    
    # Rango dinámico
    if metrics.dynamic_range_db is not None:
        dr_status = "✅ EXCELENTE" if metrics.dynamic_range_db > 60 else \
                   "⚠️ ACEPTABLE" if metrics.dynamic_range_db > 40 else "❌ POBRE"
        table.add_row("Rango Dinámico", f"{metrics.dynamic_range_db:.1f} dB", dr_status, ">60dB recomendado")
    
    # Nivel de pico
    if metrics.peak_level_db is not None:
        peak_status = "✅ ÓPTIMO" if -6 <= metrics.peak_level_db <= -1 else \
                     "⚠️ ALTO" if metrics.peak_level_db > -1 else "⚠️ BAJO"
        table.add_row("Nivel de Pico", f"{metrics.peak_level_db:.1f} dB", peak_status, "-6dB a -1dB")
    
    # Artefactos
    artifacts_detected = getattr(metrics, 'artifacts_detected', False)
    artifact_status = "❌ DETECTADOS" if artifacts_detected else "✅ NINGUNO"
    table.add_row("Artefactos", "Sí" if artifacts_detected else "No", artifact_status, "Ninguno ideal")
    
    # Nivel de calidad general
    if metrics.quality_level is not None:
        level_emoji = {"excellent": "🏆", "good": "✅", "acceptable": "⚠️", "poor": "❌", "failed": "💥"}
        quality_emoji = level_emoji.get(metrics.quality_level.value, "❓")
        table.add_row("Calidad General", metrics.quality_level.value.upper(), f"{quality_emoji} {metrics.quality_level.value.upper()}", "Professional+")
    
    # Rendimiento
    if metrics.processing_time_ms is not None:
        perf_status = "🚀 RÁPIDO" if metrics.processing_time_ms < 1000 else \
                     "✅ NORMAL" if metrics.processing_time_ms < 5000 else "⚠️ LENTO"
        table.add_row("Tiempo de Procesamiento", f"{metrics.processing_time_ms:.0f} ms", perf_status, "<2x tiempo real")
    
    if metrics.memory_usage_mb is not None:
        mem_status = "🔥 EFICIENTE" if metrics.memory_usage_mb < 100 else \
                    "✅ NORMAL" if metrics.memory_usage_mb < 500 else "⚠️ ALTO"
        table.add_row("Uso de Memoria", f"{metrics.memory_usage_mb:.1f} MB", mem_status, "<4x tamaño entrada")
    
    console.print(table)
    
    # Panel resumen
    if metrics.quality_level is not None:
        level_colors = {"excellent": "bright_green", "good": "green", "acceptable": "yellow", "poor": "red", "failed": "bright_red"}
        panel_color = level_colors.get(metrics.quality_level.value, "white")
        
        summary_text = f"[bold {panel_color}]Calidad: {metrics.quality_level.value.upper()}[/bold {panel_color}]\n"
        if metrics.quality_score is not None:
            summary_text += f"Puntuación: {metrics.quality_score:.1f}/100"
        
        console.print(Panel(summary_text, title="🎯 Resumen de Calidad", border_style=panel_color))

def create_parser():
    """Crea el parser principal de argumentos"""
    parser = argparse.ArgumentParser(
        description='Audio Splitter Suite - Sistema completo de procesamiento de audio',
        prog='audio-splitter'
    )
    
    parser.add_argument('--version', '-v', action='version', version='Audio Splitter Suite 2.0.0')
    
    # Subcomandos
    subparsers = parser.add_subparsers(dest='command', help='Comandos disponibles')
    
    # Comando split
    split_parser = subparsers.add_parser('split', help='Dividir archivos de audio')
    split_parser.add_argument('input_file', help='Archivo de audio de entrada')
    split_parser.add_argument('--output-dir', '-o', default='data/output', help='Directorio de salida')
    split_parser.add_argument('--segments', '-s', nargs='+', 
                             help='Segmentos en formato "inicio-fin:nombre"')
    split_parser.add_argument('--enhanced', action='store_true',
                             help='Usar divisor mejorado con cross-fade y optimizaciones DSP')
    split_parser.add_argument('--fade-enabled', action='store_true', default=True,
                             help='Activar transiciones cross-fade (Hann window)')
    split_parser.add_argument('--dither-enabled', action='store_true', default=True,
                             help='Activar dithering triangular para reducir ruido de cuantización')
    split_parser.add_argument('--quality-validation', action='store_true',
                             help='Validar calidad de cada segmento')
    split_parser.add_argument('--show-metrics', action='store_true', 
                             help='Mostrar métricas detalladas de calidad por segmento')
    
    # Comando convert
    convert_parser = subparsers.add_parser('convert', help='Convertir formatos de audio')
    convert_parser.add_argument('input', help='Archivo o directorio de entrada')
    convert_parser.add_argument('--output', '-o', required=True, help='Archivo o directorio de salida')
    convert_parser.add_argument('--format', '-f', required=True, choices=['wav', 'mp3', 'flac'], 
                               help='Formato de salida')
    convert_parser.add_argument('--quality', '-q', default='high', 
                               help='Calidad de conversión')
    convert_parser.add_argument('--batch', action='store_true', 
                               help='Conversión por lotes')
    convert_parser.add_argument('--recursive', '-r', action='store_true',
                               help='Buscar recursivamente')
    convert_parser.add_argument('--quality-validation', action='store_true',
                               help='Activar validación de calidad científica (THD+N, SNR)')
    convert_parser.add_argument('--quality-level', choices=['basic', 'professional', 'studio'],
                               default='professional', help='Nivel de validación de calidad')
    convert_parser.add_argument('--show-metrics', action='store_true', 
                               help='Mostrar métricas detalladas de calidad')
    
    # Comando channel - Nuevo comando para conversión de canales
    channel_parser = subparsers.add_parser('channel', help='Convertir canales de audio (mono ↔ stereo)')
    channel_parser.add_argument('input', help='Archivo o directorio de entrada')
    channel_parser.add_argument('--output', '-o', help='Archivo o directorio de salida')
    channel_parser.add_argument('--channels', '-c', type=int, choices=[1, 2],
                               help='Número de canales objetivo (1=mono, 2=stereo)')
    channel_parser.add_argument('--algorithm', '-a', default='downmix_center',
                               choices=['downmix_center', 'left_only', 'right_only', 'average'],
                               help='Algoritmo de mezcla para stereo→mono (default: downmix_center)')
    channel_parser.add_argument('--batch', action='store_true',
                               help='Conversión por lotes')
    channel_parser.add_argument('--recursive', '-r', action='store_true',
                               help='Buscar recursivamente en subdirectorios')
    channel_parser.add_argument('--preserve-metadata', action='store_true', default=True,
                               help='Preservar metadatos originales (default: True)')
    channel_parser.add_argument('--analyze', action='store_true',
                               help='Solo analizar propiedades de canal sin convertir')
    
    # Comando metadata
    metadata_parser = subparsers.add_parser('metadata', help='Editar metadatos')
    metadata_parser.add_argument('file_path', help='Archivo de audio')
    metadata_parser.add_argument('--title', help='Título')
    metadata_parser.add_argument('--artist', help='Artista')
    metadata_parser.add_argument('--album', help='Álbum')
    metadata_parser.add_argument('--genre', help='Género')
    metadata_parser.add_argument('--year', help='Año')
    
    # Comando spectrogram
    spectrogram_parser = subparsers.add_parser('spectrogram', help='Generar espectrogramas para LLMs')
    spectrogram_parser.add_argument('input_file', help='Archivo de audio de entrada')
    spectrogram_parser.add_argument('--output', '-o', help='Archivo de imagen de salida')
    spectrogram_parser.add_argument('--type', '-t', choices=['mel', 'linear', 'cqt', 'dual'], 
                                   default='mel', help='Tipo de espectrograma')
    spectrogram_parser.add_argument('--output-dir', help='Directorio de salida para múltiples tipos')
    spectrogram_parser.add_argument('--mel-bins', type=int, default=128, 
                                   help='Número de bins Mel (default: 128)')
    spectrogram_parser.add_argument('--fmin', type=float, default=20.0,
                                   help='Frecuencia mínima en Hz (default: 20)')
    spectrogram_parser.add_argument('--fmax', type=float, default=8000.0,
                                   help='Frecuencia máxima en Hz (default: 8000)')
    spectrogram_parser.add_argument('--duration', type=float, 
                                   help='Duración máxima en segundos')
    spectrogram_parser.add_argument('--return-data', action='store_true',
                                   help='Devolver datos de imagen base64 (para integración)')
    spectrogram_parser.add_argument('--enhanced', action='store_true',
                                   help='Usar generador mejorado con validación de calidad científica')
    spectrogram_parser.add_argument('--quality-gates', action='store_true',
                                   help='Activar puertas de calidad (resolución temporal/frecuencial)')
    spectrogram_parser.add_argument('--llm-optimized', action='store_true', default=True,
                                   help='Optimización específica para análisis LLM')
    spectrogram_parser.add_argument('--show-quality-metrics', action='store_true', 
                                   help='Mostrar métricas de calidad del espectrograma')
    
    # Comando quality-settings - Nuevo comando para gestión de configuración de calidad
    quality_parser = subparsers.add_parser('quality-settings', help='Gestionar configuración de calidad de usuario')
    quality_subparsers = quality_parser.add_subparsers(dest='quality_action', help='Acciones de configuración')
    
    # Subcomando show
    show_parser = quality_subparsers.add_parser('show', help='Mostrar configuración actual')
    show_parser.add_argument('--detailed', action='store_true', help='Mostrar configuración detallada')
    
    # Subcomando set-profile
    profile_parser = quality_subparsers.add_parser('set-profile', help='Establecer perfil de calidad')
    profile_parser.add_argument('profile', choices=['studio', 'professional', 'standard', 'basic', 'custom'],
                               help='Perfil de calidad a usar')
    
    # Subcomando set-thresholds
    thresholds_parser = quality_subparsers.add_parser('set-thresholds', help='Establecer umbrales personalizados')
    thresholds_parser.add_argument('--thd', type=float, help='Umbral THD+N en dB (ej: -60.0)')
    thresholds_parser.add_argument('--snr', type=float, help='Umbral SNR en dB (ej: 90.0)')
    thresholds_parser.add_argument('--dynamic-range', type=float, help='Rango dinámico mínimo en % (ej: 95.0)')
    
    # Subcomando preferences
    prefs_parser = quality_subparsers.add_parser('preferences', help='Configurar preferencias generales')
    prefs_parser.add_argument('--enable-validation', action='store_true', help='Activar validación por defecto')
    prefs_parser.add_argument('--disable-validation', action='store_true', help='Desactivar validación por defecto')
    prefs_parser.add_argument('--show-metrics', action='store_true', help='Mostrar métricas por defecto')
    prefs_parser.add_argument('--hide-metrics', action='store_true', help='Ocultar métricas por defecto')
    prefs_parser.add_argument('--prefer-enhanced', action='store_true', help='Preferir algoritmos mejorados')
    prefs_parser.add_argument('--prefer-standard', action='store_true', help='Preferir algoritmos estándar')
    
    # Subcomando reset
    reset_parser = quality_subparsers.add_parser('reset', help='Restablecer configuración por defecto')
    reset_parser.add_argument('--confirm', action='store_true', help='Confirmar restablecimiento')
    
    # Subcomandos export/import
    export_parser = quality_subparsers.add_parser('export', help='Exportar configuración')
    export_parser.add_argument('file', help='Archivo de destino para exportar')
    
    import_parser = quality_subparsers.add_parser('import', help='Importar configuración')
    import_parser.add_argument('file', help='Archivo de configuración a importar')
    
    return parser

def handle_split_command(args):
    """Maneja el comando split con opciones mejoradas y validación de calidad"""
    try:
        if not args.segments:
            console.print("[red]Error: Se requieren segmentos para dividir[/red]")
            return False
        
        # Procesar segmentos
        segments = []
        for seg in args.segments:
            try:
                # Formato: "inicio-fin:nombre"
                time_range, name = seg.split(':', 1) if ':' in seg else (seg, "")
                start_str, end_str = time_range.split('-')
                
                start_ms = convert_to_ms(start_str)
                end_ms = convert_to_ms(end_str)
                segments.append((start_ms, end_ms, name))
            except Exception as e:
                console.print(f"[red]Error procesando segmento '{seg}': {e}[/red]")
                return False
        
        # Determinar si usar el divisor mejorado
        use_enhanced = args.enhanced or args.quality_validation or args.show_metrics
        
        if use_enhanced:
            # Usar divisor mejorado
            console.print("[cyan]🔬 Usando divisor mejorado con optimizaciones DSP[/cyan]")
            splitter = EnhancedAudioSplitter()
            
            # Configurar opciones de calidad
            fade_enabled = getattr(args, 'fade_enabled', True)
            dither_enabled = getattr(args, 'dither_enabled', True)
            quality_validation = getattr(args, 'quality_validation', False)
            
            console.print(f"[dim]Cross-fade: {'✓' if fade_enabled else '✗'} | "
                        f"Dithering: {'✓' if dither_enabled else '✗'} | "
                        f"Validación: {'✓' if quality_validation else '✗'}[/dim]")
            
            # Ejecutar división mejorada
            result = splitter.split_audio_enhanced(
                input_file=args.input_file,
                segments=segments,
                output_dir=args.output_dir,
                fade_enabled=fade_enabled,
                dither_enabled=dither_enabled,
                quality_validation=quality_validation
            )
            
            if result['status'] == 'success':
                console.print(f"[green]✓ División mejorada completada en '{args.output_dir}'[/green]")
                
                # Mostrar estadísticas de rendimiento
                if 'performance_stats' in result:
                    stats = result['performance_stats']
                    console.print(f"[dim]Procesados: {stats.get('total_segments', len(segments))} segmentos | "
                               f"Tiempo: {stats.get('total_time_ms', 0):.0f}ms | "
                               f"Memoria: {stats.get('peak_memory_mb', 0):.1f}MB[/dim]")
                
                # Mostrar métricas de calidad si se solicitó
                if args.show_metrics and 'segment_quality_metrics' in result:
                    console.print("\n[bold cyan]📊 Métricas de Calidad por Segmento:[/bold cyan]")
                    
                    for i, metrics in enumerate(result['segment_quality_metrics']):
                        segment_name = segments[i][2] if segments[i][2] else f"segmento_{i+1}"
                        console.print(f"\n[bold white]{segment_name}:[/bold white]")
                        
                        if metrics.quality_level:
                            level_emoji = {"excellent": "🏆", "good": "✅", "acceptable": "⚠️", "poor": "❌", "failed": "💥"}
                            emoji = level_emoji.get(metrics.quality_level.value, "❓")
                            console.print(f"[dim]  Calidad: {emoji} {metrics.quality_level.value.upper()}[/dim]")
                        
                        if metrics.thd_plus_n_db and metrics.snr_db:
                            console.print(f"[dim]  THD+N: {metrics.thd_plus_n_db:.1f}dB | SNR: {metrics.snr_db:.1f}dB[/dim]")
                        
                        if metrics.artifacts_detected:
                            console.print(f"[dim red]  ⚠️ Artefactos detectados[/dim red]")
                
                return True
            else:
                console.print("[red]✗ Error en la división mejorada[/red]")
                if 'error' in result:
                    console.print(f"[red]Detalles: {result['error']}[/red]")
                return False
        else:
            # Usar divisor estándar
            console.print("[cyan]⚡ Usando divisor estándar[/cyan]")
            success = split_audio(args.input_file, segments, args.output_dir)
            if success:
                console.print(f"[green]✓ División completada en '{args.output_dir}'[/green]")
            else:
                console.print("[red]✗ Error en la división[/red]")
            
            return success
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        return False

def handle_convert_command(args):
    """Maneja el comando convert con validación de calidad opcional"""
    try:
        # Determinar si usar el convertidor mejorado
        use_enhanced = args.quality_validation or args.show_metrics
        
        if use_enhanced:
            converter = EnhancedAudioConverter()
            console.print("[cyan]🔬 Usando convertidor mejorado con validación de calidad científica[/cyan]")
        else:
            converter = AudioConverter()
            console.print("[cyan]⚡ Usando convertidor estándar[/cyan]")
        
        if args.batch:
            # Conversión por lotes
            if use_enhanced:
                console.print("[yellow]Nota: Validación de calidad no disponible en modo lotes, usando convertidor estándar[/yellow]")
                converter = AudioConverter()
            
            successful, failed = converter.batch_convert(
                args.input, args.output, args.format, 
                args.quality, True, args.recursive
            )
            console.print(f"[green]Conversión completada: {successful} exitosos, {failed} fallidos[/green]")
            return failed == 0
        else:
            # Conversión individual
            if use_enhanced:
                # Usar convertidor mejorado con validación de calidad
                result = converter.convert_with_quality_validation(
                    args.input, args.output, args.format, args.quality, True
                )
                
                if result['success']:
                    console.print("[green]✓ Conversión exitosa con validación de calidad[/green]")
                    
                    # Mostrar métricas si se solicitó
                    if args.show_metrics and 'quality_metrics' in result:
                        display_quality_metrics(
                            result['quality_metrics'], 
                            f"📊 Métricas de Calidad - {Path(args.output).name}"
                        )
                    
                    # Mostrar resumen de calidad básico
                    if 'quality_metrics' in result:
                        metrics = result['quality_metrics']
                        if metrics.quality_level:
                            level_emoji = {"excellent": "🏆", "good": "✅", "acceptable": "⚠️", "poor": "❌", "failed": "💥"}
                            emoji = level_emoji.get(metrics.quality_level.value, "❓")
                            console.print(f"[dim]Calidad: {emoji} {metrics.quality_level.value.upper()}[/dim]")
                        
                        if metrics.thd_plus_n_db and metrics.snr_db:
                            console.print(f"[dim]THD+N: {metrics.thd_plus_n_db:.1f}dB | SNR: {metrics.snr_db:.1f}dB[/dim]")
                    
                    return True
                else:
                    console.print("[red]✗ Error en conversión con validación de calidad[/red]")
                    if 'error' in result:
                        console.print(f"[red]Detalles: {result['error']}[/red]")
                    return False
            else:
                # Usar convertidor estándar
                success = converter.convert_file(
                    args.input, args.output, args.format, args.quality, True
                )
                if success:
                    console.print("[green]✓ Conversión exitosa[/green]")
                else:
                    console.print("[red]✗ Error en conversión[/red]")
                return success
            
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        return False

def handle_metadata_command(args):
    """Maneja el comando metadata"""
    try:
        editor = MetadataEditor()
        
        # Leer metadatos existentes
        existing_metadata = editor.read_metadata(args.file_path)
        if existing_metadata is None:
            console.print("[red]Error leyendo metadatos[/red]")
            return False
        
        # Crear nueva estructura con cambios
        new_metadata = AudioMetadata()
        
        # Copiar valores existentes
        for field in ['title', 'artist', 'album', 'genre', 'date', 'track', 'comment']:
            setattr(new_metadata, field, getattr(existing_metadata, field, None))
        
        # Aplicar cambios desde argumentos
        if args.title:
            new_metadata.title = args.title
        if args.artist:
            new_metadata.artist = args.artist
        if args.album:
            new_metadata.album = args.album
        if args.genre:
            new_metadata.genre = args.genre
        if args.year:
            new_metadata.date = args.year
        
        # Guardar cambios
        success = editor.write_metadata(args.file_path, new_metadata)
        if success:
            console.print("[green]✓ Metadatos actualizados[/green]")
        else:
            console.print("[red]✗ Error actualizando metadatos[/red]")
        
        return success
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        return False

def handle_channel_command(args):
    """Maneja el comando channel - Conversión de canales con algoritmos científicos"""
    try:
        converter = AudioConverter()
        
        # Validar argumentos requeridos cuando no se usa --analyze
        if not args.analyze:
            if not args.output:
                console.print("[red]Error: --output/-o es requerido para conversión[/red]")
                return False
            if not args.channels:
                console.print("[red]Error: --channels/-c es requerido para conversión[/red]")
                return False
        
        if args.analyze:
            # Solo análisis, sin conversión
            try:
                analysis = converter.analyze_channel_properties(args.input)
                
                console.print(f"\n[bold cyan]Análisis de Canales: {Path(args.input).name}[/bold cyan]")
                console.print(f"[white]Tipo:[/white] {analysis['channel_type']}")
                console.print(f"[white]Canales:[/white] {analysis['current_channels']}")
                console.print(f"[white]Sample Rate:[/white] {analysis['sample_rate']} Hz")
                console.print(f"[white]Duración:[/white] {analysis['duration']:.2f} segundos")
                
                if analysis['channel_type'] == 'mono':
                    console.print(f"[white]Nivel RMS:[/white] {20*np.log10(analysis['rms_level'] + 1e-10):.1f} dB")
                    console.print(f"[white]Nivel Peak:[/white] {20*np.log10(analysis['peak_level'] + 1e-10):.1f} dB")
                    console.print(f"[white]Rango Dinámico:[/white] {analysis['dynamic_range']:.1f} dB")
                else:
                    if 'stereo_balance_db' in analysis:
                        console.print(f"[white]Balance L/R:[/white] {analysis['stereo_balance_db']:+.1f} dB")
                        console.print(f"[white]Correlación de Fase:[/white] {analysis['phase_correlation']:.3f}")
                        console.print(f"[white]Amplitud Stereo:[/white] {analysis['stereo_width']:.3f}")
                
                # Mostrar recomendaciones
                if analysis['recommendations']:
                    console.print("\n[yellow]Recomendaciones:[/yellow]")
                    for rec in analysis['recommendations']:
                        console.print(f"  {rec}")
                
                return True
                
            except Exception as e:
                console.print(f"[red]Error analizando archivo: {e}[/red]")
                return False
        
        if args.batch:
            # Conversión por lotes
            successful, failed = converter.batch_convert_channels(
                args.input, args.output, args.channels,
                args.algorithm, args.preserve_metadata, args.recursive
            )
            console.print(f"[green]Conversión de canales completada: {successful} exitosos, {failed} fallidos[/green]")
            return failed == 0
        else:
            # Conversión individual
            channel_name = "mono" if args.channels == 1 else "stereo"
            console.print(f"[cyan]Convirtiendo a {channel_name} usando algoritmo '{args.algorithm}'[/cyan]")
            
            success = converter.convert_channels(
                args.input, args.output, args.channels,
                args.algorithm, args.preserve_metadata
            )
            
            if success:
                console.print("[green]✓ Conversión de canales exitosa[/green]")
                
                # Mostrar información post-conversión
                try:
                    final_info = converter.get_audio_info(args.output)
                    console.print(f"[dim]Resultado: {final_info['channels']}-channel, {final_info['sample_rate']} Hz[/dim]")
                except:
                    pass
            else:
                console.print("[red]✗ Error en conversión de canales[/red]")
            
            return success
            
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        return False

def handle_spectrogram_command(args):
    """Maneja el comando spectrogram - Optimizado para LLM analysis con validación de calidad"""
    try:
        # Determinar si usar el generador mejorado
        use_enhanced = args.enhanced or args.quality_gates or args.show_quality_metrics
        
        if use_enhanced:
            console.print("[cyan]🔬 Usando generador mejorado con puertas de calidad científica[/cyan]")
            generator = EnhancedSpectrogramGenerator()
        else:
            console.print("[cyan]⚡ Usando generador estándar[/cyan]")
            generator = SpectrogramGenerator(
                progress_callback=lambda current, total, msg:
                console.print(f"[cyan]Progress: {current}/{total} - {msg}[/cyan]")
            )
        
        # Preparar parámetros personalizados
        custom_params = {}
        
        if args.type == 'mel':
            custom_params = {
                'n_mels': args.mel_bins,
                'fmin': args.fmin,
                'fmax': args.fmax
            }
        elif args.type == 'cqt':
            custom_params = {
                'fmin': args.fmin,
                'n_bins': args.mel_bins,  # Usar mel_bins como n_bins para CQT
                'bins_per_octave': 12
            }
        
        # Determinar archivo de salida
        output_file = None
        if args.output:
            output_file = args.output
        elif args.output_dir:
            from pathlib import Path
            input_path = Path(args.input_file)
            output_dir = Path(args.output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            output_file = output_dir / f"{input_path.stem}_{args.type}_spectrogram.png"
        
        console.print(f"[bold blue]Generando espectrograma {args.type} para LLM analysis...[/bold blue]")
        console.print(f"[dim]Archivo: {args.input_file}[/dim]")
        if output_file:
            console.print(f"[dim]Salida: {output_file}[/dim]")
        
        # Generar espectrograma según el tipo
        if args.type == 'mel':
            result = generator.generate_mel_spectrogram(
                args.input_file, output_file, custom_params, args.return_data
            )
        elif args.type == 'linear':
            result = generator.generate_linear_spectrogram(
                args.input_file, output_file, custom_params, args.return_data
            )
        elif args.type == 'cqt':
            result = generator.generate_cqt_spectrogram(
                args.input_file, output_file, custom_params, args.return_data
            )
        elif args.type == 'dual':
            # Generar ambos tipos
            if args.output_dir:
                from pathlib import Path
                input_path = Path(args.input_file)
                output_dir = Path(args.output_dir)
                output_dir.mkdir(parents=True, exist_ok=True)
                
                mel_output = output_dir / f"{input_path.stem}_mel_spectrogram.png"
                linear_output = output_dir / f"{input_path.stem}_linear_spectrogram.png"
                
                console.print("[cyan]Generando espectrograma Mel...[/cyan]")
                mel_result = generator.generate_mel_spectrogram(
                    args.input_file, mel_output, custom_params, args.return_data
                )
                
                console.print("[cyan]Generando espectrograma Linear...[/cyan]")
                linear_result = generator.generate_linear_spectrogram(
                    args.input_file, linear_output, {}, args.return_data
                )
                
                result = {
                    'status': 'success',
                    'spectrogram_type': 'dual',
                    'mel_result': mel_result,
                    'linear_result': linear_result
                }
            else:
                console.print("[red]Error: --output-dir es necesario para tipo 'dual'[/red]")
                return False
        else:
            console.print(f"[red]Tipo de espectrograma no reconocido: {args.type}[/red]")
            return False
        
        # Verificar éxito (compatible con ambos generadores)
        is_success = result.get('success', False) or result.get('status') == 'success'

        if is_success:
            console.print(f"[green]✓ Espectrograma {args.type} generado exitosamente[/green]")

            # NOTA: EnhancedSpectrogramGenerator ya muestra sus propias métricas
            # No llamamos a display_quality_metrics() porque está diseñada para AudioQualityMetrics
            
            # Mostrar métricas básicas LLM
            if 'quality_metrics' in result:
                metrics = result['quality_metrics']
                
                # Para generador mejorado, mostrar métricas científicas resumidas
                if use_enhanced:
                    console.print(f"[dim]Calidad científica: {getattr(metrics, 'quality_level', QualityLevel.GOOD).value.upper() if hasattr(metrics, 'quality_level') else 'N/A'}[/dim]")
                    if hasattr(metrics, 'temporal_resolution_ms') and hasattr(metrics, 'frequency_resolution_hz'):
                        console.print(f"[dim]Resolución: {metrics.temporal_resolution_ms:.1f}ms temporal, {metrics.frequency_resolution_hz:.1f}Hz frecuencial[/dim]")
                else:
                    # Para generador estándar, mostrar métricas básicas
                    console.print(f"[dim]Resolución temporal: {metrics.get('temporal_resolution_ms', 'N/A'):.1f} ms[/dim]")
                    console.print(f"[dim]Resolución frecuencial: {metrics.get('frequency_resolution_hz', 'N/A'):.1f} Hz[/dim]")
                    console.print(f"[dim]Rango dinámico: {metrics.get('dynamic_range_db', 'N/A'):.1f} dB[/dim]")
                    console.print(f"[dim]Contraste visual: {metrics.get('contrast_ratio', 'N/A'):.3f}[/dim]")
                    console.print(f"[dim]Claridad de patrones: {metrics.get('pattern_clarity_score', 'N/A'):.3f}[/dim]")
                
            # Mostrar datos base64 si se solicitó
            if args.return_data and 'image_data' in result:
                console.print(f"[dim]Datos base64 disponibles: {len(result['image_data'])} caracteres[/dim]")
                
            # Mostrar información para uso con LLMs
            console.print("\n[bold yellow]Información para LLM Context:[/bold yellow]")
            console.print(f"[dim]• Tipo: {result['spectrogram_type']} - Optimizado para análisis visual[/dim]")
            console.print(f"[dim]• Duración: {result.get('duration_seconds', 'N/A'):.2f} segundos[/dim]")
            console.print(f"[dim]• Sample rate: {result.get('sample_rate', 'N/A')} Hz[/dim]")
            console.print(f"[dim]• Resolución de imagen: 1024x512 pixels (óptimo para vision models)[/dim]")
            console.print(f"[dim]• Colormap: viridis (perceptualmente uniforme)[/dim]")
            
        else:
            console.print("[red]✗ Error generando espectrograma[/red]")
            if 'error' in result:
                console.print(f"[red]{result['error']}[/red]")

        return is_success
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        return False

def handle_quality_settings_command(args):
    """Maneja el comando quality-settings"""
    try:
        settings = get_quality_settings()
        
        if not args.quality_action:
            # Si no se especifica acción, mostrar ayuda
            console.print("[yellow]Especifica una acción: show, set-profile, set-thresholds, preferences, reset, export, import[/yellow]")
            return False
        
        if args.quality_action == 'show':
            # Mostrar configuración actual
            prefs = settings.preferences
            
            table = Table(title="🔧 Configuración de Calidad de Usuario", show_header=True, header_style="bold cyan")
            table.add_column("Configuración", style="white", width=25)
            table.add_column("Valor", style="green", width=20)
            table.add_column("Descripción", style="dim", width=30)
            
            # Perfil de calidad
            profile_emoji = {"studio": "🏆", "professional": "✅", "standard": "⚡", "basic": "📱", "custom": "🔧"}
            emoji = profile_emoji.get(prefs.default_profile.value, "❓")
            table.add_row("Perfil de Calidad", f"{emoji} {prefs.default_profile.value.upper()}", "Perfil predefinido de calidad")
            
            # Validación de calidad
            validation_status = "✅ ACTIVADA" if prefs.enable_quality_validation else "❌ DESACTIVADA"
            table.add_row("Validación de Calidad", validation_status, "Validación automática de calidad")
            
            # Mostrar métricas
            metrics_status = "✅ SÍ" if prefs.show_metrics_by_default else "❌ NO"
            table.add_row("Mostrar Métricas", metrics_status, "Mostrar métricas por defecto")
            
            # Algoritmos mejorados
            enhanced_status = "✅ SÍ" if prefs.prefer_enhanced_algorithms else "❌ NO"
            table.add_row("Algoritmos Mejorados", enhanced_status, "Preferir versiones mejoradas")
            
            # Configuraciones específicas
            fade_status = "✅ SÍ" if prefs.enable_cross_fade else "❌ NO"
            table.add_row("Cross-fade", fade_status, "Transiciones suaves en split")
            
            dither_status = "✅ SÍ" if prefs.enable_dithering else "❌ NO"
            table.add_row("Dithering", dither_status, "Reducción de ruido de cuantización")
            
            console.print(table)
            
            if args.detailed:
                # Mostrar umbrales detallados
                thresholds = settings.get_quality_thresholds()
                
                console.print("\n[bold cyan]📊 Umbrales de Calidad:[/bold cyan]")
                console.print(f"[white]THD+N:[/white] < {thresholds['thd_threshold']:.1f} dB")
                console.print(f"[white]SNR:[/white] > {thresholds['snr_threshold']:.1f} dB")
                console.print(f"[white]Rango Dinámico:[/white] > {thresholds['dynamic_range_min']:.1f}%")
                
                if prefs.default_profile == QualityProfile.CUSTOM:
                    console.print("\n[yellow]⚙️ Configuración personalizada activa[/yellow]")
            
            return True
        
        elif args.quality_action == 'set-profile':
            # Establecer perfil de calidad
            profile = QualityProfile(args.profile)
            success = settings.set_profile(profile)
            
            if success:
                profile_emoji = {"studio": "🏆", "professional": "✅", "standard": "⚡", "basic": "📱", "custom": "🔧"}
                emoji = profile_emoji.get(args.profile, "❓")
                console.print(f"[green]✓ Perfil de calidad establecido: {emoji} {args.profile.upper()}[/green]")
                
                # Mostrar información del perfil
                thresholds = settings.get_quality_thresholds()
                console.print(f"[dim]THD+N: <{thresholds['thd_threshold']:.1f}dB | SNR: >{thresholds['snr_threshold']:.1f}dB | DR: >{thresholds['dynamic_range_min']:.1f}%[/dim]")
            else:
                console.print("[red]✗ Error estableciendo perfil de calidad[/red]")
            
            return success
        
        elif args.quality_action == 'set-thresholds':
            # Establecer umbrales personalizados
            if not any([args.thd, args.snr, args.dynamic_range]):
                console.print("[yellow]Especifica al menos un umbral: --thd, --snr, o --dynamic-range[/yellow]")
                return False
            
            success = settings.set_custom_thresholds(args.thd, args.snr, args.dynamic_range)
            
            if success:
                console.print("[green]✓ Umbrales personalizados establecidos (perfil CUSTOM activado)[/green]")
                thresholds = settings.get_quality_thresholds()
                console.print(f"[dim]THD+N: <{thresholds['thd_threshold']:.1f}dB | SNR: >{thresholds['snr_threshold']:.1f}dB | DR: >{thresholds['dynamic_range_min']:.1f}%[/dim]")
            else:
                console.print("[red]✗ Error estableciendo umbrales personalizados[/red]")
            
            return success
        
        elif args.quality_action == 'preferences':
            # Configurar preferencias generales
            prefs = settings.preferences
            changed = False
            
            if args.enable_validation:
                prefs.enable_quality_validation = True
                changed = True
                console.print("[green]✓ Validación de calidad activada por defecto[/green]")
            
            if args.disable_validation:
                prefs.enable_quality_validation = False
                changed = True
                console.print("[yellow]⚠️ Validación de calidad desactivada por defecto[/yellow]")
            
            if args.show_metrics:
                prefs.show_metrics_by_default = True
                changed = True
                console.print("[green]✓ Métricas de calidad se mostrarán por defecto[/green]")
            
            if args.hide_metrics:
                prefs.show_metrics_by_default = False
                changed = True
                console.print("[yellow]📊 Métricas de calidad ocultas por defecto[/yellow]")
            
            if args.prefer_enhanced:
                prefs.prefer_enhanced_algorithms = True
                changed = True
                console.print("[green]🔬 Algoritmos mejorados preferidos por defecto[/green]")
            
            if args.prefer_standard:
                prefs.prefer_enhanced_algorithms = False
                changed = True
                console.print("[yellow]⚡ Algoritmos estándar preferidos por defecto[/yellow]")
            
            if changed:
                success = settings.save_preferences()
                if not success:
                    console.print("[red]✗ Error guardando preferencias[/red]")
                return success
            else:
                console.print("[yellow]No se especificaron cambios en las preferencias[/yellow]")
                return False
        
        elif args.quality_action == 'reset':
            # Restablecer configuración por defecto
            if not args.confirm:
                console.print("[yellow]⚠️ Esto restablecerá toda la configuración de calidad a valores por defecto.[/yellow]")
                console.print("[yellow]Usa --confirm para proceder.[/yellow]")
                return False
            
            success = settings.reset_to_defaults()
            if success:
                console.print("[green]✓ Configuración de calidad restablecida a valores por defecto[/green]")
            else:
                console.print("[red]✗ Error restableciendo configuración[/red]")
            
            return success
        
        elif args.quality_action == 'export':
            # Exportar configuración
            export_path = Path(args.file)
            success = settings.export_settings(export_path)
            
            if success:
                console.print(f"[green]✓ Configuración exportada a: {export_path}[/green]")
            else:
                console.print("[red]✗ Error exportando configuración[/red]")
            
            return success
        
        elif args.quality_action == 'import':
            # Importar configuración
            import_path = Path(args.file)
            if not import_path.exists():
                console.print(f"[red]✗ Archivo no encontrado: {import_path}[/red]")
                return False
            
            success = settings.import_settings(import_path)
            
            if success:
                console.print(f"[green]✓ Configuración importada desde: {import_path}[/green]")
                # Mostrar nueva configuración
                console.print("[dim]Nueva configuración:[/dim]")
                return handle_quality_settings_command(type('args', (), {'quality_action': 'show', 'detailed': False})())
            else:
                console.print("[red]✗ Error importando configuración[/red]")
            
            return success
        
        else:
            console.print(f"[red]Acción no reconocida: {args.quality_action}[/red]")
            return False
    
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        return False

def main_cli(args=None):
    """Función principal del CLI"""
    parser = create_parser()
    parsed_args = parser.parse_args(args)
    
    if not parsed_args.command:
        parser.print_help()
        return False
    
    # Aplicar preferencias de usuario a los argumentos (excepto para quality-settings)
    if parsed_args.command != 'quality-settings':
        parsed_args = apply_user_preferences_to_args(parsed_args, parsed_args.command)
    
    # Ejecutar comando correspondiente
    if parsed_args.command == 'split':
        return handle_split_command(parsed_args)
    elif parsed_args.command == 'convert':
        return handle_convert_command(parsed_args)
    elif parsed_args.command == 'channel':
        return handle_channel_command(parsed_args)
    elif parsed_args.command == 'metadata':
        return handle_metadata_command(parsed_args)
    elif parsed_args.command == 'spectrogram':
        return handle_spectrogram_command(parsed_args)
    elif parsed_args.command == 'quality-settings':
        return handle_quality_settings_command(parsed_args)
    else:
        console.print(f"[red]Comando no reconocido: {parsed_args.command}[/red]")
        return False

if __name__ == "__main__":
    success = main_cli()
    sys.exit(0 if success else 1)
