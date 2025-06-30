import unittest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
import numpy as np
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.audio_manager import AudioManager

class TestAudioManager(unittest.TestCase):
    """Unit tests for AudioManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            'audio_settings': {
                'voice_type': 'alloy',
                'speech_speed': 1.0,
                'conversation_detection': {
                    'silence_threshold': 2.0,
                    'volume_threshold': 0.1
                },
                'quality_settings': {
                    'sample_rate': 24000,
                    'format': 'pcm16',
                    'chunk_size': 1024
                }
            }
        }
        self.audio_manager = AudioManager(self.config)
    
    def test_initialization(self):
        """Test AudioManager initialization."""
        self.assertIsNotNone(self.audio_manager)
        self.assertEqual(self.audio_manager.sample_rate, 24000)
        self.assertEqual(self.audio_manager.format, 'pcm16')
        self.assertEqual(self.audio_manager.chunk_size, 1024)
        self.assertFalse(self.audio_manager.is_recording)
        self.assertFalse(self.audio_manager.is_playing)
    
    def test_audio_settings(self):
        """Test getting audio settings."""
        settings = self.audio_manager.get_audio_settings()
        
        self.assertIn('sample_rate', settings)
        self.assertIn('chunk_size', settings)
        self.assertIn('format', settings)
        self.assertEqual(settings['sample_rate'], 24000)
        self.assertEqual(settings['format'], 'pcm16')
    
    def test_quality_metrics(self):
        """Test quality metrics functionality."""
        # Initial metrics should be zeros
        metrics = self.audio_manager.get_quality_metrics()
        self.assertEqual(metrics['signal_level'], 0.0)
        self.assertEqual(metrics['latency_ms'], 0.0)
        self.assertEqual(metrics['connection_quality'], 0.0)
        
        # Update metrics
        self.audio_manager.update_quality_metrics(50.0, 0.8)
        updated_metrics = self.audio_manager.get_quality_metrics()
        self.assertEqual(updated_metrics['latency_ms'], 50.0)
        self.assertEqual(updated_metrics['connection_quality'], 0.8)
    
    async def test_start_stop_recording(self):
        """Test recording start and stop functionality."""
        # Test start recording
        result = await self.audio_manager.start_recording()
        self.assertTrue(result)
        self.assertTrue(self.audio_manager.is_recording)
        
        # Test stop recording (should return None since no audio captured)
        audio_data = await self.audio_manager.stop_recording()
        self.assertIsNone(audio_data)
        self.assertFalse(self.audio_manager.is_recording)
    
    async def test_play_audio(self):
        """Test audio playback functionality."""
        # Test with empty audio data
        result = await self.audio_manager.play_audio(b'')
        self.assertFalse(result)
        
        # Test with valid audio data
        audio_data = b'\x00\x01\x02\x03'
        result = await self.audio_manager.play_audio(audio_data)
        self.assertTrue(result)
    
    def test_process_audio_chunk(self):
        """Test audio chunk processing."""
        # Create test audio data (16-bit PCM)
        audio_data = np.random.randint(-32768, 32767, 1024, dtype=np.int16).tobytes()
        
        # Process the chunk
        result = self.audio_manager.process_audio_chunk(audio_data)
        
        self.assertIn('volume_level', result)
        self.assertIn('is_speech', result)
        self.assertIn('chunk_size', result)
        self.assertIn('quality_metrics', result)
        self.assertEqual(result['chunk_size'], len(audio_data))
        self.assertIsInstance(result['volume_level'], float)
        self.assertIsInstance(result['is_speech'], bool)
    
    def test_audio_encoding_decoding(self):
        """Test audio encoding and decoding for API transmission."""
        # Create test audio data
        audio_data = b'\x00\x01\x02\x03\x04\x05'
        
        # Encode
        encoded = self.audio_manager.encode_audio_for_api(audio_data)
        self.assertIsInstance(encoded, str)
        
        # Decode
        decoded = self.audio_manager.decode_audio_from_api(encoded)
        self.assertEqual(decoded, audio_data)
    
    def test_callbacks(self):
        """Test callback functionality."""
        # Set up mock callbacks
        volume_callback = Mock()
        quality_callback = Mock()
        
        self.audio_manager.set_callbacks(
            on_volume_level=volume_callback,
            on_quality_update=quality_callback
        )
        
        # Trigger volume callback
        test_volume = 0.5
        if self.audio_manager.on_volume_level:
            self.audio_manager.on_volume_level(test_volume)
        volume_callback.assert_called_once_with(test_volume)
        
        # Trigger quality callback
        test_metrics = {'latency_ms': 100.0, 'connection_quality': 0.9}
        self.audio_manager.update_quality_metrics(100.0, 0.9)
        # The callback should be called internally by update_quality_metrics
    
    def test_reset(self):
        """Test reset functionality."""
        # Set some state
        self.audio_manager.is_recording = True
        self.audio_manager.is_connected = True
        self.audio_manager.audio_chunks = [b'test']
        
        # Reset
        self.audio_manager.reset()
        
        # Check state is cleared
        self.assertFalse(self.audio_manager.is_recording)
        self.assertFalse(self.audio_manager.is_connected)
        self.assertEqual(len(self.audio_manager.audio_chunks), 0)
        
        # Check quality metrics are reset
        metrics = self.audio_manager.get_quality_metrics()
        self.assertEqual(metrics['signal_level'], 0.0)
        self.assertEqual(metrics['latency_ms'], 0.0)

class TestAudioManagerAsync(unittest.IsolatedAsyncioTestCase):
    """Async tests for AudioManager class."""
    
    async def asyncSetUp(self):
        """Set up async test fixtures."""
        self.config = {
            'audio_settings': {
                'quality_settings': {
                    'sample_rate': 24000,
                    'format': 'pcm16'
                },
                'conversation_detection': {
                    'volume_threshold': 0.1
                }
            }
        }
        self.audio_manager = AudioManager(self.config)
    
    async def test_recording_with_audio_data(self):
        """Test recording with simulated audio data."""
        # Start recording
        await self.audio_manager.start_recording()
        self.assertTrue(self.audio_manager.is_recording)
        
        # Simulate processing audio chunks
        test_chunk = np.random.randint(-32768, 32767, 512, dtype=np.int16).tobytes()
        result = self.audio_manager.process_audio_chunk(test_chunk)
        
        self.assertEqual(len(self.audio_manager.audio_chunks), 1)
        self.assertEqual(result['chunk_size'], len(test_chunk))
        
        # Stop recording
        audio_data = await self.audio_manager.stop_recording()
        self.assertIsNotNone(audio_data)
        if audio_data is not None:
            self.assertEqual(len(audio_data), len(test_chunk))
    
    async def test_multiple_recording_attempts(self):
        """Test handling multiple recording start attempts."""
        # Start recording
        result1 = await self.audio_manager.start_recording()
        self.assertTrue(result1)
        
        # Try to start again (should return True but log warning)
        result2 = await self.audio_manager.start_recording()
        self.assertTrue(result2)
        
        # Stop recording
        await self.audio_manager.stop_recording()

if __name__ == '__main__':
    # Run the tests
    unittest.main()