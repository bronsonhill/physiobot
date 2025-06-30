"""
Database migration script for physiobot-realtime system.
Migrates from the legacy physiobot database to the new realtime structure.
"""

import os
import sys
import logging
from datetime import datetime
from typing import Dict, Any
from dotenv import load_dotenv

# Add the parent directory to sys.path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.mongodb_realtime import get_mongo_client, migrate_legacy_data
from utils.config_manager import ConfigManager
from utils.cohort_config_manager import CohortConfigManager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_database_indexes(connection_string: str) -> bool:
    """
    Create database indexes for optimal performance.
    
    Args:
        connection_string: MongoDB connection string
        
    Returns:
        True if successful, False otherwise
    """
    try:
        config_manager = ConfigManager()
        db_name = config_manager.get_setting('database_settings.database_name', 'physiobot-realtime')
        
        client = get_mongo_client(connection_string)
        db = getattr(client, db_name)
        
        # Create indexes for audio_transcripts collection
        logger.info("Creating indexes for audio_transcripts collection...")
        db.audio_transcripts.create_index([("cohort_id", 1), ("timestamp", -1)])
        db.audio_transcripts.create_index([("identifier", 1), ("cohort_id", 1)])
        db.audio_transcripts.create_index([("cohort_id", 1), ("assignment_id", 1)])
        
        # Create indexes for valid_identifiers collection
        logger.info("Creating indexes for valid_identifiers collection...")
        db.valid_identifiers.create_index([("cohort_id", 1), ("is_active", 1)])
        db.valid_identifiers.create_index([("identifier", 1)], unique=True)
        
        # Create indexes for cohorts collection
        logger.info("Creating indexes for cohorts collection...")
        db.cohorts.create_index([("cohort_id", 1)], unique=True)
        db.cohorts.create_index([("is_active", 1)])
        
        # Create indexes for instructors collection
        logger.info("Creating indexes for instructors collection...")
        db.instructors.create_index([("email", 1)], unique=True)
        db.instructors.create_index([("cohort_access", 1)])
        
        logger.info("Database indexes created successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error creating database indexes: {e}")
        return False
    finally:
        if 'client' in locals():
            client.close()

def create_default_cohort(connection_string: str) -> bool:
    """
    Create the default cohort for the system.
    
    Args:
        connection_string: MongoDB connection string
        
    Returns:
        True if successful, False otherwise
    """
    try:
        cohort_manager = CohortConfigManager(connection_string)
        
        default_cohort_data = {
            "cohort_id": "PHYSIO_DEFAULT",
            "cohort_name": "Default Physiotherapy Cohort",
            "academic_year": "2024",
            "semester": "Default",
            "instructor_emails": []
        }
        
        result = cohort_manager.create_cohort(default_cohort_data)
        if result:
            logger.info("Default cohort created successfully")
        else:
            logger.warning("Default cohort may already exist")
        
        return True
        
    except Exception as e:
        logger.error(f"Error creating default cohort: {e}")
        return False

def validate_database_schema(connection_string: str) -> bool:
    """
    Validate that the database schema is properly set up.
    
    Args:
        connection_string: MongoDB connection string
        
    Returns:
        True if schema is valid, False otherwise
    """
    try:
        config_manager = ConfigManager()
        db_name = config_manager.get_setting('database_settings.database_name', 'physiobot-realtime')
        
        client = get_mongo_client(connection_string)
        db = getattr(client, db_name)
        
        # Check that required collections exist
        required_collections = ['cohorts', 'valid_identifiers', 'audio_transcripts', 'instructors']
        existing_collections = db.list_collection_names()
        
        for collection in required_collections:
            if collection not in existing_collections:
                logger.warning(f"Collection '{collection}' does not exist")
                return False
        
        # Check that default cohort exists
        default_cohort = db.cohorts.find_one({"cohort_id": "PHYSIO_DEFAULT"})
        if not default_cohort:
            logger.warning("Default cohort does not exist")
            return False
        
        logger.info("Database schema validation passed")
        return True
        
    except Exception as e:
        logger.error(f"Error validating database schema: {e}")
        return False
    finally:
        if 'client' in locals():
            client.close()

def backup_legacy_database(connection_string: str, backup_prefix: str = "backup") -> bool:
    """
    Create a backup of the legacy database before migration.
    
    Args:
        connection_string: MongoDB connection string
        backup_prefix: Prefix for backup collection names
        
    Returns:
        True if successful, False otherwise
    """
    try:
        client = get_mongo_client(connection_string)
        legacy_db = client.physiobot
        
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        
        # Backup valid_identifiers
        legacy_identifiers = list(legacy_db.valid_identifiers.find({}))
        if legacy_identifiers:
            backup_collection = f"{backup_prefix}_valid_identifiers_{timestamp}"
            legacy_db[backup_collection].insert_many(legacy_identifiers)
            logger.info(f"Backed up {len(legacy_identifiers)} identifiers to {backup_collection}")
        
        # Backup transcripts
        legacy_transcripts = list(legacy_db.transcripts.find({}))
        if legacy_transcripts:
            backup_collection = f"{backup_prefix}_transcripts_{timestamp}"
            legacy_db[backup_collection].insert_many(legacy_transcripts)
            logger.info(f"Backed up {len(legacy_transcripts)} transcripts to {backup_collection}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error creating backup: {e}")
        return False
    finally:
        if 'client' in locals():
            client.close()

def main():
    """Main migration function."""
    logger.info("Starting physiobot-realtime database migration...")
    
    # Load environment variables
    load_dotenv()
    
    # Get MongoDB connection string
    connection_string = os.getenv("MONGODB_CONNECTION_STRING")
    if not connection_string:
        logger.error("MONGODB_CONNECTION_STRING not found in environment variables")
        return False
    
    # Configuration validation
    config_manager = ConfigManager()
    validation_errors = config_manager.validate_config()
    if validation_errors:
        logger.error(f"Configuration validation failed: {validation_errors}")
        return False
    
    try:
        # Step 1: Create backup of legacy data
        logger.info("Step 1: Creating backup of legacy data...")
        if not backup_legacy_database(connection_string):
            logger.error("Failed to create backup")
            return False
        
        # Step 2: Create database indexes
        logger.info("Step 2: Creating database indexes...")
        if not create_database_indexes(connection_string):
            logger.error("Failed to create database indexes")
            return False
        
        # Step 3: Create default cohort
        logger.info("Step 3: Creating default cohort...")
        if not create_default_cohort(connection_string):
            logger.error("Failed to create default cohort")
            return False
        
        # Step 4: Migrate legacy data
        logger.info("Step 4: Migrating legacy data...")
        if not migrate_legacy_data(connection_string):
            logger.error("Failed to migrate legacy data")
            return False
        
        # Step 5: Validate database schema
        logger.info("Step 5: Validating database schema...")
        if not validate_database_schema(connection_string):
            logger.error("Database schema validation failed")
            return False
        
        logger.info("Migration completed successfully!")
        logger.info(f"Database: {config_manager.get_setting('database_settings.database_name')}")
        logger.info("Next steps:")
        logger.info("1. Test the configuration with: python -c 'from utils.config_manager import ConfigManager; cm = ConfigManager(); print(cm.validate_config())'")
        logger.info("2. Verify database connectivity")
        logger.info("3. Proceed to Phase 2 development")
        
        return True
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)