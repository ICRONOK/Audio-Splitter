"""
Channel Interface para Audio Splitter Suite 2.0
Conversión de canales mono ↔ stereo con algoritmos científicos
Interfaz interactiva con soporte i18n
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional, List

import numpy as np
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

# Imports del sistema i18n
from ..i18n.translator import t

# Imports de los módulos core existentes
try:
    from ..core.converter import AudioConverter
    from ..config.quality_settings import get_quality_settings
except ImportError:
    # Fallback para ejecución directa
    sys.path.append(str(Path(__file__).parent.parent))
    from core.converter import AudioConverter
    from config.quality_settings import get_quality_settings

console = Console()

def run_channel_converter():
    """
    Interface completa para Channel Converter con i18n
    
    Funcionalidades:
    - Análisis de propiedades de canal
    - Conversión mono ↔ stereo  
    - Algoritmos científicos (downmix_center, left_only, right_only, average)
    - Batch processing
    - Integración con quality framework
    """
    
    console.print(Panel(
        f"[bold blue]{t('channel.title', '🎧 Channel Converter Enhanced')}[/bold blue]\\n" +
        f"[dim]{t('channel.subtitle', 'Conversión de canales con algoritmos científicos')}[/dim]",
        title=t('channel.panel_title', 'Channel Converter')
    ))
    
    # Mostrar estado de calidad actual
    try:
        settings = get_quality_settings()
        profile = settings.preferences.default_profile
        profile_emoji = {"studio": "🏆", "professional": "✅", "standard": "⚡", "basic": "📱", "custom": "🔧"}
        quality_emoji = profile_emoji.get(profile.value, "❓")
        console.print(f"[dim]{t('common.current_quality', 'Calidad actual: {quality_emoji} {profile}').format(quality_emoji=quality_emoji, profile=profile.value.upper())}[/dim]")
    except Exception:
        pass
    
    # Input file
    input_file = Prompt.ask(f"\\n{t('common.input_file', '🎧 Archivo de audio de entrada')}")
    
    if not Path(input_file).exists():
        console.print(f"[red]{t('common.file_not_found', '❌ Archivo no encontrado')}[/red]")
        return
    
    # Operation mode selection
    console.print(f"\\n[cyan]{t('channel.operation_mode', '🔧 Modo de operación')}:[/cyan]")
    operations = [
        ("analyze", t('channel.analyze_mode', '📊 Analizar propiedades de canal')),
        ("convert", t('channel.convert_mode', '🔄 Convertir canales')),
        ("batch", t('channel.batch_mode', '📦 Procesamiento por lotes'))
    ]
    
    for i, (key, description) in enumerate(operations, 1):
        console.print(f"  {i}. {description}")
    
    operation_choice = Prompt.ask(
        t('channel.select_operation', 'Selecciona operación'),
        choices=["1", "2", "3"],
        default="1"
    )
    
    operation_map = {"1": "analyze", "2": "convert", "3": "batch"}
    operation = operation_map[operation_choice]
    
    if operation == "analyze":
        run_channel_analysis(input_file)
    elif operation == "convert":
        run_channel_conversion(input_file)
    elif operation == "batch":
        run_batch_channel_operations()

def run_channel_analysis(input_file: str):
    """
    Ejecutar análisis completo de propiedades de canal con métricas científicas
    
    Args:
        input_file: Archivo de audio para analizar
    """
    try:
        converter = AudioConverter()
        
        console.print(f"\\n[cyan]{t('channel.analyzing', 'Analizando propiedades de canal')}...[/cyan]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            # Task 1: Basic channel analysis
            task1 = progress.add_task(t('channel.analysis_progress', 'Analizando audio'), total=None)
            
            # Ejecutar análisis usando AudioConverter existente
            analysis = converter.analyze_channel_properties(input_file)
            progress.update(task1, completed=True)
            
            # Task 2: Advanced scientific analysis
            task2 = progress.add_task(t('channel.scientific_analysis', 'Análisis científico avanzado'), total=None)
            
            # Import quality framework for advanced metrics
            try:
                from ..core.quality_framework import AudioQualityAnalyzer
                
                # Load audio for quality analysis
                import librosa
                y, sr = librosa.load(str(input_file), sr=None, mono=False)
                
                quality_analyzer = AudioQualityAnalyzer()
                
                # Analyze each channel separately for scientific metrics
                if len(y.shape) == 1:
                    # Mono analysis
                    quality_metrics = quality_analyzer.analyze_audio_quality(y, sr)
                    analysis['quality_metrics'] = {
                        'overall': quality_metrics
                    }
                else:
                    # Multi-channel analysis
                    quality_metrics = {}
                    for i in range(y.shape[0]):
                        channel_metrics = quality_analyzer.analyze_audio_quality(y[i], sr)
                        quality_metrics[f'channel_{i}'] = channel_metrics
                    
                    # Overall stereo analysis
                    if y.shape[0] >= 2:
                        # Analyze stereo mix
                        stereo_mix = np.mean(y[:2], axis=0)  # Simple stereo downmix
                        overall_metrics = quality_analyzer.analyze_audio_quality(stereo_mix, sr)
                        quality_metrics['stereo_mix'] = overall_metrics
                    
                    analysis['quality_metrics'] = quality_metrics
                    
            except ImportError:
                console.print(f"[yellow]{t('channel.quality_unavailable', '⚠️ Análisis científico no disponible')}[/yellow]")
                analysis['quality_metrics'] = None
            
            progress.update(task2, completed=True)
        
        # Mostrar resultados en tabla rica con métricas científicas
        display_channel_analysis(analysis)
        
    except Exception as e:
        console.print(f"[red]{t('channel.analysis_error', '❌ Error en análisis: {error}').format(error=str(e))}[/red]")

def display_channel_analysis(analysis: Dict[str, Any]):
    """
    Mostrar resultados de análisis en formato rico
    
    Args:
        analysis: Diccionario con resultados del análisis
    """
    file_name = Path(analysis['file_path']).name
    
    console.print(f"\\n[bold cyan]{t('channel.analysis_title', '📊 Análisis de Canales')}: {file_name}[/bold cyan]")
    
    # Tabla principal de propiedades
    table = Table(title=t('channel.properties_table', 'Propiedades de Audio'), show_header=True, header_style="bold cyan")
    table.add_column(t('channel.property', 'Propiedad'), style="white", width=20)
    table.add_column(t('channel.value', 'Valor'), style="green", width=25)
    table.add_column(t('channel.description', 'Descripción'), style="dim", width=30)
    
    # Información básica
    channel_type_desc = t('channel.mono_desc', 'Audio monofónico') if analysis['channel_type'] == 'mono' else t('channel.stereo_desc', 'Audio estereofónico')
    table.add_row(
        t('channel.type', 'Tipo'), 
        analysis['channel_type'].upper(), 
        channel_type_desc
    )
    
    table.add_row(
        t('channel.channels_count', 'Canales'), 
        str(analysis['current_channels']), 
        t('channel.channels_desc', 'Número de canales de audio')
    )
    
    table.add_row(
        t('channel.sample_rate', 'Sample Rate'), 
        f"{analysis['sample_rate']} Hz", 
        t('channel.sample_rate_desc', 'Frecuencia de muestreo')
    )
    
    table.add_row(
        t('channel.duration', 'Duración'), 
        f"{analysis['duration']:.2f} seg", 
        t('channel.duration_desc', 'Duración total del audio')
    )
    
    console.print(table)
    
    # Análisis específico por tipo
    if analysis['channel_type'] == 'mono':
        show_mono_analysis(analysis)
    else:
        show_stereo_analysis(analysis)
    
    # Mostrar métricas científicas de calidad
    if analysis.get('quality_metrics'):
        show_scientific_quality_metrics(analysis['quality_metrics'])
    
    # Mostrar recomendaciones
    if analysis.get('recommendations'):
        show_recommendations(analysis['recommendations'])

def show_mono_analysis(analysis: Dict[str, Any]):
    """Mostrar análisis específico para audio mono"""
    console.print(f"\\n[bold yellow]{t('channel.mono_analysis', '🎵 Análisis Mono')}:[/bold yellow]")
    
    # Niveles de audio
    rms_db = 20 * (analysis['rms_level'] + 1e-10) if 'rms_level' in analysis else 0
    peak_db = 20 * (analysis['peak_level'] + 1e-10) if 'peak_level' in analysis else 0
    
    console.print(f"[white]{t('channel.rms_level', 'Nivel RMS')}:[/white] {rms_db:.1f} dB")
    console.print(f"[white]{t('channel.peak_level', 'Nivel Peak')}:[/white] {peak_db:.1f} dB")
    
    if 'dynamic_range' in analysis:
        console.print(f"[white]{t('channel.dynamic_range', 'Rango Dinámico')}:[/white] {analysis['dynamic_range']:.1f} dB")

def show_stereo_analysis(analysis: Dict[str, Any]):
    """Mostrar análisis específico para audio stereo"""
    console.print(f"\\n[bold yellow]{t('channel.stereo_analysis', '🎵 Análisis Stereo')}:[/bold yellow]")
    
    if 'stereo_balance_db' in analysis:
        balance = analysis['stereo_balance_db']
        balance_desc = "Izquierda dominante" if balance < -0.5 else "Derecha dominante" if balance > 0.5 else "Balanceado"
        console.print(f"[white]{t('channel.stereo_balance', 'Balance L/R')}:[/white] {balance:+.1f} dB ({balance_desc})")
    
    if 'phase_correlation' in analysis:
        correlation = analysis['phase_correlation']
        correlation_desc = "Excelente" if correlation > 0.9 else "Buena" if correlation > 0.7 else "Pobre"
        console.print(f"[white]{t('channel.phase_correlation', 'Correlación de Fase')}:[/white] {correlation:.3f} ({correlation_desc})")
    
    if 'stereo_width' in analysis:
        width = analysis['stereo_width']
        width_desc = "Muy amplio" if width > 0.8 else "Amplio" if width > 0.5 else "Estrecho"
        console.print(f"[white]{t('channel.stereo_width', 'Amplitud Stereo')}:[/white] {width:.3f} ({width_desc})")

def show_recommendations(recommendations: List[str]):
    """Mostrar recomendaciones de conversión"""
    console.print(f"\\n[bold green]{t('channel.recommendations', '💡 Recomendaciones')}:[/bold green]")
    for rec in recommendations:
        console.print(f"  • {rec}")

def run_channel_conversion(input_file: str):
    """
    Ejecutar conversión de canales individual
    
    Args:
        input_file: Archivo de audio de entrada
    """
    try:
        converter = AudioConverter()
        
        # Primero analizar archivo actual
        console.print(f"\\n[cyan]{t('channel.detecting_format', 'Detectando formato actual')}...[/cyan]")
        analysis = converter.analyze_channel_properties(input_file)
        current_channels = analysis['current_channels']
        
        console.print(f"[dim]{t('channel.current_format', 'Formato actual: {channels} canales').format(channels=current_channels)}[/dim]")
        
        # Pedir archivo de salida
        output_file = Prompt.ask(f"{t('common.output_file', '📁 Archivo de salida')}")
        
        # Seleccionar canales objetivo
        console.print(f"\\n[cyan]{t('channel.target_channels', '📊 Canales objetivo')}:[/cyan]")
        target_options = [
            ("1", t('channel.mono_option', '1 - Mono (1 canal)')),
            ("2", t('channel.stereo_option', '2 - Stereo (2 canales)'))
        ]
        
        for value, description in target_options:
            console.print(f"  {description}")
        
        target_channels = int(Prompt.ask(
            t('channel.select_channels', 'Selecciona canales objetivo'),
            choices=["1", "2"],
            default="2" if current_channels == 1 else "1"
        ))
        
        # Si convertimos a mono, seleccionar algoritmo
        algorithm = "downmix_center"  # Default
        if target_channels == 1 and current_channels > 1:
            console.print(f"\\n[cyan]{t('channel.downmix_algorithm', '🎛️ Algoritmo de downmix')}:[/cyan]")
            algorithms = [
                ("downmix_center", t('channel.downmix_center', 'Centro (L+R)/2 - Recomendado')),
                ("left_only", t('channel.left_only', 'Solo canal izquierdo')),
                ("right_only", t('channel.right_only', 'Solo canal derecho')),
                ("average", t('channel.average', 'Promedio RMS ponderado'))
            ]
            
            for i, (alg, description) in enumerate(algorithms, 1):
                console.print(f"  {i}. {description}")
            
            algorithm_choice = Prompt.ask(
                t('channel.select_algorithm', 'Selecciona algoritmo'),
                choices=["1", "2", "3", "4"],
                default="1"
            )
            
            algorithm_map = {"1": "downmix_center", "2": "left_only", "3": "right_only", "4": "average"}
            algorithm = algorithm_map[algorithm_choice]
        
        # Preservar metadatos
        preserve_metadata = Confirm.ask(
            t('channel.preserve_metadata', '🏷️ ¿Preservar metadatos originales?'),
            default=True
        )
        
        # Ejecutar conversión
        channel_name = t('channel.mono_target', 'mono') if target_channels == 1 else t('channel.stereo_target', 'stereo')
        console.print(f"\\n[cyan]{t('channel.converting', 'Convirtiendo a {channel_name} usando algoritmo \"{algorithm}\"').format(channel_name=channel_name, algorithm=algorithm)}[/cyan]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(t('channel.conversion_progress', 'Procesando conversión'), total=None)
            
            # Usar AudioConverter existente
            success = converter.convert_channels(
                input_file, output_file, target_channels,
                algorithm, preserve_metadata
            )
            
            progress.update(task, completed=True)
        
        if success:
            console.print(f"[green]✓ {t('channel.conversion_success', 'Conversión de canales exitosa')}[/green]")
            
            # Mostrar información post-conversión
            try:
                final_info = converter.get_audio_info(output_file)
                console.print(f"[dim]{t('channel.result_info', 'Resultado: {channels}-channel, {sample_rate} Hz').format(channels=final_info['channels'], sample_rate=final_info['sample_rate'])}[/dim]")
            except Exception:
                pass
        else:
            console.print(f"[red]✗ {t('channel.conversion_error', 'Error en conversión de canales')}[/red]")
            
    except Exception as e:
        console.print(f"[red]{t('channel.execution_error', '❌ Error ejecutando conversión: {error}').format(error=str(e))}[/red]")

def run_batch_channel_operations():
    """
    Ejecutar operaciones de conversión por lotes
    """
    try:
        converter = AudioConverter()
        
        console.print(f"\\n[bold blue]{t('channel.batch_title', '📦 Conversión por Lotes')}[/bold blue]")
        
        # Input directory o files
        input_path = Prompt.ask(f"{t('channel.batch_input', '📁 Directorio o archivo de entrada')}")
        
        if not Path(input_path).exists():
            console.print(f"[red]{t('common.file_not_found', '❌ Archivo no encontrado')}[/red]")
            return
        
        # Output directory
        output_dir = Prompt.ask(f"{t('channel.batch_output', '📂 Directorio de salida')}")
        
        # Target channels
        target_channels = int(Prompt.ask(
            t('channel.select_channels', 'Selecciona canales objetivo'),
            choices=["1", "2"],
            default="1"
        ))
        
        # Algorithm for stereo->mono
        algorithm = "downmix_center"
        if target_channels == 1:
            console.print(f"\\n[cyan]{t('channel.downmix_algorithm', '🎛️ Algoritmo de downmix')}:[/cyan]")
            algorithm_choice = Prompt.ask(
                t('channel.select_algorithm', 'Selecciona algoritmo'),
                choices=["1", "2", "3", "4"],
                default="1"
            )
            algorithm_map = {"1": "downmix_center", "2": "left_only", "3": "right_only", "4": "average"}
            algorithm = algorithm_map[algorithm_choice]
        
        # Recursive processing
        recursive = Confirm.ask(
            t('channel.recursive_processing', '🔄 ¿Procesamiento recursivo en subdirectorios?'),
            default=False
        )
        
        # Preserve metadata
        preserve_metadata = Confirm.ask(
            t('channel.preserve_metadata', '🏷️ ¿Preservar metadatos originales?'),
            default=True
        )
        
        # Execute batch conversion
        console.print(f"\\n[cyan]{t('channel.batch_processing', 'Procesando conversión por lotes')}...[/cyan]")
        
        successful, failed = converter.batch_convert_channels(
            input_path, output_dir, target_channels,
            algorithm, preserve_metadata, recursive
        )
        
        # Show results
        if failed == 0:
            console.print(f"[green]✓ {t('channel.batch_success', 'Conversión por lotes completada: {successful} archivos procesados').format(successful=successful)}[/green]")
        else:
            console.print(f"[yellow]⚠️ {t('channel.batch_partial', 'Conversión parcial: {successful} exitosos, {failed} fallidos').format(successful=successful, failed=failed)}[/yellow]")
        
    except Exception as e:
        console.print(f"[red]{t('channel.batch_error', '❌ Error en conversión por lotes: {error}').format(error=str(e))}[/red]")

def show_scientific_quality_metrics(quality_metrics: Dict[str, Any]):
    """
    Mostrar métricas científicas de calidad de audio
    
    Args:
        quality_metrics: Diccionario con métricas de calidad por canal
    """
    console.print(f"\\n[bold magenta]{t('channel.scientific_metrics', '🔬 Métricas Científicas de Calidad')}:[/bold magenta]")
    
    # Crear tabla de métricas científicas
    metrics_table = Table(
        title=t('channel.scientific_table', 'Análisis de Calidad Profesional'), 
        show_header=True, 
        header_style="bold magenta"
    )
    metrics_table.add_column(t('channel.metric_type', 'Métrica'), style="white", width=20)
    metrics_table.add_column(t('channel.metric_value', 'Valor'), style="cyan", width=15)
    metrics_table.add_column(t('channel.metric_standard', 'Estándar'), style="green", width=15)
    metrics_table.add_column(t('channel.metric_status', 'Estado'), style="bold", width=15)
    
    # Función helper para formatear estado de calidad
    def format_quality_status(level):
        if hasattr(level, 'value'):
            level_str = level.value
        else:
            level_str = str(level).lower()
            
        emoji_map = {
            'excellent': '🟢 Excelente',
            'good': '🟡 Bueno',
            'acceptable': '🟠 Aceptable', 
            'poor': '🔴 Pobre',
            'failed': '❌ Fallo'
        }
        return emoji_map.get(level_str, f'❓ {level_str}')
    
    # Mostrar métricas según el tipo de análisis
    if 'overall' in quality_metrics:
        # Análisis mono
        metrics = quality_metrics['overall']
        
        if hasattr(metrics, 'thd_plus_n_db') and metrics.thd_plus_n_db is not None:
            status = format_quality_status(metrics.overall_quality) if hasattr(metrics, 'overall_quality') else '❓ N/A'
            metrics_table.add_row(
                "THD+N", 
                f"{metrics.thd_plus_n_db:.1f} dB",
                "< -60dB (Prof)",
                status
            )
        
        if hasattr(metrics, 'snr_db') and metrics.snr_db is not None:
            status = format_quality_status(metrics.overall_quality) if hasattr(metrics, 'overall_quality') else '❓ N/A'
            metrics_table.add_row(
                "SNR", 
                f"{metrics.snr_db:.1f} dB",
                "> 90dB (Prof)",
                status
            )
        
        if hasattr(metrics, 'dynamic_range_db') and metrics.dynamic_range_db is not None:
            metrics_table.add_row(
                "Rango Dinámico", 
                f"{metrics.dynamic_range_db:.1f} dB",
                "> 60dB",
                "🟢 Bueno" if metrics.dynamic_range_db > 60 else "🟡 Aceptable"
            )
            
    elif 'channel_0' in quality_metrics:
        # Análisis multi-canal - mostrar resumen
        console.print(f"[dim]{t('channel.multichannel_note', 'Análisis por canal individual:')}[/dim]")
        
        for channel_key, metrics in quality_metrics.items():
            if channel_key.startswith('channel_'):
                channel_num = channel_key.split('_')[1]
                console.print(f"\\n[cyan]{t('channel.channel_analysis', 'Canal {num}:').format(num=channel_num)}[/cyan]")
                
                # Mini tabla por canal
                if hasattr(metrics, 'thd_plus_n_db') and metrics.thd_plus_n_db is not None:
                    status = format_quality_status(metrics.overall_quality) if hasattr(metrics, 'overall_quality') else '❓'
                    console.print(f"  THD+N: {metrics.thd_plus_n_db:.1f} dB {status}")
                
                if hasattr(metrics, 'snr_db') and metrics.snr_db is not None:
                    console.print(f"  SNR: {metrics.snr_db:.1f} dB")
        
        # Mostrar análisis del mix estéreo si está disponible
        if 'stereo_mix' in quality_metrics:
            metrics = quality_metrics['stereo_mix']
            console.print(f"\\n[bold cyan]{t('channel.stereo_mix_analysis', '🎭 Análisis del Mix Estéreo:')}[/bold cyan]")
            
            if hasattr(metrics, 'thd_plus_n_db') and metrics.thd_plus_n_db is not None:
                status = format_quality_status(metrics.overall_quality) if hasattr(metrics, 'overall_quality') else '❓ N/A'
                metrics_table.add_row(
                    "THD+N (Mix)", 
                    f"{metrics.thd_plus_n_db:.1f} dB",
                    "< -60dB",
                    status
                )
            
            if hasattr(metrics, 'snr_db') and metrics.snr_db is not None:
                metrics_table.add_row(
                    "SNR (Mix)", 
                    f"{metrics.snr_db:.1f} dB", 
                    "> 90dB",
                    format_quality_status(metrics.overall_quality) if hasattr(metrics, 'overall_quality') else '❓'
                )
    
    # Mostrar tabla solo si tiene contenido
    if metrics_table.rows:
        console.print(metrics_table)
    else:
        console.print(f"[yellow]{t('channel.no_scientific_data', '⚠️ No hay datos científicos disponibles')}[/yellow]")
    
    # Mostrar nota explicativa
    console.print(f"\\n[dim]{t('channel.scientific_note', 'Nota: Estándares profesionales - THD+N <-60dB, SNR >90dB, Estudio: THD+N <-80dB, SNR >100dB')}[/dim]")

# Entry point para testing
if __name__ == "__main__":
    console.print("[cyan]Testing Channel Interface...[/cyan]")
    run_channel_converter()