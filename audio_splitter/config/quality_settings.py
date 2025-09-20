#!/usr/bin/env python3
"""
Quality Settings Configuration System
Audio Signal Processing Engineer integration

Manages user quality preferences and default settings for enhanced audio processing
"""

import json
import os
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional
from enum import Enum

from ..core.quality_framework import QualityLevel


class QualityProfile(Enum):
    """Predefined quality profiles for different use cases"""
    STUDIO = "studio"           # Maximum quality - professional studio mastering
    PROFESSIONAL = "professional"  # High quality - broadcast/production
    STANDARD = "standard"       # Good quality - consumer electronics
    BASIC = "basic"            # Acceptable quality - web streaming
    CUSTOM = "custom"          # User-defined settings


@dataclass
class QualityPreferences:
    """User quality preferences configuration"""
    
    # Default quality profile
    default_profile: QualityProfile = QualityProfile.PROFESSIONAL
    
    # Quality validation settings
    enable_quality_validation: bool = True
    show_metrics_by_default: bool = False
    fail_on_poor_quality: bool = False
    
    # Threshold customization (advanced users)
    custom_thd_threshold: Optional[float] = None      # Custom THD+N threshold in dB
    custom_snr_threshold: Optional[float] = None      # Custom SNR threshold in dB
    custom_dynamic_range_min: Optional[float] = None  # Custom dynamic range minimum %
    
    # Processing preferences
    prefer_enhanced_algorithms: bool = True           # Use enhanced classes by default
    enable_cross_fade: bool = True                   # Enable cross-fade in splitting
    enable_dithering: bool = True                    # Enable dithering for bit depth reduction
    
    # Performance vs Quality trade-offs
    processing_priority: str = "balanced"            # "speed", "balanced", "quality"
    memory_limit_mb: Optional[int] = None            # Memory usage limit
    
    # Display preferences
    use_emoji_indicators: bool = True                # Show emoji quality indicators
    detailed_performance_stats: bool = False        # Show detailed performance information
    color_coded_quality: bool = True                # Use color coding for quality levels


class QualitySettingsManager:
    """Manages user quality settings and configuration"""
    
    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize quality settings manager
        
        Args:
            config_dir: Custom configuration directory (default: ~/.audio_splitter)
        """
        if config_dir is None:
            self.config_dir = Path.home() / ".audio_splitter"
        else:
            self.config_dir = Path(config_dir)
        
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.config_dir / "quality_settings.json"
        
        # Load or create default settings
        self.preferences = self._load_preferences()
    
    def _load_preferences(self) -> QualityPreferences:
        """Load preferences from configuration file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Convert enum strings back to enums
                if 'default_profile' in data:
                    data['default_profile'] = QualityProfile(data['default_profile'])
                
                return QualityPreferences(**data)
            except (json.JSONDecodeError, ValueError, TypeError) as e:
                # If config is corrupted, use defaults and log warning
                print(f"Warning: Corrupted quality settings, using defaults. Error: {e}")
                return QualityPreferences()
        else:
            # Create default preferences
            return QualityPreferences()
    
    def save_preferences(self) -> bool:
        """Save current preferences to configuration file"""
        try:
            # Convert to dict and handle enums
            data = asdict(self.preferences)
            data['default_profile'] = self.preferences.default_profile.value
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Error saving quality settings: {e}")
            return False
    
    def get_quality_thresholds(self) -> Dict[str, float]:
        """Get quality thresholds based on current profile"""
        profile = self.preferences.default_profile
        
        # Define thresholds for each profile
        profile_thresholds = {
            QualityProfile.STUDIO: {
                'thd_threshold': -80.0,     # Studio mastering quality
                'snr_threshold': 100.0,     # High-end studio equipment
                'dynamic_range_min': 98.0   # Nearly perfect preservation
            },
            QualityProfile.PROFESSIONAL: {
                'thd_threshold': -60.0,     # Professional broadcast quality
                'snr_threshold': 90.0,      # Professional equipment
                'dynamic_range_min': 95.0   # Excellent preservation
            },
            QualityProfile.STANDARD: {
                'thd_threshold': -40.0,     # Consumer electronics quality
                'snr_threshold': 70.0,      # Good consumer equipment
                'dynamic_range_min': 90.0   # Good preservation
            },
            QualityProfile.BASIC: {
                'thd_threshold': -30.0,     # Basic acceptable quality
                'snr_threshold': 60.0,      # Basic equipment
                'dynamic_range_min': 80.0   # Acceptable preservation
            },
            QualityProfile.CUSTOM: {
                'thd_threshold': self.preferences.custom_thd_threshold or -60.0,
                'snr_threshold': self.preferences.custom_snr_threshold or 90.0,
                'dynamic_range_min': self.preferences.custom_dynamic_range_min or 95.0
            }
        }
        
        return profile_thresholds.get(profile, profile_thresholds[QualityProfile.PROFESSIONAL])
    
    def should_use_enhanced_processing(self, command_type: str) -> bool:
        """Determine if enhanced processing should be used for a command"""
        if not self.preferences.prefer_enhanced_algorithms:
            return False
        
        # Additional logic could be added here for specific command types
        return True
    
    def get_processing_config(self) -> Dict[str, Any]:
        """Get processing configuration based on preferences"""
        config = {
            'enable_cross_fade': self.preferences.enable_cross_fade,
            'enable_dithering': self.preferences.enable_dithering,
            'quality_validation': self.preferences.enable_quality_validation,
            'show_metrics': self.preferences.show_metrics_by_default,
            'fail_on_poor_quality': self.preferences.fail_on_poor_quality,
            'processing_priority': self.preferences.processing_priority
        }
        
        if self.preferences.memory_limit_mb:
            config['memory_limit_mb'] = self.preferences.memory_limit_mb
        
        return config
    
    def get_display_config(self) -> Dict[str, Any]:
        """Get display configuration for UI components"""
        return {
            'use_emoji_indicators': self.preferences.use_emoji_indicators,
            'detailed_performance_stats': self.preferences.detailed_performance_stats,
            'color_coded_quality': self.preferences.color_coded_quality
        }
    
    def set_profile(self, profile: QualityProfile) -> bool:
        """Set quality profile"""
        self.preferences.default_profile = profile
        return self.save_preferences()
    
    def set_custom_thresholds(self, thd_threshold: float = None, 
                            snr_threshold: float = None, 
                            dynamic_range_min: float = None) -> bool:
        """Set custom quality thresholds"""
        if thd_threshold is not None:
            self.preferences.custom_thd_threshold = thd_threshold
        if snr_threshold is not None:
            self.preferences.custom_snr_threshold = snr_threshold
        if dynamic_range_min is not None:
            self.preferences.custom_dynamic_range_min = dynamic_range_min
        
        # Automatically switch to custom profile when setting custom thresholds
        self.preferences.default_profile = QualityProfile.CUSTOM
        
        return self.save_preferences()
    
    def reset_to_defaults(self) -> bool:
        """Reset all preferences to default values"""
        self.preferences = QualityPreferences()
        return self.save_preferences()
    
    def export_settings(self, export_path: Path) -> bool:
        """Export settings to a file for sharing/backup"""
        try:
            data = asdict(self.preferences)
            data['default_profile'] = self.preferences.default_profile.value
            data['_export_version'] = "1.0"
            data['_export_source'] = "Audio Splitter Suite 2.0"
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Error exporting settings: {e}")
            return False
    
    def import_settings(self, import_path: Path) -> bool:
        """Import settings from a file"""
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Remove export metadata
            data.pop('_export_version', None)
            data.pop('_export_source', None)
            
            # Convert enum strings back to enums
            if 'default_profile' in data:
                data['default_profile'] = QualityProfile(data['default_profile'])
            
            self.preferences = QualityPreferences(**data)
            return self.save_preferences()
        except Exception as e:
            print(f"Error importing settings: {e}")
            return False


# Global settings manager instance
_settings_manager = None

def get_quality_settings() -> QualitySettingsManager:
    """Get the global quality settings manager instance"""
    global _settings_manager
    if _settings_manager is None:
        _settings_manager = QualitySettingsManager()
    return _settings_manager


def apply_user_preferences_to_args(args, command_type: str):
    """Apply user preferences to command arguments"""
    settings = get_quality_settings()
    config = settings.get_processing_config()
    
    # Apply quality validation preferences if not explicitly set
    if not hasattr(args, 'quality_validation') or args.quality_validation is None:
        args.quality_validation = config['quality_validation']
    
    if not hasattr(args, 'show_metrics') or args.show_metrics is None:
        args.show_metrics = config['show_metrics']
    
    # Apply enhanced processing preferences
    if command_type in ['convert', 'split', 'spectrogram']:
        if not hasattr(args, 'enhanced') or args.enhanced is None:
            args.enhanced = settings.should_use_enhanced_processing(command_type)
    
    # Apply processing-specific preferences
    if command_type == 'split':
        if not hasattr(args, 'fade_enabled') or args.fade_enabled is None:
            args.fade_enabled = config['enable_cross_fade']
        if not hasattr(args, 'dither_enabled') or args.dither_enabled is None:
            args.dither_enabled = config['enable_dithering']
    
    return args