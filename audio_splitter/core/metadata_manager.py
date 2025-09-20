#!/usr/bin/env python3
"""
Metadata Editor Avanzado - Editor profesional de metadatos para archivos de audio
Soporta ID3v2.4, Vorbis Comments, iTunes tags y gestión de carátulas
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass, asdict

# Bibliotecas de metadatos
from mutagen import File
from mutagen.mp3 import MP3
from mutagen.flac import FLAC, Picture
from mutagen.mp4 import MP4
from mutagen.wave import WAVE
from mutagen.aiff import AIFF
from mutagen.id3 import ID3NoHeaderError, TIT2, TPE1, TALB, TPE2, TDRC, TCON, TRCK, TPOS, TCOM, COMM, APIC, ID3
from mutagen._vorbis import VCommentDict

# Pillow para manejo de imágenes (opcional)
try:
    from PIL import Image
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False

# Custom exception for metadata operations
class MetadataError(Exception):
    """Exception raised for metadata-related errors"""
    pass

# UI y utilidades
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

console = Console()

@dataclass
class AudioMetadata:
    """Clase para representar metadatos de audio de forma unificada"""
    title: Optional[str] = None
    artist: Optional[str] = None
    album: Optional[str] = None
    albumartist: Optional[str] = None
    date: Optional[str] = None
    genre: Optional[str] = None
    track: Optional[str] = None
    track_total: Optional[str] = None
    disc: Optional[str] = None
    disc_total: Optional[str] = None
    composer: Optional[str] = None
    comment: Optional[str] = None
    artwork_data: Optional[bytes] = None
    artwork_mime: Optional[str] = None
    artwork_description: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario excluyendo campos None"""
        return {k: v for k, v in asdict(self).items() if v is not None}

class MetadataEditor:
    """Editor principal de metadatos con soporte para múltiples formatos"""
    
    def __init__(self):
        pass
    
    def read_metadata(self, file_path: Union[str, Path]) -> Optional[AudioMetadata]:
        """Lee metadatos de un archivo de audio"""
        try:
            audio_file = File(str(file_path))
            if audio_file is None:
                console.print(f"[red]No se pudo leer el archivo: {file_path}[/red]")
                return None
            
            metadata = AudioMetadata()
            
            # Leer metadatos según el formato
            if isinstance(audio_file, MP3):
                self._read_id3_tags(audio_file, metadata)
            elif isinstance(audio_file, FLAC):
                self._read_vorbis_tags(audio_file, metadata)
            elif isinstance(audio_file, MP4):
                self._read_mp4_tags(audio_file, metadata)
            elif isinstance(audio_file, (WAVE, AIFF)):
                self._read_id3_tags_from_container(audio_file, metadata)
            
            return metadata
            
        except Exception as e:
            console.print(f"[red]Error leyendo metadatos: {e}[/red]")
            return None
    
    def _read_id3_tags(self, audio_file: MP3, metadata: AudioMetadata):
        """Lee tags ID3 de archivos MP3"""
        tags = audio_file.tags
        if not tags:
            return
        
        # Mapeo básico de tags ID3
        if 'TIT2' in tags:
            metadata.title = str(tags['TIT2'].text[0]) if tags['TIT2'].text else None
        if 'TPE1' in tags:
            metadata.artist = str(tags['TPE1'].text[0]) if tags['TPE1'].text else None
        if 'TALB' in tags:
            metadata.album = str(tags['TALB'].text[0]) if tags['TALB'].text else None
        if 'TPE2' in tags:
            metadata.albumartist = str(tags['TPE2'].text[0]) if tags['TPE2'].text else None
        if 'TDRC' in tags:
            metadata.date = str(tags['TDRC'].text[0]) if tags['TDRC'].text else None
        if 'TCON' in tags:
            metadata.genre = str(tags['TCON'].text[0]) if tags['TCON'].text else None
        if 'TRCK' in tags:
            track_info = str(tags['TRCK'].text[0]).split('/')
            metadata.track = track_info[0]
            if len(track_info) > 1:
                metadata.track_total = track_info[1]
    
    def _read_id3_tags_from_container(self, audio_file: Union[WAVE, AIFF], metadata: AudioMetadata):
        """Lee tags ID3 de archivos WAV/AIFF que pueden contener chunks ID3"""
        # Los archivos WAV/AIFF pueden tener tags ID3v2 embebidos
        if hasattr(audio_file, 'tags') and audio_file.tags:
            # Si ya tiene tags ID3, los leemos como MP3
            if hasattr(audio_file.tags, 'getall'):
                self._read_id3_tags_direct(audio_file.tags, metadata)
        else:
            # Si no tiene tags, intentamos crear un objeto ID3 vacío
            console.print(f"[yellow]Archivo {type(audio_file).__name__} sin metadatos existentes[/yellow]")
    
    def _read_id3_tags_direct(self, tags, metadata: AudioMetadata):
        """Lee tags ID3 directamente de un objeto de tags"""
        # Mapeo básico de tags ID3 (similar a _read_id3_tags pero sin audio_file.tags)
        if 'TIT2' in tags:
            metadata.title = str(tags['TIT2'].text[0]) if tags['TIT2'].text else None
        if 'TPE1' in tags:
            metadata.artist = str(tags['TPE1'].text[0]) if tags['TPE1'].text else None
        if 'TALB' in tags:
            metadata.album = str(tags['TALB'].text[0]) if tags['TALB'].text else None
        if 'TPE2' in tags:
            metadata.albumartist = str(tags['TPE2'].text[0]) if tags['TPE2'].text else None
        if 'TDRC' in tags:
            metadata.date = str(tags['TDRC'].text[0]) if tags['TDRC'].text else None
        if 'TCON' in tags:
            metadata.genre = str(tags['TCON'].text[0]) if tags['TCON'].text else None
        if 'TRCK' in tags:
            track_info = str(tags['TRCK'].text[0]).split('/')
            metadata.track = track_info[0]
            if len(track_info) > 1:
                metadata.track_total = track_info[1]
    
    def _read_vorbis_tags(self, audio_file: FLAC, metadata: AudioMetadata):
        """Lee Vorbis Comments de archivos FLAC"""
        if not audio_file.tags:
            return
        
        # Mapeo básico de Vorbis Comments
        if 'TITLE' in audio_file.tags:
            metadata.title = audio_file.tags['TITLE'][0] if audio_file.tags['TITLE'] else None
        if 'ARTIST' in audio_file.tags:
            metadata.artist = audio_file.tags['ARTIST'][0] if audio_file.tags['ARTIST'] else None
        if 'ALBUM' in audio_file.tags:
            metadata.album = audio_file.tags['ALBUM'][0] if audio_file.tags['ALBUM'] else None
        if 'ALBUMARTIST' in audio_file.tags:
            metadata.albumartist = audio_file.tags['ALBUMARTIST'][0] if audio_file.tags['ALBUMARTIST'] else None
        if 'DATE' in audio_file.tags:
            metadata.date = audio_file.tags['DATE'][0] if audio_file.tags['DATE'] else None
        if 'GENRE' in audio_file.tags:
            metadata.genre = audio_file.tags['GENRE'][0] if audio_file.tags['GENRE'] else None
        if 'TRACKNUMBER' in audio_file.tags:
            metadata.track = audio_file.tags['TRACKNUMBER'][0] if audio_file.tags['TRACKNUMBER'] else None
    
    def _read_mp4_tags(self, audio_file: MP4, metadata: AudioMetadata):
        """Lee tags de archivos MP4/M4A"""
        tags = audio_file.tags
        if not tags:
            return
        
        # Mapeo básico de tags MP4
        if '©nam' in tags:
            metadata.title = str(tags['©nam'][0]) if tags['©nam'] else None
        if '©ART' in tags:
            metadata.artist = str(tags['©ART'][0]) if tags['©ART'] else None
        if '©alb' in tags:
            metadata.album = str(tags['©alb'][0]) if tags['©alb'] else None
        if 'aART' in tags:
            metadata.albumartist = str(tags['aART'][0]) if tags['aART'] else None
        if '©day' in tags:
            metadata.date = str(tags['©day'][0]) if tags['©day'] else None
        if '©gen' in tags:
            metadata.genre = str(tags['©gen'][0]) if tags['©gen'] else None
        if '©wrt' in tags:
            metadata.composer = str(tags['©wrt'][0]) if tags['©wrt'] else None
        if '©cmt' in tags:
            metadata.comment = str(tags['©cmt'][0]) if tags['©cmt'] else None
        
        # Track y disc numbers en MP4
        if 'trkn' in tags and isinstance(tags['trkn'][0], tuple):
            metadata.track = str(tags['trkn'][0][0])
            if tags['trkn'][0][1] > 0:
                metadata.track_total = str(tags['trkn'][0][1])
        
        if 'disk' in tags and isinstance(tags['disk'][0], tuple):
            metadata.disc = str(tags['disk'][0][0])
            if tags['disk'][0][1] > 0:
                metadata.disc_total = str(tags['disk'][0][1])
        
        # Leer artwork
        if 'covr' in tags:
            metadata.artwork_data = bytes(tags['covr'][0])
            metadata.artwork_mime = 'image/jpeg'  # MP4 típicamente usa JPEG
            metadata.artwork_description = 'Cover'
    
    def write_metadata(self, file_path: Union[str, Path], metadata: AudioMetadata) -> bool:
        """Escribe metadatos a un archivo de audio"""
        try:
            audio_file = File(str(file_path))
            if audio_file is None:
                console.print(f"[red]No se pudo abrir el archivo: {file_path}[/red]")
                return False
            
            # Escribir según el formato
            if isinstance(audio_file, MP3):
                success = self._write_id3_tags(audio_file, metadata)
            elif isinstance(audio_file, FLAC):
                success = self._write_vorbis_tags(audio_file, metadata)
            elif isinstance(audio_file, MP4):
                success = self._write_mp4_tags(audio_file, metadata)
            elif isinstance(audio_file, (WAVE, AIFF)):
                success = self._write_id3_tags_to_container(audio_file, metadata)
            else:
                console.print(f"[red]Formato no soportado para escritura: {type(audio_file)}[/red]")
                return False
            
            if success:
                audio_file.save()
                return True
            
            return False
            
        except Exception as e:
            console.print(f"[red]Error escribiendo metadatos: {e}[/red]")
            return False
    
    def _write_id3_tags(self, audio_file: MP3, metadata: AudioMetadata) -> bool:
        """Escribe tags ID3 a archivos MP3"""
        try:
            # Asegurar que existan tags ID3
            if audio_file.tags is None:
                audio_file.add_tags()
            
            tags = audio_file.tags
            
            # Limpiar tags existentes de los campos que vamos a escribir
            tags_to_remove = ['TIT2', 'TPE1', 'TALB', 'TPE2', 'TDRC', 'TCON', 'TRCK', 'TPOS', 'TCOM']
            for tag_id in tags_to_remove:
                if tag_id in tags:
                    del tags[tag_id]
            
            # Limpiar comentarios
            comm_keys = [k for k in tags.keys() if k.startswith('COMM')]
            for key in comm_keys:
                del tags[key]
            
            # Limpiar artwork
            apic_keys = [k for k in tags.keys() if k.startswith('APIC')]
            for key in apic_keys:
                del tags[key]
            
            # Escribir tags básicos
            if metadata.title:
                tags.add(TIT2(encoding=3, text=metadata.title))
            if metadata.artist:
                tags.add(TPE1(encoding=3, text=metadata.artist))
            if metadata.album:
                tags.add(TALB(encoding=3, text=metadata.album))
            if metadata.albumartist:
                tags.add(TPE2(encoding=3, text=metadata.albumartist))
            if metadata.date:
                tags.add(TDRC(encoding=3, text=metadata.date))
            if metadata.genre:
                tags.add(TCON(encoding=3, text=metadata.genre))
            if metadata.composer:
                tags.add(TCOM(encoding=3, text=metadata.composer))
            if metadata.comment:
                tags.add(COMM(encoding=3, lang='eng', desc='', text=metadata.comment))
            
            # Track number
            if metadata.track:
                track_text = metadata.track
                if metadata.track_total:
                    track_text += f"/{metadata.track_total}"
                tags.add(TRCK(encoding=3, text=track_text))
            
            # Disc number
            if metadata.disc:
                disc_text = metadata.disc
                if metadata.disc_total:
                    disc_text += f"/{metadata.disc_total}"
                tags.add(TPOS(encoding=3, text=disc_text))
            
            # Artwork
            if metadata.artwork_data:
                tags.add(APIC(
                    encoding=3,
                    mime=metadata.artwork_mime or 'image/jpeg',
                    type=3,  # Cover (front)
                    desc=metadata.artwork_description or 'Cover',
                    data=metadata.artwork_data
                ))
            
            return True
            
        except Exception as e:
            console.print(f"[red]Error escribiendo tags ID3: {e}[/red]")
            return False
    
    def _write_id3_tags_to_container(self, audio_file: Union[WAVE, AIFF], metadata: AudioMetadata) -> bool:
        """Escribe tags ID3 a archivos WAV/AIFF"""
        try:
            # Intentar agregar tags ID3 al archivo WAV/AIFF
            if audio_file.tags is None:
                audio_file.add_tags()
            
            tags = audio_file.tags
            
            # Usar la misma lógica que para MP3
            return self._write_id3_tags_direct(tags, metadata)
            
        except Exception as e:
            console.print(f"[red]Error escribiendo tags ID3 a {type(audio_file).__name__}: {e}[/red]")
            console.print(f"[yellow]Nota: Los archivos {type(audio_file).__name__} tienen soporte limitado para metadatos[/yellow]")
            console.print(f"[yellow]Considera convertir a MP3 o FLAC para mejor soporte de metadatos[/yellow]")
            return False
    
    def _write_id3_tags_direct(self, tags, metadata: AudioMetadata) -> bool:
        """Escribe tags ID3 directamente a un objeto de tags"""
        try:
            # Limpiar tags existentes de los campos que vamos a escribir
            tags_to_remove = ['TIT2', 'TPE1', 'TALB', 'TPE2', 'TDRC', 'TCON', 'TRCK', 'TPOS', 'TCOM']
            for tag_id in tags_to_remove:
                if tag_id in tags:
                    del tags[tag_id]
            
            # Limpiar comentarios
            comm_keys = [k for k in tags.keys() if k.startswith('COMM')]
            for key in comm_keys:
                del tags[key]
            
            # Limpiar artwork
            apic_keys = [k for k in tags.keys() if k.startswith('APIC')]
            for key in apic_keys:
                del tags[key]
            
            # Escribir tags básicos
            if metadata.title:
                tags.add(TIT2(encoding=3, text=metadata.title))
            if metadata.artist:
                tags.add(TPE1(encoding=3, text=metadata.artist))
            if metadata.album:
                tags.add(TALB(encoding=3, text=metadata.album))
            if metadata.albumartist:
                tags.add(TPE2(encoding=3, text=metadata.albumartist))
            if metadata.date:
                tags.add(TDRC(encoding=3, text=metadata.date))
            if metadata.genre:
                tags.add(TCON(encoding=3, text=metadata.genre))
            if metadata.composer:
                tags.add(TCOM(encoding=3, text=metadata.composer))
            if metadata.comment:
                tags.add(COMM(encoding=3, lang='eng', desc='', text=metadata.comment))
            
            # Track number
            if metadata.track:
                track_text = metadata.track
                if metadata.track_total:
                    track_text += f"/{metadata.track_total}"
                tags.add(TRCK(encoding=3, text=track_text))
            
            # Disc number
            if metadata.disc:
                disc_text = metadata.disc
                if metadata.disc_total:
                    disc_text += f"/{metadata.disc_total}"
                tags.add(TPOS(encoding=3, text=disc_text))
            
            # Artwork (limitado en WAV/AIFF)
            if metadata.artwork_data:
                tags.add(APIC(
                    encoding=3,
                    mime=metadata.artwork_mime or 'image/jpeg',
                    type=3,  # Cover (front)
                    desc=metadata.artwork_description or 'Cover',
                    data=metadata.artwork_data
                ))
            
            return True
            
        except Exception as e:
            console.print(f"[red]Error escribiendo tags ID3 directos: {e}[/red]")
            return False
    
    def _write_vorbis_tags(self, audio_file: FLAC, metadata: AudioMetadata) -> bool:
        """Escribe Vorbis Comments a archivos FLAC"""
        try:
            # Limpiar tags existentes
            if audio_file.tags:
                audio_file.tags.clear()
            else:
                audio_file.tags = VCommentDict()
            
            tags = audio_file.tags
            
            # Escribir tags
            if metadata.title:
                tags['TITLE'] = metadata.title
            if metadata.artist:
                tags['ARTIST'] = metadata.artist
            if metadata.album:
                tags['ALBUM'] = metadata.album
            if metadata.albumartist:
                tags['ALBUMARTIST'] = metadata.albumartist
            if metadata.date:
                tags['DATE'] = metadata.date
            if metadata.genre:
                tags['GENRE'] = metadata.genre
            if metadata.composer:
                tags['COMPOSER'] = metadata.composer
            if metadata.comment:
                tags['COMMENT'] = metadata.comment
            if metadata.track:
                tags['TRACKNUMBER'] = metadata.track
            if metadata.track_total:
                tags['TRACKTOTAL'] = metadata.track_total
            if metadata.disc:
                tags['DISCNUMBER'] = metadata.disc
            if metadata.disc_total:
                tags['DISCTOTAL'] = metadata.disc_total
            
            # Artwork
            if metadata.artwork_data:
                # Limpiar imágenes existentes
                audio_file.clear_pictures()
                
                # Crear objeto Picture
                pic = Picture()
                pic.type = 3  # Cover (front)
                pic.mime = metadata.artwork_mime or 'image/jpeg'
                pic.desc = metadata.artwork_description or 'Cover'
                pic.data = metadata.artwork_data
                
                # Agregar al archivo
                audio_file.add_picture(pic)
            
            return True
            
        except Exception as e:
            console.print(f"[red]Error escribiendo tags Vorbis: {e}[/red]")
            return False
    
    def _write_mp4_tags(self, audio_file: MP4, metadata: AudioMetadata) -> bool:
        """Escribe tags a archivos MP4/M4A"""
        try:
            # Limpiar tags existentes
            if audio_file.tags:
                audio_file.tags.clear()
            else:
                audio_file.tags = {}
            
            tags = audio_file.tags
            
            # Escribir tags
            if metadata.title:
                tags['©nam'] = [metadata.title]
            if metadata.artist:
                tags['©ART'] = [metadata.artist]
            if metadata.album:
                tags['©alb'] = [metadata.album]
            if metadata.albumartist:
                tags['aART'] = [metadata.albumartist]
            if metadata.date:
                tags['©day'] = [metadata.date]
            if metadata.genre:
                tags['©gen'] = [metadata.genre]
            if metadata.composer:
                tags['©wrt'] = [metadata.composer]
            if metadata.comment:
                tags['©cmt'] = [metadata.comment]
            
            # Track number
            if metadata.track:
                try:
                    track_num = int(metadata.track)
                    track_total = int(metadata.track_total) if metadata.track_total else 0
                    tags['trkn'] = [(track_num, track_total)]
                except ValueError:
                    pass
            
            # Disc number
            if metadata.disc:
                try:
                    disc_num = int(metadata.disc)
                    disc_total = int(metadata.disc_total) if metadata.disc_total else 0
                    tags['disk'] = [(disc_num, disc_total)]
                except ValueError:
                    pass
            
            # Artwork
            if metadata.artwork_data:
                from mutagen.mp4 import MP4Cover
                cover_format = MP4Cover.FORMAT_JPEG if metadata.artwork_mime == 'image/jpeg' else MP4Cover.FORMAT_PNG
                tags['covr'] = [MP4Cover(metadata.artwork_data, imageformat=cover_format)]
            
            return True
            
        except Exception as e:
            console.print(f"[red]Error escribiendo tags MP4: {e}[/red]")
            return False

def interactive_mode():
    """Modo interactivo para edición de metadatos"""
    editor = MetadataEditor()
    
    console.print(Panel(
        "[bold blue]Metadata Editor Avanzado[/bold blue]\n" +
        "[dim]Editor profesional de metadatos para archivos de audio[/dim]",
        title="🏷️ Editor de Metadatos"
    ))
    
    while True:
        console.print("\n[cyan]Opciones disponibles:[/cyan]")
        options = [
            "1. Editar archivo individual",
            "2. Edición por lotes", 
            "3. Gestión de plantillas",
            "4. Gestión de carátulas",
            "5. Validar metadatos",
            "6. Salir"
        ]
        
        for option in options:
            console.print(f"  {option}")
        
        choice = Prompt.ask("\nSelecciona una opción", choices=["1", "2", "3", "4", "5", "6"])
        
        if choice == "1":
            _edit_single_file_interactive(editor)
        elif choice == "2":
            console.print("[yellow]Edición por lotes - Funcionalidad en desarrollo[/yellow]")
        elif choice == "3":
            console.print("[yellow]Gestión de plantillas - Funcionalidad en desarrollo[/yellow]")
        elif choice == "4":
            console.print("[yellow]Gestión de carátulas - Funcionalidad en desarrollo[/yellow]")
        elif choice == "5":
            console.print("[yellow]Validación de metadatos - Funcionalidad en desarrollo[/yellow]")
        elif choice == "6":
            console.print("[yellow]¡Hasta luego![/yellow]")
            break

def _edit_single_file_interactive(editor: MetadataEditor):
    """Modo interactivo para editar un archivo individual"""
    
    file_path = Prompt.ask("\nRuta del archivo de audio")
    if not file_path or not Path(file_path).exists():
        console.print("[red]Archivo no encontrado[/red]")
        return
    
    # Leer metadatos existentes
    existing_metadata = editor.read_metadata(file_path)
    if existing_metadata is None:
        console.print("[red]No se pudieron leer los metadatos[/red]")
        return
    
    # Mostrar metadatos actuales
    _display_metadata_table(existing_metadata, f"Metadatos actuales: {Path(file_path).name}")
    
    # Preguntar si quiere editar
    if not Confirm.ask("\n¿Quieres editar estos metadatos?"):
        return
    
    # Crear nueva estructura de metadatos basada en la existente
    new_metadata = AudioMetadata()
    
    # Copiar metadatos existentes
    for field in ['title', 'artist', 'album', 'albumartist', 'date', 'genre', 
                  'track', 'track_total', 'disc', 'disc_total', 'composer', 'comment']:
        current_value = getattr(existing_metadata, field, None)
        setattr(new_metadata, field, current_value)
    
    # Copiar artwork existente
    new_metadata.artwork_data = getattr(existing_metadata, 'artwork_data', None)
    new_metadata.artwork_mime = getattr(existing_metadata, 'artwork_mime', None)
    new_metadata.artwork_description = getattr(existing_metadata, 'artwork_description', None)
    
    console.print("\n[cyan]Editar metadatos (Enter para mantener valor actual):[/cyan]")
    
    # Editar campos principales
    fields_to_edit = [
        ('title', 'Título'),
        ('artist', 'Artista'),
        ('album', 'Álbum'),
        ('albumartist', 'Artista del álbum'),
        ('date', 'Fecha (YYYY)'),
        ('genre', 'Género'),
        ('track', 'Número de track'),
        ('track_total', 'Total de tracks'),
        ('disc', 'Número de disco'),
        ('disc_total', 'Total de discos'),
        ('composer', 'Compositor'),
        ('comment', 'Comentario')
    ]
    
    for field, label in fields_to_edit:
        current_value = getattr(new_metadata, field) or ""
        prompt_text = f"{label}"
        if current_value:
            prompt_text += f" [{current_value}]"
        
        new_value = Prompt.ask(prompt_text, default=current_value or "")
        setattr(new_metadata, field, new_value if new_value else None)
    
    # Manejar carátula
    if Confirm.ask("\n¿Agregar/cambiar carátula?"):
        artwork_path = Prompt.ask("Ruta de la imagen (JPEG/PNG)")
        if artwork_path and Path(artwork_path).exists():
            try:
                # Validar imagen si PIL está disponible
                if PILLOW_AVAILABLE:
                    with Image.open(artwork_path) as img:
                        img.verify()
                
                # Cargar datos de imagen
                with open(artwork_path, 'rb') as f:
                    artwork_data = f.read()
                
                # Determinar tipo MIME
                extension = Path(artwork_path).suffix.lower()
                mime_type = 'image/jpeg' if extension in ['.jpg', '.jpeg'] else 'image/png'
                
                new_metadata.artwork_data = artwork_data
                new_metadata.artwork_mime = mime_type
                new_metadata.artwork_description = "Cover"
                
                console.print("[green]✓ Carátula cargada exitosamente[/green]")
                
            except Exception as e:
                console.print(f"[red]Error cargando carátula: {e}[/red]")
    
    # Mostrar resumen de cambios
    console.print("\n[cyan]Resumen de cambios:[/cyan]")
    changes_made = False
    
    for field in ['title', 'artist', 'album', 'albumartist', 'date', 'genre', 
                  'track', 'track_total', 'disc', 'disc_total', 'composer', 'comment']:
        old_value = getattr(existing_metadata, field, None) or ""
        new_value = getattr(new_metadata, field, None) or ""
        
        if old_value != new_value:
            field_name = field.replace('_', ' ').title()
            console.print(f"  {field_name}: '{old_value}' → '{new_value}'")
            changes_made = True
    
    if new_metadata.artwork_data and not getattr(existing_metadata, 'artwork_data', None):
        console.print("  Carátula: Agregada")
        changes_made = True
    elif new_metadata.artwork_data and getattr(existing_metadata, 'artwork_data', None):
        console.print("  Carátula: Actualizada")
        changes_made = True
    
    if not changes_made:
        console.print("  [yellow]No se realizaron cambios[/yellow]")
        return
    
    # Confirmar guardado
    if Confirm.ask("\n¿Guardar cambios?"):
        if editor.write_metadata(file_path, new_metadata):
            console.print("[green]✓ Metadatos guardados exitosamente[/green]")
            
            # Preguntar si guardar como plantilla
            if Confirm.ask("\n¿Guardar estos metadatos como plantilla?"):
                template_name = Prompt.ask("Nombre de la plantilla")
                if template_name:
                    console.print("[yellow]Funcionalidad de plantillas - En desarrollo[/yellow]")
        else:
            console.print("[red]✗ Error guardando metadatos[/red]")
    else:
        console.print("[yellow]Cambios cancelados[/yellow]")

def _display_metadata_table(metadata: AudioMetadata, title: str):
    """Muestra metadatos en formato tabla"""
    
    table = Table(title=title)
    table.add_column("Campo", style="cyan")
    table.add_column("Valor", style="white")
    
    metadata_dict = metadata.to_dict()
    
    # Excluir artwork data de la visualización
    if 'artwork_data' in metadata_dict:
        del metadata_dict['artwork_data']
        # Mostrar info de carátula si existe
        if getattr(metadata, 'artwork_data', None):
            artwork_mime = getattr(metadata, 'artwork_mime', 'unknown')
            artwork_size = len(metadata.artwork_data)
            table.add_row("Carátula", f"Presente ({artwork_mime}, {artwork_size} bytes)")
    
    if 'artwork_mime' in metadata_dict:
        del metadata_dict['artwork_mime']
    if 'artwork_description' in metadata_dict:
        del metadata_dict['artwork_description']
    
    if metadata_dict:
        for field, value in metadata_dict.items():
            if value:
                display_name = field.replace('_', ' ').title()
                table.add_row(display_name, str(value))
    else:
        table.add_row("[dim]Sin metadatos[/dim]", "[dim]Archivo sin tags[/dim]")
    
    console.print(table)

# Backward compatibility alias for tests
MetadataManager = MetadataEditor

if __name__ == "__main__":
    interactive_mode()
