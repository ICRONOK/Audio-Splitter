#!/usr/bin/env python3
"""
Tests para Professional Workflows
Testing de workflows de Podcast y Music Mastering
"""

import unittest
import sys
from pathlib import Path
import numpy as np
import soundfile as sf

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from audio_splitter.core.workflows.podcast_workflow import (
    create_podcast_workflow,
    create_quick_podcast_workflow,
    get_podcast_template,
    PODCAST_TEMPLATES
)

from audio_splitter.core.workflows.music_workflow import (
    create_music_mastering_workflow,
    create_quick_music_workflow,
    create_mono_mastering_workflow,
    create_stereo_upmix_workflow,
    get_mastering_template,
    MASTERING_TEMPLATES
)


class TestPodcastWorkflow(unittest.TestCase):
    """Tests para Podcast Production Workflow"""

    @classmethod
    def setUpClass(cls):
        """Crear archivo de prueba"""
        cls.test_dir = Path("/tmp/workflow_test")
        cls.test_dir.mkdir(exist_ok=True)

        # Crear audio de prueba (30 segundos, stereo)
        sample_rate = 44100
        duration = 30.0
        t = np.linspace(0, duration, int(sample_rate * duration))
        frequency = 440  # A4

        left = 0.5 * np.sin(2 * np.pi * frequency * t)
        right = 0.5 * np.sin(2 * np.pi * frequency * t * 1.01)  # Ligeramente diferente
        stereo = np.column_stack((left, right))

        cls.test_file = cls.test_dir / "test_podcast.wav"
        sf.write(str(cls.test_file), stereo, sample_rate)

    def test_podcast_workflow_creation(self):
        """Test: Crear workflow de podcast"""
        workflow = create_podcast_workflow(
            input_file=str(self.test_file),
            output_dir=str(self.test_dir / "podcast_output")
        )

        self.assertEqual(workflow.name, "Complete Podcast Production")
        self.assertGreater(len(workflow.steps), 0)

    def test_quick_podcast_workflow(self):
        """Test: Quick podcast workflow"""
        workflow = create_quick_podcast_workflow(
            input_file=str(self.test_file),
            output_dir=str(self.test_dir / "quick_podcast"),
            episode_title="Test Episode",
            host_name="Test Host",
            series_name="Test Series"
        )

        self.assertIsNotNone(workflow)
        self.assertEqual(workflow.context.input_file, str(self.test_file))

    def test_podcast_templates(self):
        """Test: Templates de podcast disponibles"""
        self.assertIn('short_episode', PODCAST_TEMPLATES)
        self.assertIn('standard_episode', PODCAST_TEMPLATES)
        self.assertIn('long_episode', PODCAST_TEMPLATES)

        template = get_podcast_template('standard_episode')
        self.assertIn('segments', template)
        self.assertIn('duration', template)

    def test_podcast_workflow_configuration(self):
        """Test: Configuración del workflow"""
        metadata = {
            'title': 'Test Podcast',
            'artist': 'Test Host',
            'album': 'Test Series'
        }

        workflow = create_podcast_workflow(
            input_file=str(self.test_file),
            output_dir=str(self.test_dir / "configured_podcast"),
            metadata=metadata,
            generate_spectrogram=False,
            quality_validation=False
        )

        self.assertEqual(workflow.context.input_file, str(self.test_file))
        self.assertIsNotNone(workflow.context.output_dir)


class TestMusicMasteringWorkflow(unittest.TestCase):
    """Tests para Music Mastering Workflow"""

    @classmethod
    def setUpClass(cls):
        """Crear archivo de prueba"""
        cls.test_dir = Path("/tmp/workflow_test")
        cls.test_dir.mkdir(exist_ok=True)

        # Crear audio de prueba (5 segundos, stereo)
        sample_rate = 44100
        duration = 5.0
        t = np.linspace(0, duration, int(sample_rate * duration))

        # Signal con contenido musical
        left = 0.6 * np.sin(2 * np.pi * 440 * t)  # A4
        right = 0.6 * np.sin(2 * np.pi * 554 * t)  # C#5
        stereo = np.column_stack((left, right))

        cls.test_file_stereo = cls.test_dir / "test_music_stereo.wav"
        sf.write(str(cls.test_file_stereo), stereo, sample_rate)

        # Crear versión mono
        mono = np.mean(stereo, axis=1)
        cls.test_file_mono = cls.test_dir / "test_music_mono.wav"
        sf.write(str(cls.test_file_mono), mono, sample_rate)

    def test_music_workflow_creation(self):
        """Test: Crear workflow de mastering"""
        workflow = create_music_mastering_workflow(
            input_file=str(self.test_file_stereo),
            output_dir=str(self.test_dir / "music_output")
        )

        self.assertEqual(workflow.name, "Professional Music Mastering")
        self.assertGreater(len(workflow.steps), 0)

    def test_quick_music_workflow(self):
        """Test: Quick music workflow"""
        workflow = create_quick_music_workflow(
            input_file=str(self.test_file_stereo),
            output_dir=str(self.test_dir / "quick_music"),
            track_title="Test Track",
            artist_name="Test Artist",
            album_name="Test Album"
        )

        self.assertIsNotNone(workflow)
        self.assertEqual(workflow.context.input_file, str(self.test_file_stereo))

    def test_music_templates(self):
        """Test: Templates de mastering disponibles"""
        self.assertIn('single_release', MASTERING_TEMPLATES)
        self.assertIn('streaming_optimized', MASTERING_TEMPLATES)
        self.assertIn('vinyl_master', MASTERING_TEMPLATES)
        self.assertIn('mono_radio', MASTERING_TEMPLATES)

        template = get_mastering_template('single_release')
        self.assertIn('include_flac', template)
        self.assertIn('include_mp3', template)

    def test_channel_conversion_workflows(self):
        """Test: Workflows con conversión de canales"""
        # Test mono workflow
        mono_workflow = create_mono_mastering_workflow(
            input_file=str(self.test_file_stereo),
            output_dir=str(self.test_dir / "mono_output"),
            metadata={'title': 'Test Mono'}
        )

        self.assertIsNotNone(mono_workflow)
        # Verificar que tiene step de conversión de canales
        step_names = [step.name for step in mono_workflow.steps]
        self.assertTrue(any('Mono' in name or 'mono' in name for name in step_names))

        # Test stereo upmix workflow
        stereo_workflow = create_stereo_upmix_workflow(
            input_file=str(self.test_file_mono),
            output_dir=str(self.test_dir / "stereo_output"),
            metadata={'title': 'Test Stereo'}
        )

        self.assertIsNotNone(stereo_workflow)
        step_names = [step.name for step in stereo_workflow.steps]
        self.assertTrue(any('Stereo' in name or 'stereo' in name for name in step_names))

    def test_music_workflow_with_channel_options(self):
        """Test: Workflow con opciones de canal"""
        # Sin conversión
        workflow_no_convert = create_music_mastering_workflow(
            input_file=str(self.test_file_stereo),
            output_dir=str(self.test_dir / "no_convert"),
            channel_conversion=None
        )

        # Con conversión a mono
        workflow_to_mono = create_music_mastering_workflow(
            input_file=str(self.test_file_stereo),
            output_dir=str(self.test_dir / "to_mono"),
            channel_conversion="mono",
            mixing_algorithm="downmix_center"
        )

        # Con conversión a stereo
        workflow_to_stereo = create_music_mastering_workflow(
            input_file=str(self.test_file_mono),
            output_dir=str(self.test_dir / "to_stereo"),
            channel_conversion="stereo"
        )

        # Verificar que todos se crearon
        self.assertIsNotNone(workflow_no_convert)
        self.assertIsNotNone(workflow_to_mono)
        self.assertIsNotNone(workflow_to_stereo)

        # Verificar número diferente de steps
        steps_no_convert = len(workflow_no_convert.steps)
        steps_to_mono = len(workflow_to_mono.steps)
        steps_to_stereo = len(workflow_to_stereo.steps)

        # Los workflows con conversión deben tener un step adicional
        self.assertEqual(steps_to_mono, steps_no_convert + 1)
        self.assertEqual(steps_to_stereo, steps_no_convert + 1)


class TestWorkflowIntegration(unittest.TestCase):
    """Tests de integración de workflows"""

    @classmethod
    def setUpClass(cls):
        """Setup común"""
        cls.test_dir = Path("/tmp/workflow_test")
        cls.test_dir.mkdir(exist_ok=True)

    def test_workflow_metadata(self):
        """Test: Metadatos en workflows"""
        metadata = {
            'title': 'Integration Test',
            'artist': 'Test Artist',
            'album': 'Test Album',
            'year': '2025',
            'genre': 'Test'
        }

        workflow = create_music_mastering_workflow(
            input_file="/tmp/test.wav",  # No importa si no existe para este test
            output_dir=str(self.test_dir / "metadata_test"),
            metadata=metadata
        )

        # Verificar que tiene step de metadata
        has_metadata_step = False
        for step in workflow.steps:
            if 'metadata' in step.name.lower():
                has_metadata_step = True
                break

        self.assertTrue(has_metadata_step)

    def test_workflow_quality_options(self):
        """Test: Opciones de calidad en workflows"""
        workflow_pro = create_music_mastering_workflow(
            input_file="/tmp/test.wav",
            output_dir=str(self.test_dir / "pro"),
            quality_profile="professional"
        )

        workflow_studio = create_music_mastering_workflow(
            input_file="/tmp/test.wav",
            output_dir=str(self.test_dir / "studio"),
            quality_profile="studio"
        )

        self.assertIsNotNone(workflow_pro)
        self.assertIsNotNone(workflow_studio)


def run_tests():
    """Ejecutar todos los tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Agregar tests
    suite.addTests(loader.loadTestsFromTestCase(TestPodcastWorkflow))
    suite.addTests(loader.loadTestsFromTestCase(TestMusicMasteringWorkflow))
    suite.addTests(loader.loadTestsFromTestCase(TestWorkflowIntegration))

    # Ejecutar tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
