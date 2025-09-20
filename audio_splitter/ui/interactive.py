"""
Interfaz interactiva principal del Audio Splitter Suite
"""

import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

console = Console()

def interactive_menu():
    """Menú principal interactivo del sistema Audio Splitter Suite"""
    
    console.print(Panel(
        "[bold blue]🎵 Audio Splitter Suite 2.0[/bold blue]\n" +
        "[dim]Sistema completo de procesamiento de audio[/dim]",
        title="Audio Processing Suite"
    ))
    
    while True:
        console.print("\n[cyan]🎛️ Módulos disponibles:[/cyan]")
        options = [
            "1. 🔄 Audio Converter - Conversión entre formatos (WAV/MP3/FLAC)",
            "2. ✂️  Audio Splitter - División en segmentos con metadatos",
            "3. 🏷️  Metadata Editor - Editor profesional de metadatos",
            "4. 📊 Spectrogram Generator - Generación de espectrogramas para LLMs",
            "5. 🖼️  Artwork Manager - Gestión de carátulas",
            "6. 📄 Documentación y ayuda",
            "7. 🚪 Salir"
        ]
        
        for option in options:
            console.print(f"  {option}")
        
        choice = Prompt.ask("\nSelecciona un módulo", choices=["1", "2", "3", "4", "5", "6", "7"])
        
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
            show_documentation()
        elif choice == "7":
            console.print("\n[yellow]👋 ¡Gracias por usar Audio Splitter Suite![/yellow]")
            break

def run_audio_converter():
    """Ejecuta el módulo de conversión de audio"""
    try:
        from ..core.converter import interactive_mode
        console.print("\n[blue]🔄 Iniciando Audio Converter...[/blue]")
        interactive_mode()
    except ImportError as e:
        console.print(f"[red]❌ Error importando Audio Converter: {e}[/red]")
    except Exception as e:
        console.print(f"[red]❌ Error ejecutando Audio Converter: {e}[/red]")

def run_audio_splitter():
    """Ejecuta el módulo de división de audio"""
    try:
        from ..core.splitter import interactive_mode
        console.print("\n[blue]✂️ Iniciando Audio Splitter...[/blue]")
        interactive_mode()
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
    """Ejecuta el generador de espectrogramas para LLMs"""
    try:
        from ..core.spectrogram_generator import SpectrogramGenerator
        console.print("\n[blue]📊 Iniciando Spectrogram Generator...[/blue]")
        
        # Implementación del modo interactivo para espectrogramas
        from rich.prompt import Prompt
        from pathlib import Path
        
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
        
        # Generar espectrograma
        generator = SpectrogramGenerator()
        
        console.print(f"\n[cyan]Generando espectrograma {spectrogram_type}...[/cyan]")
        
        if spectrogram_type == "mel":
            result = generator.generate_mel_spectrogram(input_file, output_file)
        elif spectrogram_type == "linear":
            result = generator.generate_linear_spectrogram(input_file, output_file)
        elif spectrogram_type == "cqt":
            result = generator.generate_cqt_spectrogram(input_file, output_file)
        elif spectrogram_type == "dual":
            # Para dual, necesitamos un directorio
            output_dir = Path(output_file).parent
            input_path = Path(input_file)
            
            mel_output = output_dir / f"{input_path.stem}_mel_spectrogram.png"
            linear_output = output_dir / f"{input_path.stem}_linear_spectrogram.png"
            
            console.print("[cyan]Generando espectrograma Mel...[/cyan]")
            mel_result = generator.generate_mel_spectrogram(input_file, mel_output)
            
            console.print("[cyan]Generando espectrograma Linear...[/cyan]")
            linear_result = generator.generate_linear_spectrogram(input_file, linear_output)
            
            result = {
                'status': 'success',
                'spectrogram_type': 'dual',
                'mel_output': str(mel_output),
                'linear_output': str(linear_output)
            }
        
        if result['status'] == 'success':
            console.print(f"\n[green]✓ Espectrograma generado exitosamente[/green]")
            
            if spectrogram_type == "dual":
                console.print(f"[dim]Mel: {result['mel_output']}[/dim]")
                console.print(f"[dim]Linear: {result['linear_output']}[/dim]")
            else:
                console.print(f"[dim]Archivo: {output_file}[/dim]")
            
            # Mostrar métricas si están disponibles
            if 'quality_metrics' in result:
                metrics = result['quality_metrics']
                console.print("\n[bold yellow]Métricas de calidad para LLM:[/bold yellow]")
                console.print(f"[dim]Resolución temporal: {metrics.get('temporal_resolution_ms', 'N/A'):.1f} ms[/dim]")
                console.print(f"[dim]Resolución frecuencial: {metrics.get('frequency_resolution_hz', 'N/A'):.1f} Hz[/dim]")
                console.print(f"[dim]Rango dinámico: {metrics.get('dynamic_range_db', 'N/A'):.1f} dB[/dim]")
                
            console.print("\n[bold yellow]Información para LLM Context:[/bold yellow]")
            console.print(f"[dim]• Tipo: {result['spectrogram_type']} - Optimizado para análisis visual[/dim]")
            console.print(f"[dim]• Resolución: 1024x512 pixels (óptimo para vision models)[/dim]")
            console.print(f"[dim]• Colormap: viridis (perceptualmente uniforme)[/dim]")
        else:
            console.print("[red]✗ Error generando espectrograma[/red]")
            
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
