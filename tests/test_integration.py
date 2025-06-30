import unittest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.audio_manager import AudioManager
from utils.conversation_handler import ConversationHandler, ConversationState
from utils.config_manager import ConfigManager

class TestAudioInfrastructureIntegration(unittest.IsolatedAsyncioTestCase):
    """Integration tests for audio infrastructure components."""
    
    async def asyncSetUp(self):
        """Set up test fixtures."""
        # Use config manager to load configuration
        self.config_manager = ConfigManager("config.yaml")
        self.config = self.config_manager.config
        
        # Mock API key for testing
        self.api_key = "test-api-key"
    
    def test_config_manager_audio_settings(self):
        """Test that config manager provides proper audio settings."""
        audio_settings = self.config_manager.get_audio_settings()
        
        self.assertIn('voice_type', audio_settings)
        self.assertIn('speech_speed', audio_settings)
        self.assertIn('quality_settings', audio_settings)
        
        quality_settings = audio_settings['quality_settings']
        self.assertIn('sample_rate', quality_settings)
        self.assertIn('format', quality_settings)
    
    def test_audio_manager_with_config(self):
        """Test AudioManager initialization with real config."""
        audio_manager = AudioManager(self.config)
        
        # Check that settings are applied correctly
        settings = audio_manager.get_audio_settings()
        expected_sample_rate = self.config['audio_settings']['quality_settings']['sample_rate']
        self.assertEqual(settings['sample_rate'], expected_sample_rate)
    
    @patch('utils.realtime_client.websockets.connect')
    async def test_conversation_handler_initialization(self, mock_websocket_connect):
        """Test ConversationHandler initialization and component integration."""
        # Mock the websocket connection to avoid actual API calls
        mock_websocket = AsyncMock()
        mock_websocket_connect.return_value = mock_websocket
        
        # Create conversation handler
        conversation_handler = ConversationHandler(self.config, self.api_key)
        
        # Verify initial state
        self.assertEqual(conversation_handler.state, ConversationState.IDLE)
        self.assertIsNotNone(conversation_handler.audio_manager)
        self.assertIsNotNone(conversation_handler.realtime_client)
        
        # Verify configuration is passed correctly
        audio_settings = conversation_handler.audio_manager.get_audio_settings()
        self.assertEqual(
            audio_settings['sample_rate'],
            self.config['audio_settings']['quality_settings']['sample_rate']
        )
    
    def test_conversation_state_transitions(self):
        """Test conversation state management."""
        conversation_handler = ConversationHandler(self.config, self.api_key)
        
        # Test initial state
        self.assertEqual(conversation_handler.state, ConversationState.IDLE)
        
        # Test state change
        conversation_handler._change_state(ConversationState.CONNECTING)
        self.assertEqual(conversation_handler.state, ConversationState.CONNECTING)
        
        # Test status retrieval
        status = conversation_handler.get_conversation_status()
        self.assertEqual(status['state'], ConversationState.CONNECTING.value)
        self.assertIn('duration_seconds', status)
        self.assertIn('response_count', status)
    
    def test_audio_quality_metrics_integration(self):
        """Test that quality metrics flow between components."""
        audio_manager = AudioManager(self.config)
        
        # Update quality metrics
        audio_manager.update_quality_metrics(75.0, 0.95)
        
        # Verify metrics are accessible
        metrics = audio_manager.get_quality_metrics()
        self.assertEqual(metrics['latency_ms'], 75.0)
        self.assertEqual(metrics['connection_quality'], 0.95)
    
    def test_configuration_validation(self):
        """Test configuration validation across components."""
        # Test valid configuration
        errors = self.config_manager.validate_config()
        self.assertEqual(len(errors), 0, f"Configuration validation failed: {errors}")
        
        # Test audio settings validation specifically
        audio_settings = self.config_manager.get_audio_settings()
        voice_type = audio_settings.get('voice_type')
        valid_voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
        self.assertIn(voice_type, valid_voices)
        
        speech_speed = audio_settings.get('speech_speed', 1.0)
        self.assertIsInstance(speech_speed, (int, float))
        self.assertTrue(0.25 <= speech_speed <= 4.0)
    
    async def test_callback_integration(self):
        """Test that callbacks work across component boundaries."""
        conversation_handler = ConversationHandler(self.config, self.api_key)
        
        # Set up callback tracking
        state_changes = []
        transcript_updates = []
        audio_levels = []
        
        def track_state_change(old_state, new_state):
            state_changes.append((old_state, new_state))
        
        def track_transcript_update(transcript, speaker, is_complete):
            transcript_updates.append((transcript, speaker, is_complete))
        
        def track_audio_level(level):
            audio_levels.append(level)
        
        # Set callbacks
        conversation_handler.set_callbacks(
            on_state_change=track_state_change,
            on_transcript_update=track_transcript_update,
            on_audio_level=track_audio_level
        )
        
        # Trigger state change
        conversation_handler._change_state(ConversationState.CONNECTING)
        
        # Verify callback was called
        self.assertEqual(len(state_changes), 1)
        self.assertEqual(state_changes[0][1], ConversationState.CONNECTING.value)
        
        # Trigger volume level update through audio manager callback mechanism
        if conversation_handler.audio_manager.on_volume_level:
            conversation_handler.audio_manager.on_volume_level(0.6)
        
        # Verify audio level callback was called
        self.assertEqual(len(audio_levels), 1)
        self.assertEqual(audio_levels[0], 0.6)
    
    def test_error_handling_integration(self):
        """Test error handling across components."""
        conversation_handler = ConversationHandler(self.config, self.api_key)
        
        # Set up error tracking
        errors = []
        
        def track_errors(error_message):
            errors.append(error_message)
        
        conversation_handler.set_callbacks(on_error=track_errors)
        
        # Reset to clear any initialization state
        conversation_handler.reset()
        
        # Verify reset worked
        self.assertEqual(conversation_handler.state, ConversationState.IDLE)
        self.assertEqual(len(conversation_handler.transcript_segments), 0)
    
    def test_transcript_management(self):
        """Test transcript management functionality."""
        conversation_handler = ConversationHandler(self.config, self.api_key)
        
        # Add transcript segments
        conversation_handler._add_transcript_segment("user", "Hello", "text")
        conversation_handler._add_transcript_segment("assistant", "Hi there!", "audio")
        
        # Verify transcript retrieval
        transcript = conversation_handler.get_transcript()
        self.assertEqual(len(transcript), 2)
        self.assertEqual(transcript[0]['speaker'], "user")
        self.assertEqual(transcript[0]['text'], "Hello")
        self.assertEqual(transcript[1]['speaker'], "assistant")
        self.assertEqual(transcript[1]['text'], "Hi there!")

class TestConfigurationIntegration(unittest.TestCase):
    """Test configuration integration across components."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config_manager = ConfigManager("config.yaml")
    
    def test_audio_configuration_consistency(self):
        """Test that audio configuration is consistent across components."""
        config = self.config_manager.config
        
        # Create components with same config
        audio_manager = AudioManager(config)
        
        # Verify consistent sample rate
        expected_sample_rate = config['audio_settings']['quality_settings']['sample_rate']
        self.assertEqual(audio_manager.sample_rate, expected_sample_rate)
        
        # Verify format consistency
        expected_format = config['audio_settings']['quality_settings']['format']
        self.assertEqual(audio_manager.format, expected_format)
    
    def test_conversation_limits_configuration(self):
        """Test conversation limits are properly configured."""
        config = self.config_manager.config
        conversation_handler = ConversationHandler(config, "test-key")
        
        # Check that limits are set from config
        expected_max_duration = config['conversation_settings']['max_duration']
        expected_max_responses = config['conversation_settings']['max_responses']
        
        self.assertEqual(conversation_handler.max_duration, expected_max_duration)
        self.assertEqual(conversation_handler.max_responses, expected_max_responses)
    
    def test_openai_configuration_integration(self):
        """Test OpenAI configuration integration."""
        config = self.config_manager.config
        openai_settings = self.config_manager.get_openai_realtime_settings()
        
        # Verify required settings are present
        self.assertIn('model', openai_settings)
        self.assertIn('voice', openai_settings)
        self.assertIn('input_audio_format', openai_settings)
        self.assertIn('output_audio_format', openai_settings)
        
        # Verify format consistency with audio settings
        audio_format = config['audio_settings']['quality_settings']['format']
        self.assertEqual(openai_settings['input_audio_format'], audio_format)
        self.assertEqual(openai_settings['output_audio_format'], audio_format)

if __name__ == '__main__':
    unittest.main()