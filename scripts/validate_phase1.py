"""
Phase 1 validation script for physiobot-realtime.
Tests all components implemented in Phase 1: Foundation & Infrastructure.
"""

import os
import sys
import logging
from datetime import datetime
from typing import Dict, Any
from dotenv import load_dotenv

# Add the parent directory to sys.path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.config_manager import ConfigManager
from utils.cohort_config_manager import CohortConfigManager
from utils.mongodb_realtime import get_mongo_client, get_database_name

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Phase1Validator:
    """Validator for Phase 1 components."""
    
    def __init__(self):
        """Initialize the validator."""
        self.config_manager = ConfigManager()
        self.validation_results = {}
    
    def validate_config_system(self) -> bool:
        """Validate configuration system."""
        logger.info("Validating configuration system...")
        
        try:
            # Test configuration loading
            config = self.config_manager.config
            required_sections = ['audio_settings', 'conversation_settings', 'ui_settings', 'database_settings']
            
            for section in required_sections:
                if section not in config:
                    logger.error(f"Missing configuration section: {section}")
                    return False
            
            # Test configuration validation
            errors = self.config_manager.validate_config()
            if errors:
                logger.warning(f"Configuration validation warnings: {errors}")
            
            # Test setting operations
            original_voice = self.config_manager.get_setting('audio_settings.voice_type')
            test_success = self.config_manager.update_setting('audio_settings.voice_type', 'echo')
            
            if test_success:
                # Restore original value
                self.config_manager.update_setting('audio_settings.voice_type', original_voice)
            
            logger.info("✓ Configuration system validation passed")
            return True
            
        except Exception as e:
            logger.error(f"Configuration system validation failed: {e}")
            return False
    
    def validate_database_connection(self, connection_string: str) -> bool:
        """Validate database connection and structure."""
        logger.info("Validating database connection...")
        
        try:
            client = get_mongo_client(connection_string)
            db_name = get_database_name()
            db = getattr(client, db_name)
            
            # Test connection
            db.command('ping')
            logger.info(f"✓ Connected to database: {db_name}")
            
            # Check collections
            collections = db.list_collection_names()
            required_collections = ['cohorts', 'valid_identifiers', 'audio_transcripts', 'instructors']
            
            missing_collections = [col for col in required_collections if col not in collections]
            if missing_collections:
                logger.warning(f"Missing collections (will be created on first use): {missing_collections}")
            else:
                logger.info("✓ All required collections present")
            
            return True
            
        except Exception as e:
            logger.error(f"Database connection validation failed: {e}")
            return False
        finally:
            if 'client' in locals():
                client.close()
    
    def validate_cohort_system(self, connection_string: str) -> bool:
        """Validate cohort management system."""
        logger.info("Validating cohort management system...")
        
        try:
            cohort_manager = CohortConfigManager(connection_string)
            
            # Test cohort creation
            test_cohort_data = {
                "cohort_id": f"TEST_COHORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "cohort_name": "Test Cohort for Validation",
                "academic_year": "2024",
                "semester": "Test"
            }
            
            created = cohort_manager.create_cohort(test_cohort_data)
            if not created:
                logger.error("Failed to create test cohort")
                return False
            
            # Test cohort configuration
            config = cohort_manager.get_cohort_config(test_cohort_data["cohort_id"])
            if not config:
                logger.error("Failed to get cohort configuration")
                return False
            
            # Test configuration update
            test_settings = {"test_setting": "test_value"}
            updated = cohort_manager.update_cohort_config(test_cohort_data["cohort_id"], test_settings)
            if not updated:
                logger.error("Failed to update cohort configuration")
                return False
            
            # Test cohort listing
            active_cohorts = cohort_manager.get_active_cohorts()
            test_cohort_found = any(c['cohort_id'] == test_cohort_data["cohort_id"] for c in active_cohorts)
            if not test_cohort_found:
                logger.error("Test cohort not found in active cohorts list")
                return False
            
            # Clean up test cohort
            cohort_manager.deactivate_cohort(test_cohort_data["cohort_id"])
            
            logger.info("✓ Cohort management system validation passed")
            return True
            
        except Exception as e:
            logger.error(f"Cohort system validation failed: {e}")
            return False
    
    def validate_file_structure(self) -> bool:
        """Validate project file structure."""
        logger.info("Validating project file structure...")
        
        required_files = [
            'config.yaml',
            'requirements.txt',
            'utils/config_manager.py',
            'utils/cohort_config_manager.py',
            'utils/mongodb_realtime.py',
            'scripts/migrate_to_realtime.py',
            'scripts/bulk_student_management.py'
        ]
        
        missing_files = []
        for file_path in required_files:
            if not os.path.exists(file_path):
                missing_files.append(file_path)
        
        if missing_files:
            logger.error(f"Missing required files: {missing_files}")
            return False
        
        logger.info("✓ File structure validation passed")
        return True
    
    def validate_requirements(self) -> bool:
        """Validate requirements.txt has necessary dependencies."""
        logger.info("Validating requirements...")
        
        try:
            with open('requirements.txt', 'r') as f:
                requirements_content = f.read()
            
            required_packages = [
                'openai',
                'pymongo',
                'python-dotenv',
                'streamlit',
                'websockets',
                'PyYAML',
                'pandas'
            ]
            
            missing_packages = []
            for package in required_packages:
                if package not in requirements_content:
                    missing_packages.append(package)
            
            if missing_packages:
                logger.error(f"Missing required packages in requirements.txt: {missing_packages}")
                return False
            
            logger.info("✓ Requirements validation passed")
            return True
            
        except Exception as e:
            logger.error(f"Requirements validation failed: {e}")
            return False
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate validation report."""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "phase": "Phase 1: Foundation & Infrastructure",
            "validation_results": self.validation_results,
            "overall_status": all(self.validation_results.values()),
            "next_steps": [
                "Install dependencies: pip install -r requirements.txt",
                "Set up environment variables (MONGODB_CONNECTION_STRING)",
                "Run database migration: python scripts/migrate_to_realtime.py",
                "Test configuration: python -c 'from utils.config_manager import ConfigManager; cm = ConfigManager(); print(cm.validate_config())'",
                "Proceed to Phase 2: Core Audio Infrastructure"
            ]
        }

def main():
    """Main validation function."""
    logger.info("=" * 60)
    logger.info("PhysioBot Realtime - Phase 1 Validation")
    logger.info("=" * 60)
    
    # Load environment variables
    load_dotenv()
    
    validator = Phase1Validator()
    
    # Run validations
    validations = [
        ("File Structure", validator.validate_file_structure),
        ("Requirements", validator.validate_requirements),
        ("Configuration System", validator.validate_config_system)
    ]
    
    # Database validations (only if connection string is available)
    connection_string = os.getenv("MONGODB_CONNECTION_STRING")
    if connection_string:
        validations.extend([
            ("Database Connection", lambda: validator.validate_database_connection(connection_string)),
            ("Cohort System", lambda: validator.validate_cohort_system(connection_string))
        ])
    else:
        logger.warning("MONGODB_CONNECTION_STRING not found - skipping database validations")
        validator.validation_results["Database Connection"] = False
        validator.validation_results["Cohort System"] = False
    
    # Execute validations
    for name, validation_func in validations:
        try:
            result = validation_func()
            validator.validation_results[name] = result
            status = "✓ PASS" if result else "✗ FAIL"
            logger.info(f"{name}: {status}")
        except Exception as e:
            validator.validation_results[name] = False
            logger.error(f"{name}: ✗ FAIL - {e}")
    
    # Generate report
    report = validator.generate_report()
    
    logger.info("=" * 60)
    logger.info("VALIDATION SUMMARY")
    logger.info("=" * 60)
    
    for component, status in validator.validation_results.items():
        status_text = "✓ PASS" if status else "✗ FAIL"
        logger.info(f"{component}: {status_text}")
    
    overall_status = report["overall_status"]
    logger.info("-" * 60)
    logger.info(f"Overall Status: {'✓ PASS' if overall_status else '✗ FAIL'}")
    
    if overall_status:
        logger.info("Phase 1 validation completed successfully!")
        logger.info("System is ready for Phase 2 development.")
    else:
        logger.warning("Phase 1 validation failed. Please address the issues above.")
    
    logger.info("\nNext Steps:")
    for step in report["next_steps"]:
        logger.info(f"  • {step}")
    
    return overall_status

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)