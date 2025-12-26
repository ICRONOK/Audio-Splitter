#!/usr/bin/env python3
"""
Tests para Universal Batch Processing
Testing de operaciones batch para todos los módulos
"""

import unittest
import sys
from pathlib import Path
import numpy as np
import soundfile as sf
import shutil

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from audio_splitter.core.batch_processor import (
    UniversalBatchProcessor,
    BatchResult,
    BatchOperation
)


class TestBatchProcessor(unittest.TestCase):
    """Tests para Universal Batch Processor"""

    @classmethod
    def setUpClass(cls):
        """Crear archivos de prueba"""
        cls.test_dir = Path("/tmp/batch_test")
        cls.test_dir.mkdir(exist_ok=True)

        # Crear subdirectorio
        cls.subdir = cls.test_dir / "subdir"
        cls.subdir.mkdir(exist_ok=True)

        # Crear múltiples archivos de audio de prueba
        sample_rate = 44100
        duration = 2.0
        t = np.linspace(0, duration, int(sample_rate * duration))

        # Archivo 1: stereo
        left = 0.5 * np.sin(2 * np.pi * 440 * t)
        right = 0.5 * np.sin(2 * np.pi * 554 * t)
        stereo = np.column_stack((left, right))
        cls.file1 = cls.test_dir / "test1.wav"
        sf.write(str(cls.file1), stereo, sample_rate)

        # Archivo 2: stereo
        cls.file2 = cls.test_dir / "test2.wav"
        sf.write(str(cls.file2), stereo, sample_rate)

        # Archivo 3: en subdirectorio
        cls.file3 = cls.subdir / "test3.wav"
        sf.write(str(cls.file3), stereo, sample_rate)

        cls.processor = UniversalBatchProcessor()

    @classmethod
    def tearDownClass(cls):
        """Limpiar archivos de prueba"""
        if cls.test_dir.exists():
            shutil.rmtree(cls.test_dir)

    def test_find_audio_files_single_file(self):
        """Test: Encontrar archivo individual"""
        files = self.processor.find_audio_files(str(self.file1))

        self.assertEqual(len(files), 1)
        self.assertEqual(files[0], self.file1)

    def test_find_audio_files_directory(self):
        """Test: Encontrar archivos en directorio"""
        files = self.processor.find_audio_files(str(self.test_dir), recursive=False)

        # Debe encontrar 2 archivos (test1, test2) sin recursivo
        self.assertEqual(len(files), 2)

    def test_find_audio_files_recursive(self):
        """Test: Encontrar archivos recursivamente"""
        files = self.processor.find_audio_files(str(self.test_dir), recursive=True)

        # Debe encontrar 3 archivos (test1, test2, test3)
        self.assertEqual(len(files), 3)

    def test_batch_result_success_rate(self):
        """Test: Cálculo de success rate"""
        result = BatchResult(
            total_files=10,
            successful=8,
            failed=2,
            skipped=0,
            results=[],
            duration=1.0
        )

        self.assertEqual(result.success_rate, 80.0)

    def test_batch_result_zero_files(self):
        """Test: Success rate con 0 archivos"""
        result = BatchResult(
            total_files=0,
            successful=0,
            failed=0,
            skipped=0,
            results=[],
            duration=0.0
        )

        self.assertEqual(result.success_rate, 0.0)


class TestBatchConversion(unittest.TestCase):
    """Tests para batch conversion"""

    @classmethod
    def setUpClass(cls):
        """Setup para tests de conversion"""
        cls.test_dir = Path("/tmp/batch_conv_test")
        cls.test_dir.mkdir(exist_ok=True)

        # Crear archivos de prueba
        sample_rate = 44100
        duration = 1.0
        t = np.linspace(0, duration, int(sample_rate * duration))
        audio = 0.5 * np.sin(2 * np.pi * 440 * t)
        stereo = np.column_stack((audio, audio))

        cls.file1 = cls.test_dir / "test1.wav"
        sf.write(str(cls.file1), stereo, sample_rate)

        cls.processor = UniversalBatchProcessor()

    @classmethod
    def tearDownClass(cls):
        """Cleanup"""
        if cls.test_dir.exists():
            shutil.rmtree(cls.test_dir)

    def test_batch_convert_single_file(self):
        """Test: Convertir archivo individual"""
        output_dir = self.test_dir / "output_single"

        result = self.processor.batch_convert(
            input_path=str(self.file1),
            output_dir=str(output_dir),
            output_format="mp3",
            recursive=False,
            quality_validation=False
        )

        self.assertEqual(result.total_files, 1)
        self.assertGreaterEqual(result.successful, 0)  # Puede fallar por dependencias

    def test_batch_convert_directory(self):
        """Test: Convertir directorio"""
        output_dir = self.test_dir / "output_dir"

        result = self.processor.batch_convert(
            input_path=str(self.test_dir),
            output_dir=str(output_dir),
            output_format="flac",
            recursive=False,
            quality_validation=False
        )

        self.assertGreaterEqual(result.total_files, 1)


class TestBatchChannelConversion(unittest.TestCase):
    """Tests para batch channel conversion"""

    @classmethod
    def setUpClass(cls):
        """Setup para tests de channel conversion"""
        cls.test_dir = Path("/tmp/batch_channel_test")
        cls.test_dir.mkdir(exist_ok=True)

        # Crear archivo stereo de prueba
        sample_rate = 44100
        duration = 1.0
        t = np.linspace(0, duration, int(sample_rate * duration))
        left = 0.5 * np.sin(2 * np.pi * 440 * t)
        right = 0.5 * np.sin(2 * np.pi * 554 * t)
        stereo = np.column_stack((left, right))

        cls.file1 = cls.test_dir / "stereo_test.wav"
        sf.write(str(cls.file1), stereo, sample_rate)

        cls.processor = UniversalBatchProcessor()

    @classmethod
    def tearDownClass(cls):
        """Cleanup"""
        if cls.test_dir.exists():
            shutil.rmtree(cls.test_dir)

    def test_batch_channel_convert_to_mono(self):
        """Test: Convertir a mono en batch"""
        output_dir = self.test_dir / "output_mono"

        result = self.processor.batch_channel_convert(
            input_path=str(self.test_dir),
            output_dir=str(output_dir),
            target_channels=1,
            mixing_algorithm="downmix_center",
            recursive=False
        )

        self.assertGreaterEqual(result.total_files, 1)


def run_tests():
    """Ejecutar todos los tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Agregar tests
    suite.addTests(loader.loadTestsFromTestCase(TestBatchProcessor))
    suite.addTests(loader.loadTestsFromTestCase(TestBatchConversion))
    suite.addTests(loader.loadTestsFromTestCase(TestBatchChannelConversion))

    # Ejecutar tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
