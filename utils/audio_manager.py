import asyncio
import logging
import numpy as np
import json
import base64
from typing import Optional, Callable, Dict, Any
import time
from pathlib import Path
import threading
from queue import Queue, Empty

logger = logging.getLogger(__name__)

class AudioManager:
    """
    Manages audio input/output for realtime conversation system.
    Handles audio capture, playback, and quality monitoring.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize audio manager with configuration.
        
        Args:
            config: Audio configuration dictionary
        """
        self.config = config
        self.audio_settings = config.get('audio_settings', {})
        self.quality_settings = self.audio_settings.get('quality_settings', {})
        
        # Audio state
        self.is_recording = False
        self.is_playing = False
        self.is_connected = False
        
        # Audio buffers and queues
        self.input_buffer = Queue()
        self.output_buffer = Queue()
        self.audio_chunks = []
        
        # Quality monitoring
        self.quality_metrics = {
            'signal_level': 0.0,
            'noise_level': 0.0,
            'connection_quality': 0.0,
            'latency_ms': 0.0
        }
        
        # Callbacks
        self.on_audio_data: Optional[Callable] = None
        self.on_volume_level: Optional[Callable] = None
        self.on_quality_update: Optional[Callable] = None
        
        # Audio parameters
        self.sample_rate = self.quality_settings.get('sample_rate', 24000)
        self.chunk_size = self.quality_settings.get('chunk_size', 1024)
        self.format = self.quality_settings.get('format', 'pcm16')
        
        # Detection settings
        detection_config = self.audio_settings.get('conversation_detection', {})
        self.silence_threshold = detection_config.get('silence_threshold', 2.0)
        self.volume_threshold = detection_config.get('volume_threshold', 0.1)
        
        logger.info(f"AudioManager initialized with sample_rate={self.sample_rate}, format={self.format}")
    
    async def start_recording(self) -> bool:
        """
        Start audio recording.
        
        Returns:
            True if recording started successfully, False otherwise
        """
        if self.is_recording:
            logger.warning("Recording already in progress")
            return True
        
        try:
            self.is_recording = True
            self.audio_chunks.clear()
            
            # Clear input buffer
            while not self.input_buffer.empty():
                try:
                    self.input_buffer.get_nowait()
                except Empty:
                    break
            
            logger.info("Audio recording started")
            return True
        except Exception as e:
            logger.error(f"Failed to start recording: {e}")
            self.is_recording = False
            return False
    
    async def stop_recording(self) -> Optional[bytes]:
        """
        Stop audio recording and return recorded data.
        
        Returns:
            Recorded audio data as bytes, or None if error
        """
        if not self.is_recording:
            logger.warning("No recording in progress")
            return None
        
        try:
            self.is_recording = False
            
            # Process accumulated audio chunks
            if self.audio_chunks:
                audio_data = b''.join(self.audio_chunks)
                self.audio_chunks.clear()
                
                logger.info(f"Recording stopped, captured {len(audio_data)} bytes")
                return audio_data
            else:
                logger.warning("No audio data captured")
                return None
        except Exception as e:
            logger.error(f"Failed to stop recording: {e}")
            return None
    
    async def play_audio(self, audio_data: bytes) -> bool:
        """
        Play audio data.
        
        Args:
            audio_data: Audio data to play
            
        Returns:
            True if playback started successfully, False otherwise
        """
        if not audio_data:
            logger.warning("No audio data provided for playback")
            return False
        
        try:
            self.is_playing = True
            
            # Add audio data to output buffer
            self.output_buffer.put(audio_data)
            
            logger.info(f"Started audio playback, {len(audio_data)} bytes")
            return True
        except Exception as e:
            logger.error(f"Failed to start audio playback: {e}")
            self.is_playing = False
            return False
    
    def stop_playback(self) -> bool:
        """
        Stop audio playback.
        
        Returns:
            True if playback stopped successfully, False otherwise
        """
        try:
            self.is_playing = False
            
            # Clear output buffer
            while not self.output_buffer.empty():
                try:
                    self.output_buffer.get_nowait()
                except Empty:
                    break
            
            logger.info("Audio playback stopped")
            return True
        except Exception as e:
            logger.error(f"Failed to stop playback: {e}")
            return False
    
    def process_audio_chunk(self, audio_data: bytes) -> Dict[str, Any]:
        """
        Process incoming audio chunk and update quality metrics.
        
        Args:
            audio_data: Raw audio data chunk
            
        Returns:
            Dictionary with processed audio info and quality metrics
        """
        try:
            if self.is_recording:
                self.audio_chunks.append(audio_data)
            
            # Convert to numpy array for analysis
            if self.format == 'pcm16':
                audio_array = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
            else:
                audio_array = np.frombuffer(audio_data, dtype=np.float32)
            
            # Calculate volume level
            volume_level = float(np.sqrt(np.mean(audio_array ** 2)))
            
            # Update quality metrics
            self.quality_metrics['signal_level'] = volume_level
            
            # Detect speech activity
            is_speech = volume_level > self.volume_threshold
            
            # Call volume callback if set
            if self.on_volume_level:
                try:
                    self.on_volume_level(volume_level)
                except Exception as e:
                    logger.error(f"Error in volume level callback: {e}")
            
            return {
                'volume_level': volume_level,
                'is_speech': is_speech,
                'chunk_size': len(audio_data),
                'quality_metrics': self.quality_metrics.copy()
            }
        except Exception as e:
            logger.error(f"Error processing audio chunk: {e}")
            return {
                'volume_level': 0.0,
                'is_speech': False,
                'chunk_size': 0,
                'quality_metrics': self.quality_metrics.copy()
            }
    
    def update_quality_metrics(self, latency_ms: float, connection_quality: float) -> None:
        """
        Update connection quality metrics.
        
        Args:
            latency_ms: Round-trip latency in milliseconds
            connection_quality: Connection quality score (0.0-1.0)
        """
        self.quality_metrics['latency_ms'] = latency_ms
        self.quality_metrics['connection_quality'] = connection_quality
        
        # Call quality update callback if set
        if self.on_quality_update:
            try:
                self.on_quality_update(self.quality_metrics.copy())
            except Exception as e:
                logger.error(f"Error in quality update callback: {e}")
    
    def get_quality_metrics(self) -> Dict[str, float]:
        """
        Get current audio quality metrics.
        
        Returns:
            Dictionary with current quality metrics
        """
        return self.quality_metrics.copy()
    
    def set_callbacks(self, 
                     on_audio_data: Optional[Callable] = None,
                     on_volume_level: Optional[Callable] = None,
                     on_quality_update: Optional[Callable] = None) -> None:
        """
        Set callback functions for audio events.
        
        Args:
            on_audio_data: Callback for audio data events
            on_volume_level: Callback for volume level updates
            on_quality_update: Callback for quality metric updates
        """
        self.on_audio_data = on_audio_data
        self.on_volume_level = on_volume_level
        self.on_quality_update = on_quality_update
    
    def reset(self) -> None:
        """Reset audio manager state."""
        self.stop_playback()
        self.is_recording = False
        self.is_connected = False
        
        # Clear buffers
        self.audio_chunks.clear()
        while not self.input_buffer.empty():
            try:
                self.input_buffer.get_nowait()
            except Empty:
                break
        while not self.output_buffer.empty():
            try:
                self.output_buffer.get_nowait()
            except Empty:
                break
        
        # Reset quality metrics
        self.quality_metrics = {
            'signal_level': 0.0,
            'noise_level': 0.0,
            'connection_quality': 0.0,
            'latency_ms': 0.0
        }
        
        logger.info("AudioManager reset")
    
    def get_audio_settings(self) -> Dict[str, Any]:
        """
        Get current audio settings.
        
        Returns:
            Dictionary with current audio settings
        """
        return {
            'sample_rate': self.sample_rate,
            'chunk_size': self.chunk_size,
            'format': self.format,
            'silence_threshold': self.silence_threshold,
            'volume_threshold': self.volume_threshold
        }
    
    def encode_audio_for_api(self, audio_data: bytes) -> str:
        """
        Encode audio data for API transmission.
        
        Args:
            audio_data: Raw audio data
            
        Returns:
            Base64 encoded audio data
        """
        return base64.b64encode(audio_data).decode('utf-8')
    
    def decode_audio_from_api(self, encoded_data: str) -> bytes:
        """
        Decode audio data from API.
        
        Args:
            encoded_data: Base64 encoded audio data
            
        Returns:
            Raw audio data bytes
        """
        return base64.b64decode(encoded_data)