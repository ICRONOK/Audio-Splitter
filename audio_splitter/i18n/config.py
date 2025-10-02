"""
Configuración del sistema de internacionalización
Manejo de preferencias de idioma y configuración persistente
"""

import json
import os
from pathlib import Path
from typing import Optional


class I18nConfig:
    """
    Gestiona la configuración de idioma y preferencias i18n
    
    Features:
    - Persistencia de preferencias de idioma
    - Detección automática de idioma del sistema
    - Configuración por usuario
    """
    
    def __init__(self):
        """Inicializar configuración i18n"""
        self.config_dir = Path.home() / ".audio_splitter"
        self.config_file = self.config_dir / "i18n_config.json"
        self.default_config = {
            "language": "es",  # Español por defecto (actual)
            "auto_detect": False,
            "fallback_enabled": True,
            "last_updated": "2025-09-23"
        }
        
    def load_config(self) -> dict:
        """
        Cargar configuración desde archivo
        
        Returns:
            Diccionario con configuración
        """
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # Merge con configuración por defecto
                    return {**self.default_config, **config}
            else:
                return self.default_config.copy()
        except Exception:
            return self.default_config.copy()
    
    def save_config(self, config: dict) -> bool:
        """
        Guardar configuración a archivo
        
        Args:
            config: Diccionario de configuración
            
        Returns:
            True si se guardó exitosamente
        """
        try:
            # Crear directorio si no existe
            self.config_dir.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
                
            return True
        except Exception:
            return False
    
    def get_preferred_language(self) -> str:
        """
        Obtener idioma preferido del usuario
        
        Returns:
            Código de idioma preferido
        """
        config = self.load_config()
        return config.get("language", "es")
    
    def set_preferred_language(self, language: str) -> bool:
        """
        Establecer idioma preferido
        
        Args:
            language: Código de idioma
            
        Returns:
            True si se guardó exitosamente
        """
        config = self.load_config()
        config["language"] = language
        return self.save_config(config)
    
    def detect_system_language(self) -> str:
        """
        Detectar idioma del sistema
        
        Returns:
            Código de idioma detectado o 'es' por defecto
        """
        try:
            # Intentar detectar idioma del sistema
            import locale
            system_locale = locale.getdefaultlocale()[0]
            
            if system_locale:
                # Extraer código de idioma
                lang_code = system_locale.split('_')[0].lower()
                
                # Mapear a idiomas soportados
                supported = ['es', 'en', 'fr', 'de', 'pt']
                if lang_code in supported:
                    return lang_code
                    
        except Exception:
            pass
            
        return "es"  # Fallback a español
    
    def is_first_run(self) -> bool:
        """
        Verificar si es la primera ejecución
        
        Returns:
            True si no existe configuración
        """
        return not self.config_file.exists()
    
    def setup_first_run(self) -> str:
        """
        Configuración para primera ejecución
        
        Returns:
            Idioma configurado
        """
        config = self.default_config.copy()
        
        # Si auto_detect está habilitado, detectar idioma
        if config.get("auto_detect", False):
            detected_lang = self.detect_system_language()
            config["language"] = detected_lang
        
        # Guardar configuración inicial
        self.save_config(config)
        
        return config["language"]


# Instancia global de configuración
i18n_config = I18nConfig()


def get_user_language() -> str:
    """
    Obtener idioma del usuario
    
    Returns:
        Código de idioma preferido
    """
    return i18n_config.get_preferred_language()


def set_user_language(language: str) -> bool:
    """
    Establecer idioma del usuario
    
    Args:
        language: Código de idioma
        
    Returns:
        True si se guardó exitosamente
    """
    return i18n_config.set_preferred_language(language)


def is_first_run() -> bool:
    """
    Verificar si es primera ejecución
    
    Returns:
        True si es primera vez
    """
    return i18n_config.is_first_run()