#!/usr/bin/env python3
"""
Phase 3 Validation Script
Validates the audio-enabled patient conversation implementation.
"""

import os
import sys
import logging
import yaml
import importlib.util
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def check_file_exists(file_path: str, description: str) -> bool:
    """Check if a file exists."""
    if os.path.exists(file_path):
        logger.info(f"✅ {description}: {file_path}")
        return True
    else:
        logger.error(f"❌ Missing {description}: {file_path}")
        return False

def check_module_imports() -> bool:
    """Check if all required modules can be imported."""
    logger.info("Checking module imports...")
    
    modules = [
        ("streamlit", "Streamlit framework"),
        ("asyncio", "Async I/O support"),
        ("json", "JSON processing"),
        ("logging", "Logging framework"),
        ("datetime", "Date/time handling"),
        ("typing", "Type hints"),
        ("pymongo", "MongoDB client"),
        ("yaml", "YAML configuration"),
        ("numpy", "Numerical operations"),
        ("openai", "OpenAI API client"),
    ]
    
    all_imports_ok = True
    
    for module_name, description in modules:
        try:
            __import__(module_name)
            logger.info(f"✅ {description}: {module_name}")
        except ImportError as e:
            logger.error(f"❌ Failed to import {description} ({module_name}): {e}")
            all_imports_ok = False
    
    return all_imports_ok

def check_utils_modules() -> bool:
    """Check if all utils modules exist and can be imported."""
    logger.info("Checking utils modules...")
    
    utils_modules = [
        ("utils.audio_manager", "AudioManager"),
        ("utils.conversation_handler", "ConversationHandler"),
        ("utils.realtime_client", "RealtimeClient"),
        ("utils.config_manager", "ConfigManager"),
        ("utils.mongodb_realtime", "MongoDB Realtime"),
        ("utils.cohort_config_manager", "CohortConfigManager"),
    ]
    
    all_utils_ok = True
    
    for module_path, description in utils_modules:
        try:
            importlib.import_module(module_path)
            logger.info(f"✅ {description}: {module_path}")
        except ImportError as e:
            logger.error(f"❌ Failed to import {description} ({module_path}): {e}")
            all_utils_ok = False
    
    return all_utils_ok

def check_configuration() -> bool:
    """Check configuration file structure."""
    logger.info("Checking configuration...")
    
    config_path = "config.yaml"
    if not check_file_exists(config_path, "Configuration file"):
        return False
    
    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        
        required_sections = [
            "audio_settings",
            "conversation_settings", 
            "ui_settings",
            "database_settings",
            "openai_realtime"
        ]
        
        all_sections_ok = True
        
        for section in required_sections:
            if section in config:
                logger.info(f"✅ Configuration section: {section}")
            else:
                logger.error(f"❌ Missing configuration section: {section}")
                all_sections_ok = False
        
        # Check specific audio settings
        if "audio_settings" in config:
            audio_settings = config["audio_settings"]
            audio_keys = ["voice_type", "speech_speed", "conversation_detection", "quality_settings"]
            
            for key in audio_keys:
                if key in audio_settings:
                    logger.info(f"✅ Audio setting: {key}")
                else:
                    logger.error(f"❌ Missing audio setting: {key}")
                    all_sections_ok = False
        
        return all_sections_ok
        
    except yaml.YAMLError as e:
        logger.error(f"❌ Error parsing configuration file: {e}")
        return False

def check_static_files() -> bool:
    """Check static JavaScript files."""
    logger.info("Checking static files...")
    
    static_files = [
        ("static/js/audio_interface.js", "Audio Interface JavaScript"),
        ("static/js/audio_processor.js", "Audio Processor JavaScript"),
    ]
    
    all_files_ok = True
    
    for file_path, description in static_files:
        if not check_file_exists(file_path, description):
            all_files_ok = False
    
    return all_files_ok

def check_prompts() -> bool:
    """Check prompt files."""
    logger.info("Checking prompt files...")
    
    prompt_files = [
        ("prompts/prompt.txt", "Original patient prompt"),
        ("prompts/audio_patient_prompt.txt", "Audio-specific patient prompt"),
        ("prompts/supervisorprompt.txt", "Supervisor prompt"),
    ]
    
    all_prompts_ok = True
    
    for file_path, description in prompt_files:
        if not check_file_exists(file_path, description):
            all_prompts_ok = False
    
    return all_prompts_ok

def check_pages() -> bool:
    """Check Streamlit pages."""
    logger.info("Checking Streamlit pages...")
    
    pages = [
        ("Home.py", "Home page"),
        ("pages/1_Patient_Conversation.py", "Patient conversation page"),
        ("pages/2_Supervisor_Conversation.py", "Supervisor conversation page"),
    ]
    
    all_pages_ok = True
    
    for file_path, description in pages:
        if not check_file_exists(file_path, description):
            all_pages_ok = False
    
    return all_pages_ok

def check_requirements() -> bool:
    """Check requirements.txt."""
    logger.info("Checking requirements...")
    
    if not check_file_exists("requirements.txt", "Requirements file"):
        return False
    
    try:
        with open("requirements.txt", 'r') as file:
            requirements = file.read()
        
        required_packages = [
            "streamlit",
            "openai", 
            "pymongo",
            "pyyaml",
            "numpy",
            "asyncio",
        ]
        
        all_requirements_ok = True
        
        for package in required_packages:
            if package in requirements.lower():
                logger.info(f"✅ Required package: {package}")
            else:
                logger.warning(f"⚠️ Package not found in requirements: {package}")
                # Don't fail for this as some packages might be in stdlib
        
        return all_requirements_ok
        
    except Exception as e:
        logger.error(f"❌ Error reading requirements file: {e}")
        return False

def check_audio_conversation_page() -> bool:
    """Check the audio conversation page implementation."""
    logger.info("Checking audio conversation page implementation...")
    
    page_path = "pages/1_Patient_Conversation.py"
    if not os.path.exists(page_path):
        logger.error(f"❌ Patient conversation page not found: {page_path}")
        return False
    
    try:
        with open(page_path, 'r') as file:
            content = file.read()
        
        required_features = [
            ("ConversationHandler", "ConversationHandler import"),
            ("audio_conversation_handler", "Audio conversation handler"),
            ("audio_transcript_segments", "Audio transcript segments"),
            ("Start Audio Conversation", "Start conversation button"),
            ("Start Recording", "Recording button"),
            ("Stop Recording", "Stop recording button"),
            ("Live Conversation Transcript", "Live transcript display"),
            ("audio_interface.js", "Audio interface JavaScript"),
            ("log_audio_transcript", "Audio transcript logging"),
        ]
        
        all_features_ok = True
        
        for feature, description in required_features:
            if feature in content:
                logger.info(f"✅ {description}: Found")
            else:
                logger.error(f"❌ {description}: Not found")
                all_features_ok = False
        
        return all_features_ok
        
    except Exception as e:
        logger.error(f"❌ Error reading patient conversation page: {e}")
        return False

def validate_phase3() -> bool:
    """Run all Phase 3 validation checks."""
    logger.info("Starting Phase 3 validation...")
    logger.info("=" * 50)
    
    checks = [
        ("Module imports", check_module_imports),
        ("Utils modules", check_utils_modules),
        ("Configuration", check_configuration),
        ("Static files", check_static_files),
        ("Prompt files", check_prompts),
        ("Streamlit pages", check_pages),
        ("Requirements", check_requirements),
        ("Audio conversation page", check_audio_conversation_page),
    ]
    
    all_checks_passed = True
    
    for check_name, check_function in checks:
        logger.info(f"\n--- {check_name} ---")
        try:
            if not check_function():
                all_checks_passed = False
        except Exception as e:
            logger.error(f"❌ Error during {check_name}: {e}")
            all_checks_passed = False
    
    logger.info("\n" + "=" * 50)
    
    if all_checks_passed:
        logger.info("🎉 Phase 3 validation PASSED!")
        logger.info("The audio-enabled patient conversation is ready for testing.")
        return True
    else:
        logger.error("❌ Phase 3 validation FAILED!")
        logger.error("Please fix the issues above before proceeding.")
        return False

def main():
    """Main validation function."""
    try:
        success = validate_phase3()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("\nValidation interrupted by user.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error during validation: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()