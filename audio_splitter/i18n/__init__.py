"""
Sistema de internacionalización para Audio Splitter Suite 2.0
Soporte multiidioma con fallback automático y backward compatibility
"""

from .translator import TranslationEngine, t

__version__ = "1.0.0"
__author__ = "Audio Splitter Suite Team"

# Instancia global del translator
translator = TranslationEngine()

# Función de conveniencia para traducciones
def translate(key: str, fallback: str = None, **kwargs) -> str:
    """
    Función de conveniencia para traducciones
    
    Args:
        key: Clave de traducción (ej: "menu.audio_converter")
        fallback: String original (para backward compatibility)
        **kwargs: Variables para formateo
    
    Returns:
        String traducido o fallback
    """
    return translator.t(key, fallback, **kwargs)

# Configurar idioma por defecto
def set_language(language: str) -> bool:
    """
    Cambiar idioma activo
    
    Args:
        language: Código de idioma (es, en, fr, de, pt)
    
    Returns:
        True si el cambio fue exitoso
    """
    return translator.set_language(language)

def get_current_language() -> str:
    """Obtener idioma actual"""
    return translator.current_language

def get_available_languages() -> list:
    """Obtener lista de idiomas disponibles"""
    return translator.get_available_languages()