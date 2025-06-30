#!/usr/bin/env python3
"""
Phase 4 Validation Script - Supervisor Conversation Implementation

This script validates the implementation of Phase 4 deliverables:
1. Audio-enabled supervisor conversation page
2. Audio-specific feedback integration
3. Audio analysis features (pace, speaking time ratios, quality metrics)
4. Enhanced conversation context integration
"""

import sys
import os
import importlib.util
from pathlib import Path
import json
from typing import Dict, Any, List, Optional
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class Phase4Validator:
    """Validates Phase 4 implementation components."""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.successes = []
        self.project_root = Path(__file__).parent.parent
    
    def validate_all(self) -> bool:
        """Run all validation checks."""
        logger.info("🔍 Starting Phase 4 validation...")
        
        # Core validation checks
        self.validate_file_structure()
        self.validate_module_imports()
        self.validate_supervisor_conversation_page()
        self.validate_audio_analysis_module()
        self.validate_enhanced_prompts()
        self.validate_database_integration()
        self.validate_ui_components()
        self.validate_configuration()
        
        # Display results
        self.display_results()
        
        return len(self.errors) == 0
    
    def validate_file_structure(self):
        """Validate required files and directories exist."""
        logger.info("📁 Validating file structure...")
        
        required_files = [
            'pages/2_Supervisor_Conversation.py',
            'utils/audio_analysis.py',
            'prompts/audio_supervisor_prompt.txt',
            'utils/conversation_handler.py',
            'utils/audio_manager.py',
            'utils/mongodb_realtime.py',
            'config.yaml'
        ]
        
        for file_path in required_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                self.successes.append(f"✅ Found: {file_path}")
            else:
                self.errors.append(f"❌ Missing: {file_path}")
    
    def validate_module_imports(self):
        """Validate that all required modules can be imported."""
        logger.info("📦 Validating module imports...")
        
        modules_to_test = [
            ('utils.audio_analysis', 'AudioConversationAnalyzer'),
            ('utils.conversation_handler', 'ConversationHandler'),
            ('utils.audio_manager', 'AudioManager'),
            ('utils.mongodb_realtime', 'log_audio_transcript'),
            ('utils.config_manager', 'ConfigManager')
        ]
        
        # Add project root to path for imports
        sys.path.insert(0, str(self.project_root))
        
        for module_name, class_or_function in modules_to_test:
            try:
                module = importlib.import_module(module_name)
                if hasattr(module, class_or_function):
                    self.successes.append(f"✅ Import successful: {module_name}.{class_or_function}")
                else:
                    self.errors.append(f"❌ Missing: {class_or_function} in {module_name}")
            except ImportError as e:
                self.errors.append(f"❌ Import failed: {module_name} - {str(e)}")
            except Exception as e:
                self.warnings.append(f"⚠️  Import warning: {module_name} - {str(e)}")
    
    def validate_supervisor_conversation_page(self):
        """Validate the enhanced supervisor conversation page."""
        logger.info("👨‍🏫 Validating supervisor conversation page...")
        
        supervisor_page_path = self.project_root / 'pages' / '2_Supervisor_Conversation.py'
        
        if not supervisor_page_path.exists():
            self.errors.append("❌ Supervisor conversation page not found")
            return
        
        with open(supervisor_page_path, 'r') as f:
            content = f.read()
        
        # Check for required imports
        required_imports = [
            'from utils.audio_analysis import AudioConversationAnalyzer',
            'from utils.conversation_handler import ConversationHandler',
            'import asyncio',
            'import json'
        ]
        
        for import_stmt in required_imports:
            if import_stmt in content:
                self.successes.append(f"✅ Import found: {import_stmt}")
            else:
                self.errors.append(f"❌ Missing import: {import_stmt}")
        
        # Check for required functions
        required_functions = [
            'get_patient_conversation_analysis',
            'create_enhanced_supervisor_prompt',
            'display_patient_conversation_summary',
            'display_audio_quality_metrics'
        ]
        
        for func_name in required_functions:
            if f"def {func_name}" in content:
                self.successes.append(f"✅ Function found: {func_name}")
            else:
                self.errors.append(f"❌ Missing function: {func_name}")
        
        # Check for audio conversation features
        audio_features = [
            'ConversationHandler',
            'AudioConversationAnalyzer',
            'start_recording',
            'stop_recording',
            'audio_analysis',
            'advanced_analysis'
        ]
        
        for feature in audio_features:
            if feature in content:
                self.successes.append(f"✅ Audio feature found: {feature}")
            else:
                self.warnings.append(f"⚠️  Audio feature missing: {feature}")
        
        # Check for UI enhancements
        ui_elements = [
            'st.columns',
            'st.metric',
            'st.expander',
            'st.progress',
            'supervisor-header',
            'audio-analysis-card'
        ]
        
        for element in ui_elements:
            if element in content:
                self.successes.append(f"✅ UI element found: {element}")
            else:
                self.warnings.append(f"⚠️  UI element missing: {element}")
    
    def validate_audio_analysis_module(self):
        """Validate the audio analysis module functionality."""
        logger.info("🔊 Validating audio analysis module...")
        
        analysis_module_path = self.project_root / 'utils' / 'audio_analysis.py'
        
        if not analysis_module_path.exists():
            self.errors.append("❌ Audio analysis module not found")
            return
        
        try:
            sys.path.insert(0, str(self.project_root))
            from utils.audio_analysis import AudioConversationAnalyzer, create_conversation_analysis_report
            
            # Test analyzer initialization
            analyzer = AudioConversationAnalyzer()
            self.successes.append("✅ AudioConversationAnalyzer initialized successfully")
            
            # Check for required methods
            required_methods = [
                'analyze_conversation',
                '_analyze_basic_metrics',
                '_analyze_communication_patterns',
                '_analyze_questions',
                '_analyze_pace_and_timing',
                '_analyze_language_quality',
                '_analyze_empathy_and_rapport',
                '_analyze_professional_communication'
            ]
            
            for method_name in required_methods:
                if hasattr(analyzer, method_name):
                    self.successes.append(f"✅ Method found: {method_name}")
                else:
                    self.errors.append(f"❌ Missing method: {method_name}")
            
            # Test with sample data
            sample_segments = [
                {
                    'timestamp': '2024-01-01T12:00:00',
                    'speaker': 'user',
                    'text': 'Hello, how are you feeling today?',
                    'input_type': 'audio'
                },
                {
                    'timestamp': '2024-01-01T12:00:05',
                    'speaker': 'assistant',
                    'text': 'I am feeling some pain in my lower back.',
                    'input_type': 'audio'
                }
            ]
            
            analysis_result = analyzer.analyze_conversation(sample_segments, 300)  # 5 minutes
            
            if 'error' not in analysis_result:
                self.successes.append("✅ Audio analysis test successful")
                
                # Check for required analysis components
                required_components = [
                    'basic_metrics',
                    'communication_patterns',
                    'question_analysis',
                    'pace_analysis',
                    'language_quality',
                    'empathy_analysis',
                    'professional_analysis',
                    'overall_assessment'
                ]
                
                for component in required_components:
                    if component in analysis_result:
                        self.successes.append(f"✅ Analysis component: {component}")
                    else:
                        self.errors.append(f"❌ Missing analysis component: {component}")
            else:
                self.errors.append(f"❌ Audio analysis test failed: {analysis_result['error']}")
            
            # Test report generation
            try:
                report = create_conversation_analysis_report(analysis_result)
                if report and len(report) > 100:  # Reasonable report length
                    self.successes.append("✅ Analysis report generation successful")
                else:
                    self.warnings.append("⚠️  Analysis report seems too short")
            except Exception as e:
                self.errors.append(f"❌ Report generation failed: {str(e)}")
                
        except Exception as e:
            self.errors.append(f"❌ Audio analysis module validation failed: {str(e)}")
    
    def validate_enhanced_prompts(self):
        """Validate the enhanced audio supervisor prompt."""
        logger.info("📝 Validating enhanced prompts...")
        
        prompt_path = self.project_root / 'prompts' / 'audio_supervisor_prompt.txt'
        
        if not prompt_path.exists():
            self.errors.append("❌ Audio supervisor prompt not found")
            return
        
        with open(prompt_path, 'r') as f:
            prompt_content = f.read()
        
        # Check for required sections
        required_sections = [
            'Clinical Assessment Feedback',
            'Audio Communication Skills Feedback',
            'Pace and Speaking Rhythm',
            'Tone and Vocal Empathy',
            'Clarity and Articulation',
            'Active Listening Demonstration',
            'Response Timing and Turn-Taking',
            'Conversation Analysis Integration',
            'Response Structure and Guidelines'
        ]
        
        for section in required_sections:
            if section in prompt_content:
                self.successes.append(f"✅ Prompt section found: {section}")
            else:
                self.warnings.append(f"⚠️  Prompt section missing: {section}")
        
        # Check for audio-specific keywords
        audio_keywords = [
            'pace', 'rhythm', 'tone', 'empathy', 'clarity', 'articulation',
            'listening', 'timing', 'turn-taking', 'rapport', 'fluency',
            'filler words', 'speech', 'vocal', 'audio'
        ]
        
        found_keywords = sum(1 for keyword in audio_keywords if keyword.lower() in prompt_content.lower())
        
        if found_keywords >= len(audio_keywords) * 0.8:  # 80% of keywords found
            self.successes.append(f"✅ Audio keywords coverage: {found_keywords}/{len(audio_keywords)}")
        else:
            self.warnings.append(f"⚠️  Low audio keywords coverage: {found_keywords}/{len(audio_keywords)}")
        
        # Check prompt length (should be comprehensive)
        if len(prompt_content) > 2000:  # Reasonable length for comprehensive prompt
            self.successes.append("✅ Prompt length adequate")
        else:
            self.warnings.append("⚠️  Prompt may be too short")
    
    def validate_database_integration(self):
        """Validate database integration for supervisor conversations."""
        logger.info("🗄️  Validating database integration...")
        
        try:
            sys.path.insert(0, str(self.project_root))
            from utils.mongodb_realtime import log_audio_transcript
            
            self.successes.append("✅ Database module import successful")
            
            # Check for required functions
            required_functions = [
                'log_audio_transcript',
                'get_conversation_history',  
                'update_session_metadata'
            ]
            
            from utils import mongodb_realtime
            
            for func_name in required_functions:
                if hasattr(mongodb_realtime, func_name):
                    self.successes.append(f"✅ Database function found: {func_name}")
                else:
                    self.warnings.append(f"⚠️  Database function missing: {func_name}")
                    
        except Exception as e:
            self.errors.append(f"❌ Database integration validation failed: {str(e)}")
    
    def validate_ui_components(self):
        """Validate UI components and styling."""
        logger.info("🎨 Validating UI components...")
        
        supervisor_page_path = self.project_root / 'pages' / '2_Supervisor_Conversation.py'
        
        if supervisor_page_path.exists():
            with open(supervisor_page_path, 'r') as f:
                content = f.read()
            
            # Check for CSS styling
            css_classes = [
                'supervisor-header',
                'audio-analysis-card',
                'feedback-section',
                'patient-context-card',
                'quality-metric'
            ]
            
            for css_class in css_classes:
                if css_class in content:
                    self.successes.append(f"✅ CSS class found: {css_class}")
                else:
                    self.warnings.append(f"⚠️  CSS class missing: {css_class}")
            
            # Check for Streamlit components
            streamlit_components = [
                'st.columns',
                'st.metric',
                'st.expander',
                'st.progress',
                'st.button',
                'st.markdown',
                'st.info',
                'st.success',
                'st.error'
            ]
            
            for component in streamlit_components:
                if component in content:
                    self.successes.append(f"✅ Streamlit component found: {component}")
                else:
                    self.warnings.append(f"⚠️  Streamlit component missing: {component}")
        
        else:
            self.errors.append("❌ Cannot validate UI components - supervisor page not found")
    
    def validate_configuration(self):
        """Validate configuration settings for Phase 4."""
        logger.info("⚙️  Validating configuration...")
        
        config_path = self.project_root / 'config.yaml'
        
        if not config_path.exists():
            self.errors.append("❌ Configuration file not found")
            return
        
        try:
            import yaml
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            # Check for required configuration sections
            required_sections = [
                'audio_settings',
                'conversation_settings',
                'ui_settings',
                'database_settings'
            ]
            
            for section in required_sections:
                if section in config:
                    self.successes.append(f"✅ Config section found: {section}")
                else:
                    self.errors.append(f"❌ Missing config section: {section}")
            
            # Check specific audio settings
            if 'audio_settings' in config:
                audio_settings = config['audio_settings']
                required_audio_settings = [
                    'voice_type',
                    'speech_speed',
                    'conversation_detection',
                    'quality_settings'
                ]
                
                for setting in required_audio_settings:
                    if setting in audio_settings:
                        self.successes.append(f"✅ Audio setting found: {setting}")
                    else:
                        self.warnings.append(f"⚠️  Audio setting missing: {setting}")
                        
        except Exception as e:
            self.errors.append(f"❌ Configuration validation failed: {str(e)}")
    
    def display_results(self):
        """Display validation results."""
        print("\n" + "="*60)
        print("📊 PHASE 4 VALIDATION RESULTS")
        print("="*60)
        
        if self.successes:
            print(f"\n🎉 SUCCESSES ({len(self.successes)}):")
            for success in self.successes:
                print(f"  {success}")
        
        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  {warning}")
        
        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"  {error}")
        
        print("\n" + "="*60)
        print("📈 SUMMARY:")
        print(f"  ✅ Successes: {len(self.successes)}")
        print(f"  ⚠️  Warnings: {len(self.warnings)}")
        print(f"  ❌ Errors: {len(self.errors)}")
        
        if len(self.errors) == 0:
            print("\n🎊 PHASE 4 VALIDATION PASSED!")
            print("✨ All core components are properly implemented.")
            if self.warnings:
                print("⚠️  Please review warnings for optimal implementation.")
        else:
            print("\n🚨 PHASE 4 VALIDATION FAILED!")
            print("❌ Please fix the errors above before proceeding.")
        
        print("="*60)

def main():
    """Main validation function."""
    validator = Phase4Validator()
    success = validator.validate_all()
    
    if success:
        print("\n🎯 Phase 4 implementation validation completed successfully!")
        print("🚀 The supervisor conversation with audio analysis is ready for testing.")
    else:
        print("\n🔧 Please address the validation errors and run the script again.")
        sys.exit(1)

if __name__ == "__main__":
    main()