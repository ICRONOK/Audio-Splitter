#!/usr/bin/env python3
"""
Workflow Engine - Sistema de automatización de procesos complejos
Permite encadenar operaciones de audio en workflows profesionales

Workflows soportados:
- Complete Podcast Production
- Professional Music Mastering
- Custom workflows definidos por usuario
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import time
from datetime import datetime

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn
from rich.table import Table
from rich.panel import Panel

# Imports relativos con fallback
try:
    from ..config.quality_settings import get_quality_settings
    from ..core.enhanced_converter import EnhancedAudioConverter
    from ..core.enhanced_splitter import EnhancedAudioSplitter
    from ..core.enhanced_spectrogram import EnhancedSpectrogramGenerator
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from config.quality_settings import get_quality_settings
    from core.enhanced_converter import EnhancedAudioConverter
    from core.enhanced_splitter import EnhancedAudioSplitter
    from core.enhanced_spectrogram import EnhancedSpectrogramGenerator

console = Console()


class StepStatus(Enum):
    """Estados posibles de un step del workflow"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ROLLED_BACK = "rolled_back"


class WorkflowError(Exception):
    """Excepción personalizada para errores de workflow"""
    pass


@dataclass
class WorkflowContext:
    """
    Contexto compartido entre steps del workflow
    Permite pasar datos y configuración entre steps
    """
    input_file: Optional[str] = None
    output_dir: Optional[str] = None
    intermediate_files: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    quality_settings: Optional[Any] = None
    start_time: Optional[datetime] = None

    def __post_init__(self):
        if self.start_time is None:
            self.start_time = datetime.now()
        if self.quality_settings is None:
            self.quality_settings = get_quality_settings()

    def add_intermediate_file(self, key: str, filepath: str):
        """Registrar archivo intermedio generado por un step"""
        self.intermediate_files[key] = filepath

    def get_intermediate_file(self, key: str) -> Optional[str]:
        """Obtener archivo intermedio generado por step previo"""
        return self.intermediate_files.get(key)

    def set_metadata(self, key: str, value: Any):
        """Establecer metadato del workflow"""
        self.metadata[key] = value

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Obtener metadato del workflow"""
        return self.metadata.get(key, default)


class WorkflowStep:
    """
    Step base para workflows
    Cada step representa una operación atómica del workflow
    """

    def __init__(self,
                 name: str,
                 description: str = "",
                 required: bool = True,
                 timeout: Optional[int] = None):
        self.name = name
        self.description = description or name
        self.required = required
        self.timeout = timeout
        self.status = StepStatus.PENDING
        self.error_message: Optional[str] = None
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None

    def validate_preconditions(self, context: WorkflowContext) -> bool:
        """
        Validar que las precondiciones para ejecutar el step se cumplan
        Override en subclases para implementar validaciones específicas
        """
        return True

    def execute(self, context: WorkflowContext) -> Dict[str, Any]:
        """
        Ejecutar el step del workflow
        Override en subclases para implementar lógica específica

        Returns:
            Dict con resultados del step
        """
        raise NotImplementedError("Subclass must implement execute()")

    def rollback(self, context: WorkflowContext):
        """
        Revertir cambios realizados por este step
        Override en subclases si el step requiere rollback
        """
        pass

    def validate_postconditions(self, context: WorkflowContext) -> bool:
        """
        Validar que el step se ejecutó correctamente
        Override en subclases para implementar validaciones específicas
        """
        return True

    def get_duration(self) -> Optional[float]:
        """Obtener duración de ejecución del step en segundos"""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None

    def __str__(self) -> str:
        return f"WorkflowStep({self.name}, status={self.status.value})"


class WorkflowEngine:
    """
    Motor de ejecución de workflows
    Orquesta la ejecución de steps con progress tracking y error handling
    """

    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description or name
        self.steps: List[WorkflowStep] = []
        self.context = WorkflowContext()
        self.executed_steps: List[WorkflowStep] = []
        self.failed_step: Optional[WorkflowStep] = None

    def add_step(self, step: WorkflowStep) -> 'WorkflowEngine':
        """
        Agregar step al workflow
        Permite chaining: engine.add_step(step1).add_step(step2)
        """
        self.steps.append(step)
        return self

    def configure(self,
                  input_file: Optional[str] = None,
                  output_dir: Optional[str] = None,
                  **kwargs) -> 'WorkflowEngine':
        """
        Configurar contexto del workflow
        """
        if input_file:
            self.context.input_file = input_file
        if output_dir:
            self.context.output_dir = output_dir

        for key, value in kwargs.items():
            self.context.set_metadata(key, value)

        return self

    def execute(self, show_progress: bool = True) -> Dict[str, Any]:
        """
        Ejecutar workflow completo con progress tracking

        Returns:
            Dict con resultados del workflow
        """
        console.print(f"\n[bold cyan]🚀 Ejecutando Workflow: {self.name}[/bold cyan]")
        if self.description:
            console.print(f"[dim]{self.description}[/dim]")

        results = {
            'success': False,
            'workflow_name': self.name,
            'total_steps': len(self.steps),
            'completed_steps': 0,
            'failed_step': None,
            'duration': 0.0,
            'step_results': {}
        }

        workflow_start = time.time()

        if show_progress:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TimeRemainingColumn(),
                console=console
            ) as progress:
                task = progress.add_task(
                    f"[cyan]Workflow: {self.name}",
                    total=len(self.steps)
                )

                for i, step in enumerate(self.steps, 1):
                    progress.update(task, description=f"[cyan]{i}/{len(self.steps)}: {step.description}")

                    step_result = self._execute_step(step)
                    results['step_results'][step.name] = step_result

                    if step_result['success']:
                        results['completed_steps'] += 1
                        progress.advance(task)
                    else:
                        results['failed_step'] = step.name
                        self.failed_step = step
                        break
        else:
            for step in self.steps:
                step_result = self._execute_step(step)
                results['step_results'][step.name] = step_result

                if step_result['success']:
                    results['completed_steps'] += 1
                else:
                    results['failed_step'] = step.name
                    self.failed_step = step
                    break

        workflow_duration = time.time() - workflow_start
        results['duration'] = workflow_duration
        results['success'] = results['completed_steps'] == len(self.steps)

        # Mostrar resumen
        self._display_summary(results)

        return results

    def _execute_step(self, step: WorkflowStep) -> Dict[str, Any]:
        """
        Ejecutar un step individual con validaciones y error handling
        """
        result = {
            'success': False,
            'step_name': step.name,
            'duration': 0.0,
            'error': None
        }

        try:
            # Validar precondiciones
            if not step.validate_preconditions(self.context):
                raise WorkflowError(f"Preconditions not met for step: {step.name}")

            # Ejecutar step
            step.status = StepStatus.RUNNING
            step.start_time = time.time()

            step_output = step.execute(self.context)

            step.end_time = time.time()
            result['duration'] = step.get_duration()

            # Validar postcondiciones
            if not step.validate_postconditions(self.context):
                raise WorkflowError(f"Postconditions not met for step: {step.name}")

            step.status = StepStatus.COMPLETED
            self.executed_steps.append(step)
            result['success'] = True
            result['output'] = step_output

        except Exception as e:
            step.status = StepStatus.FAILED
            step.error_message = str(e)
            result['error'] = str(e)

            console.print(f"[red]❌ Step failed: {step.name}[/red]")
            console.print(f"[red]Error: {str(e)}[/red]")

            # Si el step no es requerido, marcarlo como skipped y continuar
            if not step.required:
                step.status = StepStatus.SKIPPED
                console.print(f"[yellow]⚠️ Step {step.name} skipped (not required)[/yellow]")
                result['success'] = True

        return result

    def rollback(self):
        """
        Revertir todos los steps ejecutados en orden inverso
        """
        console.print(f"\n[yellow]🔄 Ejecutando rollback del workflow: {self.name}[/yellow]")

        for step in reversed(self.executed_steps):
            try:
                console.print(f"[dim]Revertiendo step: {step.name}[/dim]")
                step.rollback(self.context)
                step.status = StepStatus.ROLLED_BACK
            except Exception as e:
                console.print(f"[red]Error en rollback de {step.name}: {str(e)}[/red]")

    def _display_summary(self, results: Dict[str, Any]):
        """Mostrar resumen de ejecución del workflow"""
        console.print("\n" + "="*60)

        if results['success']:
            console.print(f"[bold green]✓ Workflow completado exitosamente: {self.name}[/bold green]")
        else:
            console.print(f"[bold red]✗ Workflow fallido: {self.name}[/bold red]")
            if results['failed_step']:
                console.print(f"[red]Step fallido: {results['failed_step']}[/red]")

        # Tabla de resumen
        table = Table(title="Resumen del Workflow", show_header=True, header_style="bold cyan")
        table.add_column("Métrica", style="white", width=30)
        table.add_column("Valor", style="green", width=20)

        table.add_row("Steps completados", f"{results['completed_steps']}/{results['total_steps']}")
        table.add_row("Duración total", f"{results['duration']:.2f}s")
        table.add_row("Estado", "✅ Exitoso" if results['success'] else "❌ Fallido")

        console.print(table)
        console.print("="*60 + "\n")


# Funciones helper para crear workflows comunes
def create_workflow(name: str, description: str = "") -> WorkflowEngine:
    """
    Factory function para crear workflows
    """
    return WorkflowEngine(name, description)


if __name__ == "__main__":
    # Testing básico del engine
    console.print("[cyan]Testing WorkflowEngine...[/cyan]")

    # Crear workflow de prueba
    workflow = create_workflow(
        "Test Workflow",
        "Workflow simple para testing del engine"
    )

    console.print("✅ WorkflowEngine creado exitosamente")
