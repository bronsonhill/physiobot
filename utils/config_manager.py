import yaml
import os
from typing import Dict, Any, Optional
import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

class ConfigManager:
    """Configuration manager for physiobot-realtime application."""
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize configuration manager.
        
        Args:
            config_path: Path to the configuration file
        """
        self.config_path = Path(config_path)
        self.config = self.load_config()
    
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
    
    def update_config(self, new_config: Dict[str, Any]) -> bool:
        """
        Update configuration with new settings and save to file.
        
        Args:
            new_config: Dictionary containing configuration updates
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Deep merge the new configuration with existing configuration
            self.config = self._deep_merge(self.config, new_config)
            
            # Validate the updated configuration
            validation_errors = self.validate_config()
            if validation_errors:
                error_msg = "Configuration validation failed:\n"
                for section, errors in validation_errors.items():
                    error_msg += f"{section}: {', '.join(errors)}\n"
                logger.error(error_msg)
                return False
            
            # Save to file
            return self.save_config()
            
        except Exception as e:
            logger.error(f"Error updating configuration: {e}")
            return False
    
    def reset_to_defaults(self) -> bool:
        """
        Reset configuration to default values and save to file.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.config = self._get_default_config()
            return self.save_config()
        except Exception as e:
            logger.error(f"Error resetting configuration to defaults: {e}")
            return False
    
    def backup_config(self, backup_path: Optional[str] = None) -> bool:
        """
        Create a backup of the current configuration.
        
        Args:
            backup_path: Optional path for backup file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if backup_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = f"{self.config_path.stem}_backup_{timestamp}.yaml"
            
            backup_path = Path(backup_path)
            
            with open(backup_path, 'w', encoding='utf-8') as file:
                yaml.dump(self.config, file, default_flow_style=False, indent=2)
                logger.info(f"Configuration backed up to {backup_path}")
                return True
                
        except Exception as e:
            logger.error(f"Error creating configuration backup: {e}")
            return False
    
    def restore_config(self, backup_path: str) -> bool:
        """
        Restore configuration from a backup file.
        
        Args:
            backup_path: Path to the backup file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            backup_path = Path(backup_path)
            if not backup_path.exists():
                logger.error(f"Backup file {backup_path} not found")
                return False
            
            with open(backup_path, 'r', encoding='utf-8') as file:
                restored_config = yaml.safe_load(file)
            
            # Validate restored configuration
            old_config = self.config
            self.config = restored_config
            validation_errors = self.validate_config()
            
            if validation_errors:
                self.config = old_config
                error_msg = "Restored configuration validation failed:\n"
                for section, errors in validation_errors.items():
                    error_msg += f"{section}: {', '.join(errors)}\n"
                logger.error(error_msg)
                return False
            
            # Save restored configuration
            return self.save_config()
            
        except Exception as e:
            logger.error(f"Error restoring configuration: {e}")
            return False
    
    def get_config_info(self) -> Dict[str, Any]:
        """
        Get information about the current configuration.
        
        Returns:
            Dictionary containing configuration metadata
        """
        try:
            config_info = {
                "config_file": str(self.config_path),
                "file_exists": self.config_path.exists(),
                "total_settings": self._count_settings(self.config),
                "validation_status": "valid" if not self.validate_config() else "invalid",
                "sections": list(self.config.keys())
            }
            
            if self.config_path.exists():
                stat = self.config_path.stat()
                config_info["last_modified"] = datetime.fromtimestamp(stat.st_mtime)
                config_info["file_size_bytes"] = stat.st_size
            
            return config_info
            
        except Exception as e:
            logger.error(f"Error getting configuration info: {e}")
            return {"error": str(e)}
    
    def _deep_merge(self, dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deep merge two dictionaries.
        
        Args:
            dict1: Base dictionary
            dict2: Dictionary to merge into dict1
            
        Returns:
            Merged dictionary
        """
        result = dict1.copy()
        
        for key, value in dict2.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def _count_settings(self, config_dict: Dict[str, Any]) -> int:
        """
        Count total number of settings in configuration.
        
        Args:
            config_dict: Configuration dictionary
            
        Returns:
            Total number of settings
        """
        count = 0
        for value in config_dict.values():
            if isinstance(value, dict):
                count += self._count_settings(value)
            else:
                count += 1
        return count