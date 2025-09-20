"""
Progress Tracker - Utility for tracking progress across different interfaces
Compatible with CLI, Interactive, and Worker progress callbacks
"""

import time
from typing import Optional, Callable, Dict, Any, Union
from dataclasses import dataclass
from enum import Enum

class ProgressStage(Enum):
    """Progress stages for audio processing operations"""
    LOADING = "loading"
    ANALYZING = "analyzing"
    PROCESSING = "processing"
    GENERATING = "generating"
    SAVING = "saving"
    COMPLETE = "complete"
    ERROR = "error"

@dataclass
class ProgressInfo:
    """Progress information structure"""
    current: int
    total: int
    percentage: float
    stage: ProgressStage
    message: str
    timestamp: float
    operation: str = "unknown"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'current': self.current,
            'total': self.total,
            'percentage': self.percentage,
            'stage': self.stage.value,
            'message': self.message,
            'timestamp': self.timestamp,
            'operation': self.operation
        }

class ProgressTracker:
    """
    Universal progress tracker for audio processing operations
    Compatible with CLI, Interactive UI, and Worker callbacks
    """
    
    def __init__(self, operation: str = "audio_processing", 
                 callback: Optional[Callable[[int, int, str], None]] = None):
        self.operation = operation
        self.callback = callback
        self.start_time = time.time()
        self.current_stage = ProgressStage.LOADING
        self.stages_completed = []
        
    def update(self, current: int, total_or_message: Union[int, str] = 100, message: str = "", 
               stage: Optional[ProgressStage] = None):
        """Update progress with current status - flexible API for compatibility"""
        # Handle both APIs: update(current, total, message) and update(current, message)
        if isinstance(total_or_message, str):
            # Old API: update(current, message)
            total = 100
            message = total_or_message
        else:
            # New API: update(current, total, message)
            total = total_or_message
        
        if stage and stage != self.current_stage:
            self.current_stage = stage
            if stage not in self.stages_completed:
                self.stages_completed.append(stage)
        
        percentage = (current / total * 100) if total > 0 else 0
        timestamp = time.time()
        
        # Create progress info
        progress_info = ProgressInfo(
            current=current,
            total=total,
            percentage=percentage,
            stage=self.current_stage,
            message=message,
            timestamp=timestamp,
            operation=self.operation
        )
        
        # Call the callback if provided (for Worker integration)
        if self.callback:
            self.callback(current, total, message)
        
        # Log progress
        elapsed = timestamp - self.start_time
        print(f"[{elapsed:.1f}s] {self.operation}: {percentage:.1f}% - {message}")
        
        return progress_info
    
    def set_stage(self, stage: ProgressStage, message: str = ""):
        """Set current processing stage"""
        self.current_stage = stage
        if message:
            print(f"[{self.operation}] {stage.value.title()}: {message}")
    
    def complete(self, message: str = "Operation completed"):
        """Mark operation as complete"""
        elapsed = time.time() - self.start_time
        self.set_stage(ProgressStage.COMPLETE, f"{message} ({elapsed:.1f}s)")
        
    def error(self, error_message: str):
        """Mark operation as failed"""
        elapsed = time.time() - self.start_time
        self.set_stage(ProgressStage.ERROR, f"Error: {error_message} ({elapsed:.1f}s)")
    
    def start(self, message: str = "Starting operation"):
        """Start the operation tracking"""
        self.start_time = time.time()
        self.set_stage(ProgressStage.LOADING, message)
        print(f"[{self.operation}] {message}")
    
    def finish(self, message: str = "Operation completed"):
        """Finish the operation tracking (alias for complete)"""
        self.complete(message)

class SpectrogramProgressTracker(ProgressTracker):
    """Specialized progress tracker for spectrogram generation"""
    
    def __init__(self, spectrogram_type: str = "mel", 
                 callback: Optional[Callable[[int, int, str], None]] = None):
        super().__init__(f"spectrogram_{spectrogram_type}", callback)
        self.spectrogram_type = spectrogram_type
    
    def start_loading(self, filename: str):
        """Start audio loading phase"""
        self.set_stage(ProgressStage.LOADING, f"Loading audio file: {filename}")
        return self.update(10, 100, f"Loading {filename}")
    
    def start_analyzing(self):
        """Start audio analysis phase"""
        self.set_stage(ProgressStage.ANALYZING, "Analyzing audio properties")
        return self.update(25, 100, "Analyzing frequency content and dynamics")
    
    def start_generating(self):
        """Start spectrogram generation phase"""
        self.set_stage(ProgressStage.GENERATING, f"Generating {self.spectrogram_type} spectrogram")
        return self.update(50, 100, f"Computing {self.spectrogram_type} transformation")
    
    def start_optimizing(self):
        """Start LLM optimization phase"""
        self.set_stage(ProgressStage.PROCESSING, "Optimizing for LLM comprehension")
        return self.update(75, 100, "Applying visual enhancements")
    
    def start_saving(self, output_path: str):
        """Start saving phase"""
        self.set_stage(ProgressStage.SAVING, f"Saving to {output_path}")
        return self.update(90, 100, f"Writing spectrogram image")
    
    def finish(self, output_path: str, file_size_mb: float):
        """Complete spectrogram generation"""
        self.complete(f"Spectrogram saved: {output_path} ({file_size_mb:.1f}MB)")
        return self.update(100, 100, "Spectrogram generation complete")

# Convenience functions for quick progress tracking
def create_progress_tracker(operation: str, callback: Optional[Callable] = None) -> ProgressTracker:
    """Create a standard progress tracker"""
    return ProgressTracker(operation, callback)

def create_spectrogram_tracker(spectrogram_type: str, callback: Optional[Callable] = None) -> SpectrogramProgressTracker:
    """Create a spectrogram-specific progress tracker"""
    return SpectrogramProgressTracker(spectrogram_type, callback)
