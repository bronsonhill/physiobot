import yaml
import os
from typing import Dict, Any

class ConfigManager:
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as file:
                    return yaml.safe_load(file)
            else:
                return self.get_default_config()
        except Exception as e:
            print(f"Error loading config: {e}")
            return self.get_default_config()
    
    def get_default_config(self) -> Dict[str, Any]:
        """Return default configuration"""
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
                'show_audio_controls': True
            }
        }
    
    def get_audio_settings(self) -> Dict[str, Any]:
        """Get audio configuration settings"""
        return self.config.get('audio_settings', {})
    
    def get_conversation_settings(self) -> Dict[str, Any]:
        """Get conversation configuration settings"""
        return self.config.get('conversation_settings', {})
    
    def get_ui_settings(self) -> Dict[str, Any]:
        """Get UI configuration settings"""
        return self.config.get('ui_settings', {})
    
    def update_setting(self, key: str, value: Any) -> bool:
        """Update a configuration setting"""
        try:
            keys = key.split('.')
            config_section = self.config
            
            # Navigate to the correct section
            for k in keys[:-1]:
                if k not in config_section:
                    config_section[k] = {}
                config_section = config_section[k]
            
            # Update the value
            config_section[keys[-1]] = value
            
            # Save to file
            with open(self.config_path, 'w') as file:
                yaml.dump(self.config, file, default_flow_style=False)
            
            return True
        except Exception as e:
            print(f"Error updating setting: {e}")
            return False