from typing import Dict, Any, Optional
import logging
from datetime import datetime
from utils.mongodb_realtime import get_mongo_client
from utils.config_manager import ConfigManager

logger = logging.getLogger(__name__)

# Cache the config manager instance
_config_manager = None

class CohortConfigManager:
    """Configuration manager for cohort-specific settings."""
    
    def __init__(self, connection_string: str):
        """
        Initialize cohort configuration manager.
        
        Args:
            connection_string: MongoDB connection string
        """
        global _config_manager
        self.connection_string = connection_string
        if _config_manager is None:
            _config_manager = ConfigManager()
        self.config_manager = _config_manager
        self.database_name = self.config_manager.get_setting('database_settings.database_name', 'physiobot-realtime')
    
    def get_cohort_config(self, cohort_id: str) -> Dict[str, Any]:
        """
        Get configuration for specific cohort.
        
        Args:
            cohort_id: Unique identifier for the cohort
            
        Returns:
            Dictionary containing cohort-specific settings
        """
        try:
            client = get_mongo_client(self.connection_string)
            db = getattr(client, self.database_name)
            cohorts_collection = db.cohorts
            
            cohort = cohorts_collection.find_one({"cohort_id": cohort_id})
            
            if cohort:
                # Merge default config with cohort-specific settings
                default_config = self.config_manager.config
                cohort_settings = cohort.get('settings', {})
                
                # Deep merge configurations
                merged_config = self._deep_merge(default_config.copy(), cohort_settings)
                return merged_config
            else:
                logger.warning(f"Cohort {cohort_id} not found, using default configuration")
                return self.config_manager.config
                
        except Exception as e:
            logger.error(f"Error getting cohort config for {cohort_id}: {e}")
            return self.config_manager.config
        finally:
            if 'client' in locals():
                client.close()
    
    def update_cohort_config(self, cohort_id: str, settings: Dict[str, Any]) -> bool:
        """
        Update configuration for specific cohort.
        
        Args:
            cohort_id: Unique identifier for the cohort
            settings: Dictionary of settings to update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            client = get_mongo_client(self.connection_string)
            db = getattr(client, self.database_name)
            cohorts_collection = db.cohorts
            
            result = cohorts_collection.update_one(
                {"cohort_id": cohort_id},
                {
                    "$set": {
                        "settings": settings,
                        "updated_at": datetime.utcnow()
                    }
                },
                upsert=True
            )
            
            if result.modified_count > 0 or result.upserted_id:
                logger.info(f"Updated configuration for cohort {cohort_id}")
                return True
            else:
                logger.warning(f"No changes made to cohort {cohort_id} configuration")
                return False
                
        except Exception as e:
            logger.error(f"Error updating cohort config for {cohort_id}: {e}")
            return False
        finally:
            if 'client' in locals():
                client.close()
    
    def create_cohort(self, cohort_data: Dict[str, Any]) -> bool:
        """
        Create a new cohort with default settings.
        
        Args:
            cohort_data: Dictionary containing cohort information
            
        Returns:
            True if successful, False otherwise
        """
        try:
            client = get_mongo_client(self.connection_string)
            db = getattr(client, self.database_name)
            cohorts_collection = db.cohorts
            
            # Ensure required fields
            required_fields = ['cohort_id', 'cohort_name', 'academic_year', 'semester']
            for field in required_fields:
                if field not in cohort_data:
                    raise ValueError(f"Missing required field: {field}")
            
            # Add default settings and metadata
            cohort_document = {
                **cohort_data,
                'created_at': datetime.utcnow(),
                'is_active': True,
                'settings': self._get_default_cohort_settings()
            }
            
            result = cohorts_collection.insert_one(cohort_document)
            
            if result.inserted_id:
                logger.info(f"Created cohort {cohort_data['cohort_id']}")
                return True
            else:
                logger.error(f"Failed to create cohort {cohort_data['cohort_id']}")
                return False
                
        except Exception as e:
            logger.error(f"Error creating cohort: {e}")
            return False
        finally:
            if 'client' in locals():
                client.close()
    
    def get_active_cohorts(self) -> list:
        """
        Get list of active cohorts.
        
        Returns:
            List of active cohort documents
        """
        try:
            client = get_mongo_client(self.connection_string)
            db = getattr(client, self.database_name)
            cohorts_collection = db.cohorts
            
            cohorts = list(cohorts_collection.find(
                {"is_active": True},
                {"_id": 0, "cohort_id": 1, "cohort_name": 1, "academic_year": 1, "semester": 1}
            ))
            
            return cohorts
            
        except Exception as e:
            logger.error(f"Error getting active cohorts: {e}")
            return []
        finally:
            if 'client' in locals():
                client.close()
    
    def deactivate_cohort(self, cohort_id: str) -> bool:
        """
        Deactivate a cohort (soft delete).
        
        Args:
            cohort_id: Unique identifier for the cohort
            
        Returns:
            True if successful, False otherwise
        """
        try:
            client = get_mongo_client(self.connection_string)
            db = getattr(client, self.database_name)
            cohorts_collection = db.cohorts
            
            result = cohorts_collection.update_one(
                {"cohort_id": cohort_id},
                {
                    "$set": {
                        "is_active": False,
                        "deactivated_at": datetime.utcnow()
                    }
                }
            )
            
            if result.modified_count > 0:
                logger.info(f"Deactivated cohort {cohort_id}")
                return True
            else:
                logger.warning(f"Cohort {cohort_id} not found or already deactivated")
                return False
                
        except Exception as e:
            logger.error(f"Error deactivating cohort {cohort_id}: {e}")
            return False
        finally:
            if 'client' in locals():
                client.close()
    
    def _deep_merge(self, base: Dict[str, Any], update: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deep merge two dictionaries.
        
        Args:
            base: Base dictionary
            update: Dictionary with updates
            
        Returns:
            Merged dictionary
        """
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value
        return base
    
    def _get_default_cohort_settings(self) -> Dict[str, Any]:
        """Get default settings for new cohorts."""
        return {
            'audio_settings': self.config_manager.get_audio_settings(),
            'conversation_settings': self.config_manager.get_conversation_settings(),
            'assignment_settings': {
                'patient_prompt_override': None,
                'supervisor_prompt_override': None,
                'due_date': None,
                'instructions': None
            }
        }