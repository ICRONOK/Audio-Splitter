#!/usr/bin/env python3
"""
Tests para WorkflowEngine
Testing de sistema de workflows y steps
"""

import unittest
import sys
from pathlib import Path
from typing import Dict, Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from audio_splitter.core.workflow_engine import (
    WorkflowEngine,
    WorkflowStep,
    WorkflowContext,
    StepStatus,
    WorkflowError,
    create_workflow
)


class MockSuccessStep(WorkflowStep):
    """Step de prueba que siempre tiene éxito"""

    def __init__(self, name: str = "Mock Success Step"):
        super().__init__(name=name, description="Step de prueba exitoso")
        self.executed = False

    def execute(self, context: WorkflowContext) -> Dict[str, Any]:
        self.executed = True
        context.set_metadata(f"{self.name}_executed", True)
        return {'success': True, 'message': f'{self.name} executed successfully'}


class MockFailStep(WorkflowStep):
    """Step de prueba que siempre falla"""

    def __init__(self, name: str = "Mock Fail Step"):
        super().__init__(name=name, description="Step de prueba que falla")

    def execute(self, context: WorkflowContext) -> Dict[str, Any]:
        raise WorkflowError(f"{self.name} intentionally failed")


class MockOptionalStep(WorkflowStep):
    """Step opcional que puede fallar sin detener workflow"""

    def __init__(self, should_fail: bool = False):
        super().__init__(
            name="Mock Optional Step",
            description="Step opcional de prueba",
            required=False
        )
        self.should_fail = should_fail

    def execute(self, context: WorkflowContext) -> Dict[str, Any]:
        if self.should_fail:
            raise WorkflowError("Optional step failed")
        return {'success': True}


class TestWorkflowEngine(unittest.TestCase):
    """Tests para WorkflowEngine"""

    def test_workflow_creation(self):
        """Test: Crear workflow básico"""
        workflow = create_workflow("Test Workflow", "Testing workflow creation")

        self.assertEqual(workflow.name, "Test Workflow")
        self.assertEqual(workflow.description, "Testing workflow creation")
        self.assertEqual(len(workflow.steps), 0)

    def test_add_steps(self):
        """Test: Agregar steps al workflow"""
        workflow = WorkflowEngine("Test Workflow")
        step1 = MockSuccessStep("Step 1")
        step2 = MockSuccessStep("Step 2")

        workflow.add_step(step1).add_step(step2)

        self.assertEqual(len(workflow.steps), 2)
        self.assertEqual(workflow.steps[0].name, "Step 1")
        self.assertEqual(workflow.steps[1].name, "Step 2")

    def test_configure_workflow(self):
        """Test: Configurar contexto del workflow"""
        workflow = WorkflowEngine("Test Workflow")
        workflow.configure(
            input_file="test.wav",
            output_dir="/tmp/output",
            custom_param="test_value"
        )

        self.assertEqual(workflow.context.input_file, "test.wav")
        self.assertEqual(workflow.context.output_dir, "/tmp/output")
        self.assertEqual(workflow.context.get_metadata("custom_param"), "test_value")

    def test_successful_workflow_execution(self):
        """Test: Ejecutar workflow exitoso"""
        workflow = WorkflowEngine("Success Workflow")
        workflow.add_step(MockSuccessStep("Step 1"))
        workflow.add_step(MockSuccessStep("Step 2"))
        workflow.add_step(MockSuccessStep("Step 3"))

        results = workflow.execute(show_progress=False)

        self.assertTrue(results['success'])
        self.assertEqual(results['completed_steps'], 3)
        self.assertEqual(results['total_steps'], 3)
        self.assertIsNone(results['failed_step'])

    def test_failed_workflow_execution(self):
        """Test: Workflow que falla en un step"""
        workflow = WorkflowEngine("Failing Workflow")
        workflow.add_step(MockSuccessStep("Step 1"))
        workflow.add_step(MockFailStep("Failing Step"))
        workflow.add_step(MockSuccessStep("Step 3"))  # No debería ejecutarse

        results = workflow.execute(show_progress=False)

        self.assertFalse(results['success'])
        self.assertEqual(results['completed_steps'], 1)  # Solo el primero
        self.assertEqual(results['failed_step'], "Failing Step")

    def test_optional_step_failure_continues(self):
        """Test: Step opcional que falla no detiene workflow"""
        workflow = WorkflowEngine("Optional Step Workflow")
        workflow.add_step(MockSuccessStep("Step 1"))
        workflow.add_step(MockOptionalStep(should_fail=True))  # Falla pero opcional
        workflow.add_step(MockSuccessStep("Step 3"))

        results = workflow.execute(show_progress=False)

        # El workflow debe completarse a pesar del fallo opcional
        self.assertTrue(results['success'])
        self.assertEqual(results['completed_steps'], 3)

    def test_context_sharing_between_steps(self):
        """Test: Compartir datos entre steps via contexto"""
        workflow = WorkflowEngine("Context Sharing Workflow")
        step1 = MockSuccessStep("Step 1")
        step2 = MockSuccessStep("Step 2")
        workflow.add_step(step1).add_step(step2)

        results = workflow.execute(show_progress=False)

        # Verificar que ambos steps escribieron al contexto
        self.assertTrue(workflow.context.get_metadata("Step 1_executed"))
        self.assertTrue(workflow.context.get_metadata("Step 2_executed"))

    def test_step_status_tracking(self):
        """Test: Tracking de estados de steps"""
        workflow = WorkflowEngine("Status Tracking Workflow")
        step1 = MockSuccessStep("Step 1")
        step2 = MockSuccessStep("Step 2")
        workflow.add_step(step1).add_step(step2)

        # Antes de ejecución
        self.assertEqual(step1.status, StepStatus.PENDING)
        self.assertEqual(step2.status, StepStatus.PENDING)

        # Después de ejecución
        workflow.execute(show_progress=False)

        self.assertEqual(step1.status, StepStatus.COMPLETED)
        self.assertEqual(step2.status, StepStatus.COMPLETED)

    def test_workflow_duration_tracking(self):
        """Test: Tracking de duración del workflow"""
        workflow = WorkflowEngine("Duration Tracking Workflow")
        workflow.add_step(MockSuccessStep("Step 1"))

        results = workflow.execute(show_progress=False)

        self.assertIn('duration', results)
        self.assertIsInstance(results['duration'], float)
        self.assertGreater(results['duration'], 0)

    def test_step_duration_tracking(self):
        """Test: Tracking de duración de steps individuales"""
        workflow = WorkflowEngine("Step Duration Workflow")
        step = MockSuccessStep("Timed Step")
        workflow.add_step(step)

        workflow.execute(show_progress=False)

        duration = step.get_duration()
        self.assertIsNotNone(duration)
        self.assertIsInstance(duration, float)
        self.assertGreater(duration, 0)


class TestWorkflowContext(unittest.TestCase):
    """Tests para WorkflowContext"""

    def test_context_creation(self):
        """Test: Crear contexto"""
        context = WorkflowContext()

        self.assertIsNone(context.input_file)
        self.assertIsNone(context.output_dir)
        self.assertEqual(len(context.intermediate_files), 0)
        self.assertIsNotNone(context.quality_settings)

    def test_context_with_initial_values(self):
        """Test: Crear contexto con valores iniciales"""
        context = WorkflowContext(
            input_file="test.wav",
            output_dir="/tmp/output"
        )

        self.assertEqual(context.input_file, "test.wav")
        self.assertEqual(context.output_dir, "/tmp/output")

    def test_intermediate_files_management(self):
        """Test: Gestión de archivos intermedios"""
        context = WorkflowContext()

        context.add_intermediate_file("converted", "converted.mp3")
        context.add_intermediate_file("split_1", "segment_1.wav")

        self.assertEqual(context.get_intermediate_file("converted"), "converted.mp3")
        self.assertEqual(context.get_intermediate_file("split_1"), "segment_1.wav")
        self.assertIsNone(context.get_intermediate_file("nonexistent"))

    def test_metadata_management(self):
        """Test: Gestión de metadatos"""
        context = WorkflowContext()

        context.set_metadata("artist", "Test Artist")
        context.set_metadata("album", "Test Album")

        self.assertEqual(context.get_metadata("artist"), "Test Artist")
        self.assertEqual(context.get_metadata("album"), "Test Album")
        self.assertEqual(context.get_metadata("nonexistent", "default"), "default")


class TestWorkflowStep(unittest.TestCase):
    """Tests para WorkflowStep base"""

    def test_step_creation(self):
        """Test: Crear step básico"""
        step = MockSuccessStep("Test Step")

        self.assertEqual(step.name, "Test Step")
        self.assertEqual(step.status, StepStatus.PENDING)
        self.assertTrue(step.required)

    def test_step_preconditions(self):
        """Test: Validación de precondiciones"""
        step = MockSuccessStep()
        context = WorkflowContext()

        # Por defecto, precondiciones deben ser válidas
        self.assertTrue(step.validate_preconditions(context))

    def test_step_postconditions(self):
        """Test: Validación de postcondiciones"""
        step = MockSuccessStep()
        context = WorkflowContext()

        # Por defecto, postcondiciones deben ser válidas
        self.assertTrue(step.validate_postconditions(context))


def run_tests():
    """Ejecutar todos los tests"""
    # Crear test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Agregar tests
    suite.addTests(loader.loadTestsFromTestCase(TestWorkflowEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestWorkflowContext))
    suite.addTests(loader.loadTestsFromTestCase(TestWorkflowStep))

    # Ejecutar tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
