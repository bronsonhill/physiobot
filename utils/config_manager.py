import yaml
import os
from typing import Dict, Any, Optional
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Global instance cache
_config_manager_instance = None

def get_config_manager(config_path: str = "config.yaml") -> 'ConfigManager':
    """
    Get a cached ConfigManager instance.
    
    Args:
        config_path: Path to the configuration file
        
    Returns:
        ConfigManager instance
    """
    global _config_manager_instance
    if _config_manager_instance is None:
        _config_manager_instance = ConfigManager(config_path)
    return _config_manager_instance

class ConfigManager:
    """Configuration manager for physiobot-realtime application."""
    
    _instance = None
    _initialized = False
    
    def __new__(cls, config_path: str = "config.yaml"):
        """Implement singleton pattern."""
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize configuration manager.
        
        Args:
            config_path: Path to the configuration file
        """
        # Only initialize once
        if not self._initialized:
            self.config_path = Path(config_path)
            self.config = self.load_config()
            ConfigManager._initialized = True
    
    def load_config(self) -> Dict[str, Any]:
        """
        Load configuration from YAML file.
        
        Returns:
            Dictionary containing configuration settings
        """
        try:
            if not self.config_path.exists():
                logger.warning(f"Configuration file {self.config_path} not found. Using defaults.")
                return self._get_default_config()
            
            with open(self.config_path, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
                logger.info(f"Configuration loaded from {self.config_path}")
                return config
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            return self._get_default_config()
    
    def save_config(self) -> bool:
        """
        Save current configuration to file.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(self.config_path, 'w', encoding='utf-8') as file:
                yaml.dump(self.config, file, default_flow_style=False, indent=2)
                logger.info(f"Configuration saved to {self.config_path}")
                return True
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            return False
    
    def get_audio_settings(self) -> Dict[str, Any]:
        """Get audio configuration settings."""
        return self.config.get('audio_settings', {})
    
    def get_conversation_settings(self) -> Dict[str, Any]:
        """Get conversation configuration settings."""
        return self.config.get('conversation_settings', {})
    
    def get_ui_settings(self) -> Dict[str, Any]:
        """Get UI configuration settings."""
        return self.config.get('ui_settings', {})
    
    def get_database_settings(self) -> Dict[str, Any]:
        """Get database configuration settings."""
        return self.config.get('database_settings', {})
    
    def get_openai_realtime_settings(self) -> Dict[str, Any]:
        """Get OpenAI Realtime API configuration settings."""
        return self.config.get('openai_realtime', {})
    
    def get_cohort_settings(self) -> Dict[str, Any]:
        """Get cohort configuration settings."""
        return self.config.get('cohort_settings', {})
    
    def update_setting(self, key: str, value: Any) -> bool:
        """
        Update a configuration setting.
        
        Args:
            key: Setting key in dot notation (e.g., 'audio_settings.voice_type')
            value: New value for the setting
            
        Returns:
            True if successful, False otherwise
        """
        try:
            keys = key.split('.')
            config_section = self.config
            
            # Navigate to the parent section
            for k in keys[:-1]:
                if k not in config_section:
                    config_section[k] = {}
                config_section = config_section[k]
            
            # Update the final key
            config_section[keys[-1]] = value
            logger.info(f"Updated setting {key} = {value}")
            return True
        except Exception as e:
            logger.error(f"Error updating setting {key}: {e}")
            return False
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration setting using dot notation.
        
        Args:
            key: Setting key in dot notation (e.g., 'audio_settings.voice_type')
            default: Default value if key not found
            
        Returns:
            Setting value or default
        """
        try:
            keys = key.split('.')
            value = self.config
            
            for k in keys:
                value = value[k]
            
            return value
        except (KeyError, TypeError):
            return default
    
    def validate_config(self) -> Dict[str, list]:
        """
        Validate configuration settings.
        
        Returns:
            Dictionary with validation errors grouped by section
        """
        errors = {}
        
        # Validate audio settings
        audio_errors = self._validate_audio_settings()
        if audio_errors:
            errors['audio_settings'] = audio_errors
        
        # Validate conversation settings
        conversation_errors = self._validate_conversation_settings()
        if conversation_errors:
            errors['conversation_settings'] = conversation_errors
        
        return errors
    
    def _validate_audio_settings(self) -> list:
        """Validate audio configuration settings."""
        errors = []
        audio_settings = self.get_audio_settings()
        
        # Validate voice type
        valid_voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
        voice_type = audio_settings.get('voice_type')
        if voice_type and voice_type not in valid_voices:
            errors.append(f"Invalid voice_type: {voice_type}. Must be one of {valid_voices}")
        
        # Validate speech speed
        speech_speed = audio_settings.get('speech_speed')
        if speech_speed and not (0.25 <= speech_speed <= 4.0):
            errors.append(f"Invalid speech_speed: {speech_speed}. Must be between 0.25 and 4.0")
        
        return errors
    
    def _validate_conversation_settings(self) -> list:
        """Validate conversation configuration settings."""
        errors = []
        conversation_settings = self.get_conversation_settings()
        
        # Validate max_duration
        max_duration = conversation_settings.get('max_duration')
        if max_duration and max_duration <= 0:
            errors.append(f"Invalid max_duration: {max_duration}. Must be positive")
        
        # Validate connection_timeout
        timeout = conversation_settings.get('connection_timeout')
        if timeout and timeout <= 0:
            errors.append(f"Invalid connection_timeout: {timeout}. Must be positive")
        
        return errors
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration if config file is not available."""
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
                'max_responses': 50
            },
            'ui_settings': {
                'show_live_transcript': True,
                'enable_audio_visualization': True,
                'theme': 'light'
            },
            'database_settings': {
                'database_name': 'physiobot-realtime',
                'collections': {
                    'cohorts': 'cohorts',
                    'valid_identifiers': 'valid_identifiers',
                    'audio_transcripts': 'audio_transcripts',
                    'instructors': 'instructors'
                }
            }
        }