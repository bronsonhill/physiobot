import asyncio
import logging
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime, timezone
import time
from enum import Enum

from .audio_manager import AudioManager
from .realtime_client import RealtimeClient
from .config_manager import ConfigManager

logger = logging.getLogger(__name__)

class ConversationState(Enum):
    """Enumeration of conversation states."""
    IDLE = "idle"
    CONNECTING = "connecting"
    WAITING_FOR_USER = "waiting_for_user"
    USER_SPEAKING = "user_speaking"
    PROCESSING = "processing"
    AI_RESPONDING = "ai_responding"
    COMPLETED = "completed"
    ERROR = "error"

class ConversationHandler:
    """
    Manages conversation flow and coordinates between audio manager and realtime client.
    Handles conversation state, timing, and transcript management.
    """
    
    def __init__(self, config: Dict[str, Any], api_key: str):
        """
        Initialize conversation handler.
        
        Args:
            config: Configuration dictionary
            api_key: OpenAI API key
        """
        self.config = config
        self.api_key = api_key
        
        # Initialize components
        self.audio_manager = AudioManager(config)
        self.realtime_client = RealtimeClient(api_key, config)
        
        # Conversation state
        self.state = ConversationState.IDLE
        self.session_id: Optional[str] = None
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        
        # Configuration
        self.conversation_settings = config.get('conversation_settings', {})
        self.max_duration = self.conversation_settings.get('max_duration', 1800)  # 30 minutes
        self.max_responses = self.conversation_settings.get('max_responses', 50)
        self.auto_save_interval = self.conversation_settings.get('auto_save_interval', 300)  # 5 minutes
        
        # Transcript and timing
        self.transcript_segments: List[Dict[str, Any]] = []
        self.response_count = 0
        self.last_auto_save = time.time()
        
        # Callbacks
        self.on_state_change: Optional[Callable] = None
        self.on_transcript_update: Optional[Callable] = None
        self.on_audio_level: Optional[Callable] = None
        self.on_error: Optional[Callable] = None
        self.on_conversation_complete: Optional[Callable] = None
        
        # Setup callbacks
        self._setup_callbacks()
        
        logger.info("ConversationHandler initialized")
    
    def _setup_callbacks(self) -> None:
        """Setup callbacks between components."""
        # Audio manager callbacks
        self.audio_manager.set_callbacks(
            on_volume_level=self._on_volume_level,
            on_quality_update=self._on_audio_quality_update
        )
        
        # Realtime client callbacks
        self.realtime_client.set_callbacks(
            on_audio_response=self._on_audio_response,
            on_transcript=self._on_transcript_update,
            on_error=self._on_realtime_error,
            on_conversation_item=self._on_conversation_item,
            on_response_done=self._on_response_done
        )
    
    async def start_conversation(self, instructions: Optional[str] = None) -> bool:
        """
        Start a new conversation.
        
        Args:
            instructions: Optional initial instructions for the assistant
            
        Returns:
            True if conversation started successfully, False otherwise
        """
        if self.state != ConversationState.IDLE:
            logger.warning(f"Cannot start conversation in state: {self.state}")
            return False
        
        try:
            self._change_state(ConversationState.CONNECTING)
            
            # Connect to realtime API
            if not await self.realtime_client.connect():
                self._change_state(ConversationState.ERROR)
                return False
            
            # Update instructions if provided
            if instructions:
                await self.realtime_client.update_session_instructions(instructions)
            
            # Initialize conversation state
            self.session_id = self.realtime_client.session_id
            self.start_time = datetime.now(timezone.utc)
            self.transcript_segments.clear()
            self.response_count = 0
            self.last_auto_save = time.time()
            
            self._change_state(ConversationState.WAITING_FOR_USER)
            
            logger.info(f"Conversation started with session_id: {self.session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start conversation: {e}")
            self._change_state(ConversationState.ERROR)
            if self.on_error:
                await self._safe_callback(self.on_error, str(e))
            return False
    
    async def start_recording(self) -> bool:
        """
        Start recording user audio.
        
        Returns:
            True if recording started successfully, False otherwise
        """
        if self.state != ConversationState.WAITING_FOR_USER:
            logger.warning(f"Cannot start recording in state: {self.state}")
            return False
        
        try:
            if await self.audio_manager.start_recording():
                self._change_state(ConversationState.USER_SPEAKING)
                return True
            else:
                return False
        except Exception as e:
            logger.error(f"Failed to start recording: {e}")
            return False
    
    async def stop_recording(self) -> bool:
        """
        Stop recording and send audio to API.
        
        Returns:
            True if audio sent successfully, False otherwise
        """
        if self.state != ConversationState.USER_SPEAKING:
            logger.warning(f"Cannot stop recording in state: {self.state}")
            return False
        
        try:
            self._change_state(ConversationState.PROCESSING)
            
            # Stop recording and get audio data
            audio_data = await self.audio_manager.stop_recording()
            if not audio_data:
                self._change_state(ConversationState.WAITING_FOR_USER)
                return False
            
            # Send audio to realtime API
            if await self.realtime_client.send_audio(audio_data):
                # Commit audio buffer to trigger response
                if await self.realtime_client.commit_audio():
                    self._change_state(ConversationState.AI_RESPONDING)
                    return True
            
            self._change_state(ConversationState.WAITING_FOR_USER)
            return False
            
        except Exception as e:
            logger.error(f"Failed to stop recording: {e}")
            self._change_state(ConversationState.ERROR)
            return False
    
    async def send_text_message(self, text: str) -> bool:
        """
        Send a text message to the conversation.
        
        Args:
            text: Text message to send
            
        Returns:
            True if message sent successfully, False otherwise
        """
        if self.state != ConversationState.WAITING_FOR_USER:
            logger.warning(f"Cannot send text in state: {self.state}")
            return False
        
        try:
            self._change_state(ConversationState.PROCESSING)
            
            if await self.realtime_client.send_text(text):
                self._change_state(ConversationState.AI_RESPONDING)
                
                # Add user message to transcript
                self._add_transcript_segment("user", text, "text")
                return True
            else:
                self._change_state(ConversationState.WAITING_FOR_USER)
                return False
                
        except Exception as e:
            logger.error(f"Failed to send text message: {e}")
            self._change_state(ConversationState.ERROR)
            return False
    
    async def end_conversation(self) -> Dict[str, Any]:
        """
        End the current conversation and return summary.
        
        Returns:
            Dictionary with conversation summary
        """
        try:
            # Stop any ongoing audio operations
            self.audio_manager.stop_playback()
            if self.audio_manager.is_recording:
                await self.audio_manager.stop_recording()
            
            # Disconnect from realtime API
            await self.realtime_client.disconnect()
            
            # Record end time
            self.end_time = datetime.now(timezone.utc)
            
            # Calculate duration
            duration_seconds = 0
            if self.start_time and self.end_time:
                duration_seconds = (self.end_time - self.start_time).total_seconds()
            
            # Create conversation summary
            summary = {
                'session_id': self.session_id,
                'start_time': self.start_time,
                'end_time': self.end_time,
                'duration_seconds': duration_seconds,
                'response_count': self.response_count,
                'transcript_segments': self.transcript_segments.copy(),
                'final_state': self.state.value
            }
            
            self._change_state(ConversationState.COMPLETED)
            
            # Call completion callback
            if self.on_conversation_complete:
                await self._safe_callback(self.on_conversation_complete, summary)
            
            logger.info(f"Conversation ended after {duration_seconds:.1f} seconds")
            return summary
            
        except Exception as e:
            logger.error(f"Error ending conversation: {e}")
            self._change_state(ConversationState.ERROR)
            return {'error': str(e)}
    
    def reset(self) -> None:
        """Reset conversation handler to initial state."""
        # Reset components
        self.audio_manager.reset()
        
        # Reset state
        self.state = ConversationState.IDLE
        self.session_id = None
        self.start_time = None
        self.end_time = None
        self.transcript_segments.clear()
        self.response_count = 0
        self.last_auto_save = time.time()
        
        logger.info("ConversationHandler reset")
    
    def get_conversation_status(self) -> Dict[str, Any]:
        """
        Get current conversation status.
        
        Returns:
            Dictionary with current status information
        """
        duration_seconds = 0
        if self.start_time:
            duration_seconds = (datetime.now(timezone.utc) - self.start_time).total_seconds()
        
        return {
            'state': self.state.value,
            'session_id': self.session_id,
            'duration_seconds': duration_seconds,
            'response_count': self.response_count,
            'max_responses': self.max_responses,
            'max_duration': self.max_duration,
            'transcript_length': len(self.transcript_segments),
            'audio_quality': self.audio_manager.get_quality_metrics(),
            'connection_status': self.realtime_client.get_connection_status()
        }
    
    def get_transcript(self) -> List[Dict[str, Any]]:
        """Get current conversation transcript."""
        return self.transcript_segments.copy()
    
    async def _on_audio_response(self, audio_data: bytes) -> None:
        """Handle audio response from realtime client."""
        try:
            await self.audio_manager.play_audio(audio_data)
        except Exception as e:
            logger.error(f"Error playing audio response: {e}")
    
    async def _on_transcript_update(self, transcript: str, is_complete: bool) -> None:
        """Handle transcript updates from realtime client."""
        try:
            if is_complete:
                self._add_transcript_segment("assistant", transcript, "audio")
                
                # Check if we should trigger callback
                if self.on_transcript_update:
                    await self._safe_callback(self.on_transcript_update, transcript, "assistant", is_complete)
        except Exception as e:
            logger.error(f"Error handling transcript update: {e}")
    
    async def _on_response_done(self, response: Dict[str, Any]) -> None:
        """Handle response completion from realtime client."""
        try:
            self.response_count += 1
            
            # Check limits
            if self.response_count >= self.max_responses:
                logger.info("Maximum responses reached, ending conversation")
                await self.end_conversation()
                return
            
            # Check duration
            if self.start_time:
                duration = (datetime.now(timezone.utc) - self.start_time).total_seconds()
                if duration >= self.max_duration:
                    logger.info("Maximum duration reached, ending conversation")
                    await self.end_conversation()
                    return
            
            # Return to waiting state
            self._change_state(ConversationState.WAITING_FOR_USER)
            
            # Auto-save check
            current_time = time.time()
            if current_time - self.last_auto_save >= self.auto_save_interval:
                # Trigger auto-save (callback can be used to save to database)
                self.last_auto_save = current_time
                if self.on_transcript_update:
                    await self._safe_callback(self.on_transcript_update, "", "system", True)
            
        except Exception as e:
            logger.error(f"Error handling response completion: {e}")
    
    async def _on_conversation_item(self, item: Dict[str, Any]) -> None:
        """Handle new conversation item from realtime client."""
        # This can be used to track conversation items if needed
        pass
    
    async def _on_realtime_error(self, error: Dict[str, Any]) -> None:
        """Handle errors from realtime client."""
        error_message = error.get('message', 'Unknown realtime API error')
        logger.error(f"Realtime API error: {error_message}")
        
        self._change_state(ConversationState.ERROR)
        if self.on_error:
            await self._safe_callback(self.on_error, error_message)
    
    def _on_volume_level(self, volume_level: float) -> None:
        """Handle volume level updates from audio manager."""
        if self.on_audio_level:
            try:
                self.on_audio_level(volume_level)
            except Exception as e:
                logger.error(f"Error in audio level callback: {e}")
    
    def _on_audio_quality_update(self, quality_metrics: Dict[str, float]) -> None:
        """Handle audio quality updates from audio manager."""
        # This can be used to monitor and react to audio quality changes
        pass
    
    def _add_transcript_segment(self, speaker: str, text: str, input_type: str) -> None:
        """Add a segment to the conversation transcript."""
        segment = {
            'timestamp': datetime.now(timezone.utc),
            'speaker': speaker,
            'text': text,
            'input_type': input_type,
            'response_number': self.response_count if speaker == "assistant" else None
        }
        self.transcript_segments.append(segment)
    
    def _change_state(self, new_state: ConversationState) -> None:
        """Change conversation state and trigger callback."""
        old_state = self.state
        self.state = new_state
        
        logger.debug(f"State changed: {old_state.value} -> {new_state.value}")
        
        if self.on_state_change:
            try:
                self.on_state_change(old_state.value, new_state.value)
            except Exception as e:
                logger.error(f"Error in state change callback: {e}")
    
    async def _safe_callback(self, callback: Callable, *args) -> None:
        """Safely execute callback function."""
        try:
            if asyncio.iscoroutinefunction(callback):
                await callback(*args)
            else:
                callback(*args)
        except Exception as e:
            logger.error(f"Error in callback: {e}")
    
    def set_callbacks(self,
                     on_state_change: Optional[Callable] = None,
                     on_transcript_update: Optional[Callable] = None,
                     on_audio_level: Optional[Callable] = None,
                     on_error: Optional[Callable] = None,
                     on_conversation_complete: Optional[Callable] = None) -> None:
        """
        Set callback functions for conversation events.
        
        Args:
            on_state_change: Callback for state changes
            on_transcript_update: Callback for transcript updates
            on_audio_level: Callback for audio level changes
            on_error: Callback for error events
            on_conversation_complete: Callback for conversation completion
        """
        self.on_state_change = on_state_change
        self.on_transcript_update = on_transcript_update
        self.on_audio_level = on_audio_level
        self.on_error = on_error
        self.on_conversation_complete = on_conversation_complete