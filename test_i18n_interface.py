#!/usr/bin/env python3
"""
Script de prueba para la interfaz interactiva multiidioma
"""

import sys
from pathlib import Path

# Asegurar que el módulo esté en el path
sys.path.insert(0, str(Path(__file__).parent))

from audio_splitter.ui.interactive_i18n import interactive_menu_i18n

if __name__ == "__main__":
    print("🚀 Iniciando Audio Splitter Suite 2.0 - Interfaz Multiidioma")
    print("=" * 60)
    
    try:
        interactive_menu_i18n()
    except KeyboardInterrupt:
        print("\n\n👋 Salida manual detectada. ¡Hasta luego!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Verifica que todas las dependencias estén instaladas.")