#!/usr/bin/env python3
"""
Tests de integración para Workflows y Batch Processing en Interactive I18n
Verifica la integración completa de las nuevas funcionalidades en el menú principal
"""

import unittest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from audio_splitter.ui.interactive_i18n import (
    run_professional_workflows_i18n,
    run_batch_processing_i18n
)


class TestWorkflowsBatchIntegration(unittest.TestCase):
    """Tests de integración para workflows y batch processing"""

    def test_workflows_import(self):
        """Test 1: Verificar que workflows se pueden importar correctamente"""
        try:
            from audio_splitter.ui.workflow_interface import run_professional_workflows
            self.assertTrue(callable(run_professional_workflows))
        except ImportError as e:
            self.fail(f"Failed to import workflows: {e}")

    def test_batch_import(self):
        """Test 2: Verificar que batch processing se puede importar correctamente"""
        try:
            from audio_splitter.ui.batch_interface import run_batch_processing
            self.assertTrue(callable(run_batch_processing))
        except ImportError as e:
            self.fail(f"Failed to import batch processing: {e}")

    @patch('audio_splitter.ui.interactive_i18n.run_professional_workflows')
    @patch('audio_splitter.ui.interactive_i18n.console')
    def test_workflows_i18n_wrapper(self, mock_console, mock_workflows):
        """Test 3: Verificar que el wrapper de workflows funciona correctamente"""
        # Simular ejecución exitosa
        mock_workflows.return_value = None

        # Ejecutar wrapper
        run_professional_workflows_i18n()

        # Verificar que se llamó a la función principal
        mock_workflows.assert_called_once()

        # Verificar que se mostró el título
        self.assertTrue(mock_console.print.called)

    @patch('audio_splitter.ui.interactive_i18n.run_batch_processing')
    @patch('audio_splitter.ui.interactive_i18n.console')
    def test_batch_i18n_wrapper(self, mock_console, mock_batch):
        """Test 4: Verificar que el wrapper de batch processing funciona correctamente"""
        # Simular ejecución exitosa
        mock_batch.return_value = None

        # Ejecutar wrapper
        run_batch_processing_i18n()

        # Verificar que se llamó a la función principal
        mock_batch.assert_called_once()

        # Verificar que se mostró el título
        self.assertTrue(mock_console.print.called)

    @patch('audio_splitter.ui.interactive_i18n.run_professional_workflows')
    @patch('audio_splitter.ui.interactive_i18n.console')
    def test_workflows_error_handling(self, mock_console, mock_workflows):
        """Test 5: Verificar manejo de errores en workflows wrapper"""
        # Simular error
        mock_workflows.side_effect = Exception("Test error")

        # Ejecutar wrapper (no debería lanzar excepción)
        try:
            run_professional_workflows_i18n()
        except Exception as e:
            self.fail(f"Wrapper should handle exceptions: {e}")

        # Verificar que se mostró mensaje de error
        error_calls = [call for call in mock_console.print.call_args_list
                      if 'Error' in str(call) or 'error' in str(call)]
        self.assertTrue(len(error_calls) > 0, "Should print error message")

    @patch('audio_splitter.ui.interactive_i18n.run_batch_processing')
    @patch('audio_splitter.ui.interactive_i18n.console')
    def test_batch_error_handling(self, mock_console, mock_batch):
        """Test 6: Verificar manejo de errores en batch processing wrapper"""
        # Simular error
        mock_batch.side_effect = Exception("Test error")

        # Ejecutar wrapper (no debería lanzar excepción)
        try:
            run_batch_processing_i18n()
        except Exception as e:
            self.fail(f"Wrapper should handle exceptions: {e}")

        # Verificar que se mostró mensaje de error
        error_calls = [call for call in mock_console.print.call_args_list
                      if 'Error' in str(call) or 'error' in str(call)]
        self.assertTrue(len(error_calls) > 0, "Should print error message")

    def test_i18n_translations_workflows(self):
        """Test 7: Verificar que las traducciones de workflows están en el archivo JSON"""
        import json
        from pathlib import Path

        # Leer directamente el archivo de traducciones
        es_json_path = Path(__file__).parent.parent / "audio_splitter" / "i18n" / "languages" / "es.json"

        with open(es_json_path, 'r', encoding='utf-8') as f:
            translations = json.load(f)

        # Verificar que existe la sección workflows
        self.assertIn('workflows', translations, "workflows section should exist")
        self.assertIn('title', translations['workflows'], "workflows.title should exist")

    def test_i18n_translations_batch(self):
        """Test 8: Verificar que las traducciones de batch están en el archivo JSON"""
        import json
        from pathlib import Path

        # Leer directamente el archivo de traducciones
        es_json_path = Path(__file__).parent.parent / "audio_splitter" / "i18n" / "languages" / "es.json"

        with open(es_json_path, 'r', encoding='utf-8') as f:
            translations = json.load(f)

        # Verificar que existe la sección batch
        self.assertIn('batch', translations, "batch section should exist")
        self.assertIn('title', translations['batch'], "batch.title should exist")

    def test_menu_integration(self):
        """Test 9: Verificar que el menú principal incluye las nuevas opciones"""
        # Importar el módulo interactive_i18n
        import audio_splitter.ui.interactive_i18n as ui_module

        # Verificar que las funciones existen
        self.assertTrue(hasattr(ui_module, 'run_professional_workflows_i18n'))
        self.assertTrue(hasattr(ui_module, 'run_batch_processing_i18n'))

        # Verificar que son callable
        self.assertTrue(callable(ui_module.run_professional_workflows_i18n))
        self.assertTrue(callable(ui_module.run_batch_processing_i18n))


class TestMenuChoiceRouting(unittest.TestCase):
    """Tests de routing del menú principal"""

    @patch('audio_splitter.ui.interactive_i18n.Prompt')
    @patch('audio_splitter.ui.interactive_i18n.run_professional_workflows_i18n')
    @patch('audio_splitter.ui.interactive_i18n.console')
    def test_menu_choice_6_routes_to_workflows(self, mock_console, mock_workflows, mock_prompt):
        """Test 10: Verificar que la opción 6 ejecuta workflows"""
        from audio_splitter.ui.interactive_i18n import interactive_menu_i18n

        # Simular selección de opción 6 (workflows) y luego salir (11)
        mock_prompt.ask.side_effect = ['6', '11']

        # Ejecutar menú
        interactive_menu_i18n()

        # Verificar que se llamó a workflows
        mock_workflows.assert_called_once()

    @patch('audio_splitter.ui.interactive_i18n.Prompt')
    @patch('audio_splitter.ui.interactive_i18n.run_batch_processing_i18n')
    @patch('audio_splitter.ui.interactive_i18n.console')
    def test_menu_choice_7_routes_to_batch(self, mock_console, mock_batch, mock_prompt):
        """Test 11: Verificar que la opción 7 ejecuta batch processing"""
        from audio_splitter.ui.interactive_i18n import interactive_menu_i18n

        # Simular selección de opción 7 (batch) y luego salir (11)
        mock_prompt.ask.side_effect = ['7', '11']

        # Ejecutar menú
        interactive_menu_i18n()

        # Verificar que se llamó a batch processing
        mock_batch.assert_called_once()


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
