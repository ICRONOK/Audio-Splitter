"""
TranslationEngine: Sistema robusto de traducción con fallback automático
Diseñado para backward compatibility absoluta
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional


class TranslationEngine:
    """
    Motor de traducción con fallback automático y backward compatibility
    
    Features:
    - Fallback automático a strings originales
    - Carga lazy de idiomas
    - Cache de traducciones  
    - Soporte para variables en strings
    - Backward compatibility garantizada
    """
    
    def __init__(self, default_language: str = 'es'):
        """
        Inicializar motor de traducción
        
        Args:
            default_language: Idioma por defecto (español = idioma actual)
        """
        self.default_language = default_language
        self.current_language = default_language
        self.translations: Dict[str, Dict] = {}
        self.fallback_mode = True  # CRITICAL: mantiene compatibilidad
        self.languages_dir = Path(__file__).parent / "languages"
        
        # Idiomas soportados
        self.supported_languages = {
            'es': 'Español',
            'en': 'English', 
            'fr': 'Français',
            'de': 'Deutsch',
            'pt': 'Português'
        }
    
    def t(self, key: str, fallback: str = None, **kwargs) -> str:
        """
        Traducir con fallback automático (función principal)
        
        Args:
            key: Clave de traducción (ej: "menu.audio_converter")
            fallback: String original (para backward compatibility)
            **kwargs: Variables para formateo de string
            
        Returns:
            String traducido, fallback o clave original
        """
        
        # Si fallback mode está activado y hay fallback, usarlo
        if self.fallback_mode and fallback:
            try:
                return fallback.format(**kwargs) if kwargs else fallback
            except Exception:
                return fallback
        
        # Buscar traducción
        translation = self.get_translation(key)
        if translation:
            try:
                return translation.format(**kwargs) if kwargs else translation
            except Exception:
                return translation
                
        # Fallback final
        if fallback:
            try:
                return fallback.format(**kwargs) if kwargs else fallback
            except Exception:
                return fallback
                
        return key

    def get_translation(self, key: str) -> Optional[str]:
        """
        Obtener traducción para una clave específica
        
        Args:
            key: Clave de traducción usando dot notation
            
        Returns:
            String traducido o None si no existe
        """
        # Cargar idioma si no está en cache
        if self.current_language not in self.translations:
            self.load_language(self.current_language)
            
        # Navegar por la estructura JSON usando dot notation
        keys = key.split('.')
        value = self.translations.get(self.current_language, {})
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return None
                
        return value if isinstance(value, str) else None

    def load_language(self, language: str) -> bool:
        """
        Cargar archivo de idioma
        
        Args:
            language: Código de idioma (es, en, fr, de, pt)
            
        Returns:
            True si la carga fue exitosa
        """
        if language not in self.supported_languages:
            return False
            
        language_file = self.languages_dir / f"{language}.json"
        
        try:
            if language_file.exists():
                with open(language_file, 'r', encoding='utf-8') as f:
                    self.translations[language] = json.load(f)
                return True
            else:
                # Si no existe el archivo, crear estructura vacía
                self.translations[language] = {}
                return False
        except Exception as e:
            print(f"Error cargando idioma {language}: {e}")
            self.translations[language] = {}
            return False

    def set_language(self, language: str) -> bool:
        """
        Cambiar idioma activo
        
        Args:
            language: Código de idioma
            
        Returns:
            True si el cambio fue exitoso
        """
        if language not in self.supported_languages:
            return False
            
        self.current_language = language
        
        # Cargar idioma si no está en cache
        if language not in self.translations:
            return self.load_language(language)
            
        return True

    def get_current_language(self) -> str:
        """Obtener idioma actual"""
        return self.current_language

    def get_available_languages(self) -> Dict[str, str]:
        """
        Obtener diccionario de idiomas disponibles
        
        Returns:
            Dict con código: nombre de idiomas soportados
        """
        return self.supported_languages.copy()

    def set_fallback_mode(self, enabled: bool):
        """
        Activar/desactivar modo fallback
        
        Args:
            enabled: True para activar fallback automático
        """
        self.fallback_mode = enabled

    def create_language_file_template(self, language: str) -> bool:
        """
        Crear archivo template para un idioma
        
        Args:
            language: Código de idioma
            
        Returns:
            True si se creó exitosamente
        """
        if language not in self.supported_languages:
            return False
            
        language_file = self.languages_dir / f"{language}.json"
        
        # Template básico
        template = {
            "_metadata": {
                "language": language,
                "language_name": self.supported_languages[language],
                "version": "1.0.0",
                "last_updated": "2025-09-23"
            },
            "menu": {
                "title": "🎵 Audio Splitter Suite 2.0",
                "subtitle": "Sistema completo de procesamiento de audio",
                "modules_available": "🎛️ Módulos disponibles:",
                "select_module": "Selecciona un módulo"
            },
            "common": {
                "input_file": "🎧 Archivo de audio de entrada",
                "output_file": "📁 Archivo de salida", 
                "file_not_found": "❌ Archivo no encontrado",
                "success": "✓ Operación exitosa",
                "error": "❌ Error",
                "cancel": "Operación cancelada"
            }
        }
        
        try:
            # Crear directorio si no existe
            self.languages_dir.mkdir(parents=True, exist_ok=True)
            
            with open(language_file, 'w', encoding='utf-8') as f:
                json.dump(template, f, ensure_ascii=False, indent=2)
                
            return True
        except Exception as e:
            print(f"Error creando template para {language}: {e}")
            return False


# Instancia global del translator
translator = TranslationEngine()

# Función de conveniencia
def t(key: str, fallback: str = None, **kwargs) -> str:
    """
    Función global de traducción
    
    Args:
        key: Clave de traducción
        fallback: String de fallback
        **kwargs: Variables para formateo
        
    Returns:
        String traducido
    """
    return translator.t(key, fallback, **kwargs)