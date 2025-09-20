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
from rich.console import Console

console = Console()

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
    
    # Comando channel - Nuevo comando para conversión de canales
    channel_parser = subparsers.add_parser('channel', help='Convertir canales de audio (mono ↔ stereo)')
    channel_parser.add_argument('input', help='Archivo o directorio de entrada')
    channel_parser.add_argument('--output', '-o', required=True, help='Archivo o directorio de salida')
    channel_parser.add_argument('--channels', '-c', required=True, type=int, choices=[1, 2],
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
    
    return parser

def handle_split_command(args):
    """Maneja el comando split"""
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
        
        # Ejecutar división
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
    """Maneja el comando convert"""
    try:
        converter = AudioConverter()
        
        if args.batch:
            # Conversión por lotes
            successful, failed = converter.batch_convert(
                args.input, args.output, args.format, 
                args.quality, True, args.recursive
            )
            console.print(f"[green]Conversión completada: {successful} exitosos, {failed} fallidos[/green]")
            return failed == 0
        else:
            # Conversión individual
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
    """Maneja el comando spectrogram - Optimizado para LLM analysis"""
    try:
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
        
        if result['status'] == 'success':
            console.print(f"[green]✓ Espectrograma {args.type} generado exitosamente[/green]")
            
            # Mostrar métricas de calidad LLM
            if 'quality_metrics' in result:
                metrics = result['quality_metrics']
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
            
        return result['status'] == 'success'
        
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
    else:
        console.print(f"[red]Comando no reconocido: {parsed_args.command}[/red]")
        return False

if __name__ == "__main__":
    success = main_cli()
    sys.exit(0 if success else 1)
