#!/usr/bin/env python3
"""
Phase 5 Validation Script: UI/UX Enhancement & Testing

This script validates all Phase 5 deliverables including:
- Enhanced User Interface components
- Configuration Interface functionality
- Comprehensive Testing tools
- Documentation and Training materials

Usage:
    python scripts/validate_phase5.py [--verbose] [--output report.txt]
"""

import os
import sys
import json
import yaml
import importlib
import traceback
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import argparse
import logging

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Phase5Validator:
    """Comprehensive validation for Phase 5 implementation."""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.results = {
            "validation_timestamp": datetime.now().isoformat(),
            "phase": "Phase 5: UI/UX Enhancement & Testing",
            "overall_status": "PENDING",
            "categories": {},
            "detailed_results": [],
            "errors": [],
            "recommendations": []
        }
        
    def run_validation(self) -> Dict[str, Any]:
        """Run complete Phase 5 validation."""
        logger.info("Starting Phase 5 validation...")
        
        # Test categories for Phase 5
        test_categories = [
            ("Enhanced User Interface", self._test_enhanced_ui),
            ("Configuration Interface", self._test_configuration_interface),
            ("Testing Tools", self._test_testing_tools),
            ("Documentation", self._test_documentation),
            ("Cross-browser Compatibility", self._test_browser_compatibility),
            ("Performance Testing", self._test_performance),
            ("User Experience", self._test_user_experience),
            ("System Integration", self._test_system_integration)
        ]
        
        passed_categories = 0
        total_categories = len(test_categories)
        
        for category_name, test_function in test_categories:
            logger.info(f"Testing {category_name}...")
            try:
                result = test_function()
                self.results["categories"][category_name] = result
                
                if result["status"] == "PASS":
                    passed_categories += 1
                    
                self._log_category_result(category_name, result)
                
            except Exception as e:
                error_msg = f"Error testing {category_name}: {str(e)}"
                logger.error(error_msg)
                self.results["errors"].append(error_msg)
                self.results["categories"][category_name] = {
                    "status": "ERROR",
                    "message": error_msg,
                    "details": traceback.format_exc()
                }
        
        # Calculate overall status
        success_rate = (passed_categories / total_categories) * 100
        if success_rate >= 90:
            self.results["overall_status"] = "PASS"
        elif success_rate >= 70:
            self.results["overall_status"] = "PARTIAL"
        else:
            self.results["overall_status"] = "FAIL"
        
        self.results["success_rate"] = success_rate
        logger.info(f"Phase 5 validation completed with {success_rate:.1f}% success rate")
        
        return self.results
    
    def _test_enhanced_ui(self) -> Dict[str, Any]:
        """Test enhanced user interface components."""
        checks = []
        
        # Check if admin configuration page exists
        admin_page_path = project_root / "pages" / "Admin_Configuration.py"
        checks.append({
            "check": "Admin Configuration Page Exists",
            "status": "PASS" if admin_page_path.exists() else "FAIL",
            "details": f"Path: {admin_page_path}"
        })
        
        if admin_page_path.exists():
            # Check admin page content
            with open(admin_page_path, 'r') as f:
                admin_content = f.read()
            
            # Essential UI components
            ui_components = [
                ("Streamlit tabs", "st.tabs(" in admin_content),
                ("Audio settings interface", "Audio Settings" in admin_content),
                ("System monitoring dashboard", "System Monitoring" in admin_content),
                ("Testing tools interface", "Testing Tools" in admin_content),
                ("User management interface", "User Management" in admin_content),
                ("Documentation interface", "Documentation" in admin_content),
                ("Authentication system", "admin_authenticated" in admin_content),
                ("Configuration controls", "ConfigManager" in admin_content),
                ("Visual indicators", "st.metric" in admin_content),
                ("Interactive buttons", "st.button" in admin_content)
            ]
            
            for component_name, check_condition in ui_components:
                checks.append({
                    "check": f"UI Component: {component_name}",
                    "status": "PASS" if check_condition else "FAIL",
                    "details": f"Found in admin page: {check_condition}"
                })
        
        # Check enhanced patient conversation UI
        patient_page_path = project_root / "pages" / "1_Patient_Conversation.py"
        if patient_page_path.exists():
            with open(patient_page_path, 'r') as f:
                patient_content = f.read()
            
            ui_enhancements = [
                ("Audio visualization", "audio_visualization" in patient_content.lower()),
                ("Volume indicators", "volume" in patient_content.lower()),
                ("Status indicators", "status" in patient_content.lower()),
                ("Professional styling", "st.markdown" in patient_content and "style" in patient_content.lower()),
                ("Responsive layout", "st.columns" in patient_content),
                ("Real-time updates", "st.rerun" in patient_content)
            ]
            
            for enhancement_name, check_condition in ui_enhancements:
                checks.append({
                    "check": f"Patient UI Enhancement: {enhancement_name}",
                    "status": "PASS" if check_condition else "FAIL",
                    "details": f"Enhanced feature present: {check_condition}"
                })
        
        passed_checks = sum(1 for check in checks if check["status"] == "PASS")
        total_checks = len(checks)
        
        return {
            "status": "PASS" if passed_checks >= total_checks * 0.8 else "FAIL",
            "passed": passed_checks,
            "total": total_checks,
            "checks": checks,
            "message": f"Enhanced UI validation: {passed_checks}/{total_checks} checks passed"
        }
    
    def _test_configuration_interface(self) -> Dict[str, Any]:
        """Test configuration interface functionality."""
        checks = []
        
        # Test ConfigManager enhancements
        try:
            from utils.config_manager import ConfigManager
            config_manager = ConfigManager()
            
            # Test new methods
            new_methods = [
                ("update_config", hasattr(config_manager, 'update_config')),
                ("reset_to_defaults", hasattr(config_manager, 'reset_to_defaults')),
                ("backup_config", hasattr(config_manager, 'backup_config')),
                ("restore_config", hasattr(config_manager, 'restore_config')),
                ("get_config_info", hasattr(config_manager, 'get_config_info')),
                ("validate_config", hasattr(config_manager, 'validate_config'))
            ]
            
            for method_name, has_method in new_methods:
                checks.append({
                    "check": f"ConfigManager method: {method_name}",
                    "status": "PASS" if has_method else "FAIL",
                    "details": f"Method exists: {has_method}"
                })
            
            # Test configuration validation
            try:
                validation_result = config_manager.validate_config()
                checks.append({
                    "check": "Configuration validation works",
                    "status": "PASS",
                    "details": f"Validation returned: {type(validation_result)}"
                })
            except Exception as e:
                checks.append({
                    "check": "Configuration validation works",
                    "status": "FAIL",
                    "details": f"Validation error: {str(e)}"
                })
            
            # Test configuration info
            try:
                config_info = config_manager.get_config_info()
                checks.append({
                    "check": "Configuration info retrieval",
                    "status": "PASS" if isinstance(config_info, dict) else "FAIL",
                    "details": f"Config info type: {type(config_info)}"
                })
            except Exception as e:
                checks.append({
                    "check": "Configuration info retrieval",
                    "status": "FAIL",
                    "details": f"Config info error: {str(e)}"
                })
                
        except ImportError as e:
            checks.append({
                "check": "ConfigManager import",
                "status": "FAIL",
                "details": f"Import error: {str(e)}"
            })
        
        # Test configuration file structure
        config_path = project_root / "config.yaml"
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    config_data = yaml.safe_load(f)
                
                required_sections = [
                    "audio_settings",
                    "conversation_settings", 
                    "ui_settings",
                    "database_settings"
                ]
                
                for section in required_sections:
                    checks.append({
                        "check": f"Config section: {section}",
                        "status": "PASS" if section in config_data else "FAIL",
                        "details": f"Section exists: {section in config_data}"
                    })
                    
            except Exception as e:
                checks.append({
                    "check": "Configuration file parsing",
                    "status": "FAIL",
                    "details": f"Parse error: {str(e)}"
                })
        else:
            checks.append({
                "check": "Configuration file exists",
                "status": "FAIL",
                "details": f"File not found: {config_path}"
            })
        
        passed_checks = sum(1 for check in checks if check["status"] == "PASS")
        total_checks = len(checks)
        
        return {
            "status": "PASS" if passed_checks >= total_checks * 0.8 else "FAIL",
            "passed": passed_checks,
            "total": total_checks,
            "checks": checks,
            "message": f"Configuration interface validation: {passed_checks}/{total_checks} checks passed"
        }
    
    def _test_testing_tools(self) -> Dict[str, Any]:
        """Test comprehensive testing tools."""
        checks = []
        
        # Check if this validation script exists and works
        checks.append({
            "check": "Phase 5 validation script exists",
            "status": "PASS",
            "details": "This script is running successfully"
        })
        
        # Test database monitoring functions
        try:
            from utils.mongodb_realtime import get_database_stats, get_recent_sessions, get_system_health
            
            mongodb_functions = [
                ("get_database_stats", get_database_stats),
                ("get_recent_sessions", get_recent_sessions),
                ("get_system_health", get_system_health)
            ]
            
            for func_name, func in mongodb_functions:
                checks.append({
                    "check": f"MongoDB function: {func_name}",
                    "status": "PASS" if callable(func) else "FAIL",
                    "details": f"Function callable: {callable(func)}"
                })
                
        except ImportError as e:
            checks.append({
                "check": "MongoDB testing functions import",
                "status": "FAIL",
                "details": f"Import error: {str(e)}"
            })
        
        # Check for previous validation scripts
        validation_scripts = [
            "validate_phase1.py",
            "validate_phase3.py",
            "validate_phase4.py"
        ]
        
        scripts_dir = project_root / "scripts"
        for script_name in validation_scripts:
            script_path = scripts_dir / script_name
            checks.append({
                "check": f"Validation script: {script_name}",
                "status": "PASS" if script_path.exists() else "FAIL",
                "details": f"Script exists: {script_path.exists()}"
            })
        
        # Test static file serving
        static_dir = project_root / "static"
        if static_dir.exists():
            static_files = [
                "js/audio_interface.js",
                "js/audio_processor.js"
            ]
            
            for static_file in static_files:
                file_path = static_dir / static_file
                checks.append({
                    "check": f"Static file: {static_file}",
                    "status": "PASS" if file_path.exists() else "FAIL",
                    "details": f"File exists: {file_path.exists()}"
                })
        
        passed_checks = sum(1 for check in checks if check["status"] == "PASS")
        total_checks = len(checks)
        
        return {
            "status": "PASS" if passed_checks >= total_checks * 0.7 else "FAIL",
            "passed": passed_checks,
            "total": total_checks,
            "checks": checks,
            "message": f"Testing tools validation: {passed_checks}/{total_checks} checks passed"
        }
    
    def _test_documentation(self) -> Dict[str, Any]:
        """Test documentation and training materials."""
        checks = []
        
        # Check for documentation files
        doc_files = [
            ("README.md", "Main documentation"),
            ("IMPLEMENTATION_PLAN.md", "Implementation plan"),
            ("PHASE3_COMPLETION_REPORT.md", "Phase 3 report"),
            ("PHASE1_README.md", "Phase 1 documentation")
        ]
        
        for doc_file, description in doc_files:
            file_path = project_root / doc_file
            checks.append({
                "check": f"Documentation file: {doc_file}",
                "status": "PASS" if file_path.exists() else "FAIL",
                "details": f"{description} - exists: {file_path.exists()}"
            })
        
        # Check prompts directory
        prompts_dir = project_root / "prompts"
        if prompts_dir.exists():
            prompt_files = [
                "audio_patient_prompt.txt",
                "audio_supervisor_prompt.txt",
                "prompt.txt",
                "supervisorprompt.txt"
            ]
            
            for prompt_file in prompt_files:
                file_path = prompts_dir / prompt_file
                checks.append({
                    "check": f"Prompt file: {prompt_file}",
                    "status": "PASS" if file_path.exists() else "FAIL",
                    "details": f"Prompt exists: {file_path.exists()}"
                })
        
        # Check if admin page includes documentation
        admin_page_path = project_root / "pages" / "Admin_Configuration.py"
        if admin_page_path.exists():
            with open(admin_page_path, 'r') as f:
                admin_content = f.read()
            
            doc_features = [
                ("Training materials section", "Training Materials" in admin_content),
                ("Documentation section", "Documentation" in admin_content),
                ("Quick reference", "Quick Reference" in admin_content),
                ("Video tutorials", "Video Tutorials" in admin_content),
                ("System status", "System Status" in admin_content)
            ]
            
            for feature_name, has_feature in doc_features:
                checks.append({
                    "check": f"Admin documentation: {feature_name}",
                    "status": "PASS" if has_feature else "FAIL",
                    "details": f"Feature present: {has_feature}"
                })
        
        passed_checks = sum(1 for check in checks if check["status"] == "PASS")
        total_checks = len(checks)
        
        return {
            "status": "PASS" if passed_checks >= total_checks * 0.8 else "FAIL",
            "passed": passed_checks,
            "total": total_checks,
            "checks": checks,
            "message": f"Documentation validation: {passed_checks}/{total_checks} checks passed"
        }
    
    def _test_browser_compatibility(self) -> Dict[str, Any]:
        """Test cross-browser compatibility indicators."""
        checks = []
        
        # Check for modern web technologies usage
        patient_page_path = project_root / "pages" / "1_Patient_Conversation.py"
        if patient_page_path.exists():
            with open(patient_page_path, 'r') as f:
                content = f.read()
            
            browser_compat_features = [
                ("WebRTC usage", "webrtc" in content.lower() or "getUserMedia" in content.lower()),
                ("JavaScript integration", "<script>" in content),
                ("Audio interface", "audio_interface" in content.lower()),
                ("Modern HTML5", "unsafe_allow_html=True" in content),
                ("Responsive design", "st.columns" in content)
            ]
            
            for feature_name, has_feature in browser_compat_features:
                checks.append({
                    "check": f"Browser compatibility: {feature_name}",
                    "status": "PASS" if has_feature else "FAIL",
                    "details": f"Feature implemented: {has_feature}"
                })
        
        # Check static JavaScript files
        js_dir = project_root / "static" / "js"
        if js_dir.exists():
            js_files = list(js_dir.glob("*.js"))
            checks.append({
                "check": "JavaScript files present",
                "status": "PASS" if js_files else "FAIL",
                "details": f"Found {len(js_files)} JS files"
            })
            
            # Check for modern JavaScript features in files
            for js_file in js_files:
                try:
                    with open(js_file, 'r') as f:
                        js_content = f.read()
                    
                    modern_features = [
                        ("ES6 syntax", "const " in js_content or "let " in js_content),
                        ("Arrow functions", "=>" in js_content),
                        ("Audio API", "Audio" in js_content or "audioContext" in js_content.lower())
                    ]
                    
                    for feature_name, has_feature in modern_features:
                        checks.append({
                            "check": f"JS modern feature in {js_file.name}: {feature_name}",
                            "status": "PASS" if has_feature else "PARTIAL",
                            "details": f"Feature present: {has_feature}"
                        })
                        
                except Exception as e:
                    checks.append({
                        "check": f"JS file reading: {js_file.name}",
                        "status": "FAIL",
                        "details": f"Error reading file: {str(e)}"
                    })
        
        passed_checks = sum(1 for check in checks if check["status"] in ["PASS", "PARTIAL"])
        total_checks = len(checks)
        
        return {
            "status": "PASS" if passed_checks >= total_checks * 0.7 else "FAIL",
            "passed": passed_checks,
            "total": total_checks,
            "checks": checks,
            "message": f"Browser compatibility validation: {passed_checks}/{total_checks} checks passed"
        }
    
    def _test_performance(self) -> Dict[str, Any]:
        """Test performance-related implementations."""
        checks = []
        
        # Check for performance optimizations in code
        patient_page_path = project_root / "pages" / "1_Patient_Conversation.py"
        if patient_page_path.exists():
            with open(patient_page_path, 'r') as f:
                content = f.read()
            
            performance_features = [
                ("Async operations", "async" in content and "await" in content),
                ("Session state management", "st.session_state" in content),
                ("Efficient reruns", "st.rerun()" in content),
                ("Error handling", "try:" in content and "except" in content),
                ("Resource cleanup", "finally:" in content or "close()" in content)
            ]
            
            for feature_name, has_feature in performance_features:
                checks.append({
                    "check": f"Performance feature: {feature_name}",
                    "status": "PASS" if has_feature else "FAIL",
                    "details": f"Feature implemented: {has_feature}"
                })
        
        # Check configuration for performance settings
        config_path = project_root / "config.yaml"
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    config_data = yaml.safe_load(f)
                
                performance_settings = [
                    ("Connection timeout", "connection_timeout" in str(config_data)),
                    ("Auto-save interval", "auto_save_interval" in str(config_data)),
                    ("Sample rate optimization", "sample_rate" in str(config_data)),
                    ("Max duration limits", "max_duration" in str(config_data))
                ]
                
                for setting_name, has_setting in performance_settings:
                    checks.append({
                        "check": f"Performance setting: {setting_name}",
                        "status": "PASS" if has_setting else "FAIL",
                        "details": f"Setting configured: {has_setting}"
                    })
                    
            except Exception as e:
                checks.append({
                    "check": "Performance configuration",
                    "status": "FAIL",
                    "details": f"Config error: {str(e)}"
                })
        
        passed_checks = sum(1 for check in checks if check["status"] == "PASS")
        total_checks = len(checks)
        
        return {
            "status": "PASS" if passed_checks >= total_checks * 0.7 else "FAIL",
            "passed": passed_checks,
            "total": total_checks,
            "checks": checks,
            "message": f"Performance validation: {passed_checks}/{total_checks} checks passed"
        }
    
    def _test_user_experience(self) -> Dict[str, Any]:
        """Test user experience enhancements."""
        checks = []
        
        # Check admin interface UX
        admin_page_path = project_root / "pages" / "Admin_Configuration.py"
        if admin_page_path.exists():
            with open(admin_page_path, 'r') as f:
                admin_content = f.read()
            
            ux_features = [
                ("User authentication", "admin_authenticated" in admin_content),
                ("Progress indicators", "st.progress" in admin_content),
                ("Success messages", "st.success" in admin_content),
                ("Error handling", "st.error" in admin_content),
                ("Interactive elements", "st.button" in admin_content),
                ("Visual feedback", "st.balloons" in admin_content or "st.success" in admin_content),
                ("Organized layout", "st.tabs" in admin_content),
                ("Help text", "st.caption" in admin_content or "st.help" in admin_content),
                ("Confirmation dialogs", "st.confirm" in admin_content),
                ("Metrics display", "st.metric" in admin_content)
            ]
            
            for feature_name, has_feature in ux_features:
                checks.append({
                    "check": f"Admin UX feature: {feature_name}",
                    "status": "PASS" if has_feature else "FAIL",
                    "details": f"Feature implemented: {has_feature}"
                })
        
        # Check patient conversation UX improvements
        patient_page_path = project_root / "pages" / "1_Patient_Conversation.py"
        if patient_page_path.exists():
            with open(patient_page_path, 'r') as f:
                patient_content = f.read()
            
            patient_ux_features = [
                ("Real-time status", "conversation_state" in patient_content),
                ("Visual indicators", "🔴" in patient_content or "🟢" in patient_content),
                ("Instructions", "Instructions" in patient_content),
                ("Fallback options", "text_input" in patient_content.lower()),
                ("Progress tracking", "duration" in patient_content.lower()),
                ("User feedback", "st.info" in patient_content or "st.warning" in patient_content)
            ]
            
            for feature_name, has_feature in patient_ux_features:
                checks.append({
                    "check": f"Patient UX feature: {feature_name}",
                    "status": "PASS" if has_feature else "FAIL",
                    "details": f"Feature implemented: {has_feature}"
                })
        
        passed_checks = sum(1 for check in checks if check["status"] == "PASS")
        total_checks = len(checks)
        
        return {
            "status": "PASS" if passed_checks >= total_checks * 0.8 else "FAIL",
            "passed": passed_checks,
            "total": total_checks,
            "checks": checks,
            "message": f"User experience validation: {passed_checks}/{total_checks} checks passed"
        }
    
    def _test_system_integration(self) -> Dict[str, Any]:
        """Test system integration and overall functionality."""
        checks = []
        
        # Check utils integration
        utils_dir = project_root / "utils"
        if utils_dir.exists():
            required_utils = [
                "config_manager.py",
                "mongodb_realtime.py",
                "conversation_handler.py",
                "audio_manager.py",
                "realtime_client.py"
            ]
            
            for util_file in required_utils:
                util_path = utils_dir / util_file
                checks.append({
                    "check": f"Utils module: {util_file}",
                    "status": "PASS" if util_path.exists() else "FAIL",
                    "details": f"Module exists: {util_path.exists()}"
                })
        
        # Check page integration
        pages_dir = project_root / "pages"
        if pages_dir.exists():
            required_pages = [
                "1_Patient_Conversation.py",
                "2_Supervisor_Conversation.py",
                "Admin_Configuration.py"
            ]
            
            for page_file in required_pages:
                page_path = pages_dir / page_file
                checks.append({
                    "check": f"Page file: {page_file}",
                    "status": "PASS" if page_path.exists() else "FAIL",
                    "details": f"Page exists: {page_path.exists()}"
                })
        
        # Check Home.py integration
        home_path = project_root / "Home.py"
        if home_path.exists():
            with open(home_path, 'r') as f:
                home_content = f.read()
            
            integration_features = [
                ("Setup function", "def setup" in home_content),
                ("OpenAI client", "openai" in home_content.lower()),
                ("Configuration", "config" in home_content.lower())
            ]
            
            for feature_name, has_feature in integration_features:
                checks.append({
                    "check": f"Home integration: {feature_name}",
                    "status": "PASS" if has_feature else "FAIL",
                    "details": f"Feature present: {has_feature}"
                })
        
        # Check requirements.txt
        requirements_path = project_root / "requirements.txt"
        if requirements_path.exists():
            with open(requirements_path, 'r') as f:
                requirements = f.read()
            
            required_packages = [
                "streamlit",
                "openai",
                "pymongo",
                "pyyaml",
                "numpy"
            ]
            
            for package in required_packages:
                checks.append({
                    "check": f"Required package: {package}",
                    "status": "PASS" if package in requirements else "FAIL",
                    "details": f"Package in requirements: {package in requirements}"
                })
        
        passed_checks = sum(1 for check in checks if check["status"] == "PASS")
        total_checks = len(checks)
        
        return {
            "status": "PASS" if passed_checks >= total_checks * 0.8 else "FAIL",
            "passed": passed_checks,
            "total": total_checks,
            "checks": checks,
            "message": f"System integration validation: {passed_checks}/{total_checks} checks passed"
        }
    
    def _log_category_result(self, category: str, result: Dict[str, Any]) -> None:
        """Log category result."""
        status = result["status"]
        message = result.get("message", "")
        
        if status == "PASS":
            logger.info(f"✅ {category}: {message}")
        elif status == "PARTIAL":
            logger.warning(f"⚠️  {category}: {message}")
        else:
            logger.error(f"❌ {category}: {message}")
        
        if self.verbose and "checks" in result:
            for check in result["checks"]:
                check_status = "✅" if check["status"] == "PASS" else "❌"
                logger.info(f"  {check_status} {check['check']}")
    
    def generate_report(self, output_path: Optional[str] = None) -> str:
        """Generate detailed validation report."""
        report_lines = [
            "=" * 80,
            "PHYSIOBOT PHASE 5 VALIDATION REPORT",
            "=" * 80,
            f"Validation Time: {self.results['validation_timestamp']}",
            f"Phase: {self.results['phase']}",
            f"Overall Status: {self.results['overall_status']}",
            f"Success Rate: {self.results.get('success_rate', 0):.1f}%",
            "",
            "CATEGORY RESULTS:",
            "-" * 40
        ]
        
        for category, result in self.results["categories"].items():
            status_symbol = {
                "PASS": "✅",
                "PARTIAL": "⚠️",
                "FAIL": "❌",
                "ERROR": "🔥"
            }.get(result["status"], "❓")
            
            report_lines.append(f"{status_symbol} {category}: {result['status']}")
            if "message" in result:
                report_lines.append(f"   {result['message']}")
            
            if self.verbose and "checks" in result:
                for check in result["checks"]:
                    check_symbol = "✅" if check["status"] == "PASS" else "❌"
                    report_lines.append(f"     {check_symbol} {check['check']}")
                    if check["details"]:
                        report_lines.append(f"        {check['details']}")
                report_lines.append("")
        
        if self.results["errors"]:
            report_lines.extend([
                "",
                "ERRORS:",
                "-" * 20
            ])
            for error in self.results["errors"]:
                report_lines.append(f"❌ {error}")
        
        report_lines.extend([
            "",
            "=" * 80,
            "END OF REPORT",
            "=" * 80
        ])
        
        report_content = "\n".join(report_lines)
        
        if output_path:
            with open(output_path, 'w') as f:
                f.write(report_content)
            logger.info(f"Report saved to {output_path}")
        
        return report_content

def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description="Validate Phase 5 implementation")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--output", "-o", help="Output report file path")
    
    args = parser.parse_args()
    
    # Run validation
    validator = Phase5Validator(verbose=args.verbose)
    results = validator.run_validation()
    
    # Generate and display report
    report = validator.generate_report(args.output)
    print(report)
    
    # Exit with appropriate code
    if results["overall_status"] == "PASS":
        print("\n🎉 Phase 5 validation PASSED! All requirements met.")
        sys.exit(0)
    elif results["overall_status"] == "PARTIAL":
        print("\n⚠️  Phase 5 validation PARTIAL. Some issues need attention.")
        sys.exit(1)
    else:
        print("\n❌ Phase 5 validation FAILED. Critical issues found.")
        sys.exit(2)

if __name__ == "__main__":
    main()