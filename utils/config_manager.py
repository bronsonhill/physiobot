"""
Configuration Manager for PhysioBot Realtime Audio
Phase 5 Implementation - UI/UX Enhancement & Configuration
"""

import yaml
import os
from typing import Dict, Any, Optional
import streamlit as st

class ConfigManager:
    """Manages configuration settings for the PhysioBot application"""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as file:
                    return yaml.safe_load(file) or {}
            else:
                return self._get_default_config()
        except Exception as e:
            st.error(f"Error loading configuration: {e}")
            return self._get_default_config()
    
    def save_config(self) -> bool:
        """Save current configuration to YAML file"""
        try:
            with open(self.config_path, 'w') as file:
                yaml.dump(self.config, file, default_flow_style=False, indent=2)
            return True
        except Exception as e:
            st.error(f"Error saving configuration: {e}")
            return False
    
    def get_audio_settings(self) -> Dict[str, Any]:
        """Get audio-specific settings"""
        return self.config.get('audio_settings', {})
    
    def get_conversation_settings(self) -> Dict[str, Any]:
        """Get conversation-specific settings"""
        return self.config.get('conversation_settings', {})
    
    def get_ui_settings(self) -> Dict[str, Any]:
        """Get UI-specific settings"""
        return self.config.get('ui_settings', {})
    
    def get_diagnostics_settings(self) -> Dict[str, Any]:
        """Get diagnostics and testing settings"""
        return self.config.get('diagnostics', {})
    
    def get_system_settings(self) -> Dict[str, Any]:
        """Get system-wide settings"""
        return self.config.get('system', {})
    
    def update_setting(self, category: str, key: str, value: Any) -> bool:
        """Update a specific setting"""
        try:
            if category not in self.config:
                self.config[category] = {}
            self.config[category][key] = value
            return self.save_config()
        except Exception as e:
            st.error(f"Error updating setting: {e}")
            return False
    
    def update_nested_setting(self, category: str, subcategory: str, key: str, value: Any) -> bool:
        """Update a nested setting"""
        try:
            if category not in self.config:
                self.config[category] = {}
            if subcategory not in self.config[category]:
                self.config[category][subcategory] = {}
            self.config[category][subcategory][key] = value
            return self.save_config()
        except Exception as e:
            st.error(f"Error updating nested setting: {e}")
            return False
    
    def get_setting(self, category: str, key: str, default: Any = None) -> Any:
        """Get a specific setting with fallback to default"""
        return self.config.get(category, {}).get(key, default)
    
    def get_nested_setting(self, category: str, subcategory: str, key: str, default: Any = None) -> Any:
        """Get a nested setting with fallback to default"""
        return self.config.get(category, {}).get(subcategory, {}).get(key, default)
    
    def reset_to_defaults(self) -> bool:
        """Reset configuration to default values"""
        self.config = self._get_default_config()
        return self.save_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration settings"""
        return {
            'audio_settings': {
                'voice_type': 'alloy',
                'speech_speed': 1.0,
                'conversation_detection': {
                    'silence_threshold': 2.0,
                    'volume_threshold': 0.1
                },
                'quality_settings': {
                    'sample_rate': 24000,
                    'format': 'pcm16'
                }
            },
            'conversation_settings': {
                'max_duration': 1800,
                'auto_save_interval': 300,
                'connection_timeout': 30,
                'max_responses': 1000
            },
            'ui_settings': {
                'show_live_transcript': True,
                'enable_audio_visualization': True,
                'theme': 'modern',
                'show_progress_indicators': True,
                'enable_keyboard_shortcuts': True
            },
            'cohort_settings': {
                'default_cohort': 'PHYSIO_DEFAULT',
                'enable_multi_cohort': False,
                'instructor_mode': False
            },
            'diagnostics': {
                'enable_performance_monitoring': True,
                'log_audio_quality': True,
                'enable_browser_compatibility_check': True,
                'debug_mode': False
            },
            'system': {
                'database_name': 'physiobot-realtime',
                'session_timeout': 3600,
                'max_concurrent_sessions': 100,
                'enable_analytics': True
            }
        }

# Global configuration instance
config_manager = ConfigManager()