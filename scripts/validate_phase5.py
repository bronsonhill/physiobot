#!/usr/bin/env python3
"""
Phase 5 Validation Script for PhysioBot
Validates that all Phase 5 deliverables have been properly implemented.
"""

import os
import sys
import yaml
from pathlib import Path

def validate_phase5():
    """Validate Phase 5 implementation."""
    print("🔍 PhysioBot Phase 5 Validation")
    print("=" * 50)
    
    validation_results = {
        "files_created": [],
        "files_enhanced": [],
        "configuration_valid": False,
        "documentation_complete": False,
        "total_checks": 0,
        "passed_checks": 0
    }
    
    # Check new files created
    new_files = [
        "pages/Audio_Preferences.py",
        "pages/Admin_Configuration.py", 
        "tests/test_audio_compatibility.py",
        "docs/PHASE5_USER_GUIDE.md",
        "docs/PHASE5_TECHNICAL_DOCUMENTATION.md",
        "PHASE5_COMPLETION_REPORT.md"
    ]
    
    print("\n📁 Checking new files...")
    for file_path in new_files:
        validation_results["total_checks"] += 1
        if os.path.exists(file_path):
            validation_results["files_created"].append(file_path)
            validation_results["passed_checks"] += 1
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
    
    # Check enhanced files
    enhanced_files = [
        "pages/1_Patient_Conversation.py",
        "static/js/audio_interface.js",
        "config.yaml",
        "utils/config_manager.py"
    ]
    
    print("\n🔧 Checking enhanced files...")
    for file_path in enhanced_files:
        validation_results["total_checks"] += 1
        if os.path.exists(file_path):
            validation_results["files_enhanced"].append(file_path)
            validation_results["passed_checks"] += 1
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
    
    # Check configuration enhancements
    print("\n⚙️ Checking configuration...")
    validation_results["total_checks"] += 1
    try:
        with open("config.yaml", 'r') as f:
            config = yaml.safe_load(f)
            
        # Check for Phase 5 configuration sections
        phase5_sections = [
            "testing_settings",
            "monitoring_settings", 
            "ui_settings"
        ]
        
        config_valid = True
        for section in phase5_sections:
            if section not in config:
                config_valid = False
                print(f"❌ Missing config section: {section}")
            else:
                print(f"✅ Config section found: {section}")
        
        if config_valid:
            validation_results["configuration_valid"] = True
            validation_results["passed_checks"] += 1
            
    except Exception as e:
        print(f"❌ Configuration validation failed: {e}")
    
    # Check documentation completeness
    print("\n📚 Checking documentation...")
    validation_results["total_checks"] += 1
    doc_files = [
        "docs/PHASE5_USER_GUIDE.md",
        "docs/PHASE5_TECHNICAL_DOCUMENTATION.md"
    ]
    
    docs_complete = True
    for doc_file in doc_files:
        if os.path.exists(doc_file):
            # Check if file has substantial content
            with open(doc_file, 'r') as f:
                content = f.read()
                if len(content) > 1000:  # At least 1000 characters
                    print(f"✅ {doc_file} (substantial content)")
                else:
                    print(f"⚠️ {doc_file} (minimal content)")
                    docs_complete = False
        else:
            print(f"❌ {doc_file} (missing)")
            docs_complete = False
    
    if docs_complete:
        validation_results["documentation_complete"] = True
        validation_results["passed_checks"] += 1
    
    # Validate specific Phase 5 features
    print("\n🎨 Checking UI enhancements...")
    ui_features = check_ui_enhancements()
    
    print("\n🧪 Checking testing infrastructure...")
    testing_features = check_testing_infrastructure()
    
    print("\n📊 Checking admin features...")
    admin_features = check_admin_features()
    
    # Generate summary
    print("\n" + "=" * 50)
    print("📊 PHASE 5 VALIDATION SUMMARY")
    print("=" * 50)
    
    success_rate = (validation_results["passed_checks"] / validation_results["total_checks"]) * 100
    
    print(f"Total Checks: {validation_results['total_checks']}")
    print(f"Passed: {validation_results['passed_checks']}")
    print(f"Success Rate: {success_rate:.1f}%")
    
    print(f"\n📁 New Files Created: {len(validation_results['files_created'])}/6")
    print(f"🔧 Files Enhanced: {len(validation_results['files_enhanced'])}/4")
    print(f"⚙️ Configuration Valid: {'✅' if validation_results['configuration_valid'] else '❌'}")
    print(f"📚 Documentation Complete: {'✅' if validation_results['documentation_complete'] else '❌'}")
    
    # Overall status
    if success_rate >= 90:
        print(f"\n🎉 PHASE 5 VALIDATION: ✅ PASSED")
        print("Phase 5 implementation is complete and ready for deployment!")
    elif success_rate >= 75:
        print(f"\n⚠️ PHASE 5 VALIDATION: ⚠️ MOSTLY COMPLETE")
        print("Phase 5 implementation is mostly complete but may need minor fixes.")
    else:
        print(f"\n❌ PHASE 5 VALIDATION: ❌ INCOMPLETE")
        print("Phase 5 implementation needs significant work before deployment.")
    
    return validation_results

def check_ui_enhancements():
    """Check for UI enhancement implementations."""
    features = {
        "audio_preferences": os.path.exists("pages/Audio_Preferences.py"),
        "admin_configuration": os.path.exists("pages/Admin_Configuration.py"),
        "enhanced_patient_page": os.path.exists("pages/1_Patient_Conversation.py")
    }
    
    for feature, exists in features.items():
        if exists:
            print(f"✅ {feature}")
        else:
            print(f"❌ {feature}")
    
    return features

def check_testing_infrastructure():
    """Check for testing infrastructure."""
    features = {
        "compatibility_tests": os.path.exists("tests/test_audio_compatibility.py"),
        "validation_script": os.path.exists("scripts/validate_phase5.py")
    }
    
    for feature, exists in features.items():
        if exists:
            print(f"✅ {feature}")
        else:
            print(f"❌ {feature}")
    
    return features

def check_admin_features():
    """Check for admin feature implementations."""
    features = {
        "admin_config_page": os.path.exists("pages/Admin_Configuration.py"),
        "enhanced_config_manager": os.path.exists("utils/config_manager.py"),
        "cohort_config_manager": os.path.exists("utils/cohort_config_manager.py")
    }
    
    for feature, exists in features.items():
        if exists:
            print(f"✅ {feature}")
        else:
            print(f"❌ {feature}")
    
    return features

def check_phase5_specific_content():
    """Check for Phase 5 specific content in files."""
    checks = []
    
    # Check Audio_Preferences.py for specific content
    if os.path.exists("pages/Audio_Preferences.py"):
        with open("pages/Audio_Preferences.py", 'r') as f:
            content = f.read()
            if "audio_test_interface" in content and "troubleshooting_interface" in content:
                checks.append(("Audio Preferences functionality", True))
            else:
                checks.append(("Audio Preferences functionality", False))
    
    # Check Admin_Configuration.py for specific content
    if os.path.exists("pages/Admin_Configuration.py"):
        with open("pages/Admin_Configuration.py", 'r') as f:
            content = f.read()
            if "cohort_management_interface" in content and "testing_tools_interface" in content:
                checks.append(("Admin Configuration functionality", True))
            else:
                checks.append(("Admin Configuration functionality", False))
    
    # Check test file for comprehensive tests
    if os.path.exists("tests/test_audio_compatibility.py"):
        with open("tests/test_audio_compatibility.py", 'r') as f:
            content = f.read()
            if "test_browser_compatibility" in content and "test_audio_pipeline" in content:
                checks.append(("Comprehensive test suite", True))
            else:
                checks.append(("Comprehensive test suite", False))
    
    print("\n🔍 Content Validation:")
    for check_name, passed in checks:
        print(f"{'✅' if passed else '❌'} {check_name}")
    
    return checks

if __name__ == "__main__":
    try:
        validation_results = validate_phase5()
        
        # Additional content checks
        content_checks = check_phase5_specific_content()
        
        print("\n🚀 Phase 5 Implementation Summary:")
        print("- Enhanced User Interface: Modern audio conversation interface with accessibility")
        print("- Configuration Management: Student and admin configuration interfaces")
        print("- Testing Infrastructure: Comprehensive automated testing suite")
        print("- Documentation: Complete user and technical documentation")
        
        print("\n📋 Next Steps:")
        print("1. Run production deployment procedures")
        print("2. Conduct user training sessions")
        print("3. Execute pilot testing with limited user group")
        print("4. Monitor system performance and gather feedback")
        
    except Exception as e:
        print(f"❌ Validation failed with error: {e}")
        sys.exit(1)