import asyncio
import time
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from utils.config_manager import ConfigManager
from utils.realtime_client import RealtimeClient
from utils.audio_manager import AudioManager

class ConversationHandler:
    def __init__(self, config_manager: ConfigManager, api_key: str):
        self.config_manager = config_manager
        self.conversation_settings = config_manager.get_conversation_settings()
        
        # Initialize components
        self.realtime_client = RealtimeClient(api_key, config_manager)
        self.audio_manager = AudioManager(config_manager)
        
        # Conversation state
        self.is_active = False
        self.is_paused = False
        self.start_time: Optional[float] = None
        self.conversation_history: List[Dict[str, Any]] = []
        self.current_transcript = {"user": "", "assistant": ""}
        self.response_counter = 0
        self.max_responses = self.conversation_settings.get("max_responses", 1000)
        self.max_duration = self.conversation_settings.get("max_duration", 1800)
        
        # Callbacks
        self.on_transcript_update: Optional[Callable] = None
        self.on_conversation_finished: Optional[Callable] = None
        self.on_error: Optional[Callable] = None
        
        # Set up realtime client callbacks
        self.realtime_client.set_callbacks(
            on_audio_received=self._handle_audio_received,
            on_transcript_received=self._handle_transcript_received,
            on_error=self._handle_error
        )
    
    async def start_conversation(self, patient_prompt: str) -> bool:
        """Start a new conversation with the patient"""
        try:
            # Connect to OpenAI Realtime API
            if not await self.realtime_client.connect():
                return False
            
            # Update session with patient prompt
            await self.realtime_client.update_session_instructions(patient_prompt)
            
            # Initialize conversation state
            self.is_active = True
            self.is_paused = False
            self.start_time = time.time()
            self.conversation_history = []
            self.current_transcript = {"user": "", "assistant": ""}
            self.response_counter = 0
            
            # Update audio manager status
            self.audio_manager.update_status("Ready to start conversation")
            
            return True
            
        except Exception as e:
            print(f"Error starting conversation: {e}")
            if self.on_error:
                self.on_error(f"Failed to start conversation: {e}")
            return False
    
    async def end_conversation(self) -> Dict[str, Any]:
        """End the current conversation and return conversation data"""
        try:
            self.is_active = False
            
            # Disconnect from realtime API
            await self.realtime_client.disconnect()
            
            # Calculate conversation duration
            duration = time.time() - self.start_time if self.start_time else 0
            
            # Update audio manager status
            self.audio_manager.update_status("Conversation ended")
            
            # Prepare conversation data
            conversation_data = {
                "timestamp": datetime.utcnow(),
                "duration_seconds": duration,
                "response_count": self.response_counter,
                "conversation_history": self.conversation_history,
                "final_transcript": self.current_transcript,
                "ended_by_user": True
            }
            
            if self.on_conversation_finished:
                self.on_conversation_finished(conversation_data)
            
            return conversation_data
            
        except Exception as e:
            print(f"Error ending conversation: {e}")
            if self.on_error:
                self.on_error(f"Error ending conversation: {e}")
            return {}
    
    async def pause_conversation(self):
        """Pause the current conversation"""
        if self.is_active:
            self.is_paused = True
            self.audio_manager.update_status("Conversation paused")
    
    async def resume_conversation(self):
        """Resume the paused conversation"""
        if self.is_active and self.is_paused:
            self.is_paused = False
            self.audio_manager.update_status("Conversation resumed - Ready to speak")
    
    async def send_audio_message(self, audio_data: str) -> bool:
        """Send audio message to the patient"""
        if not self.is_active or self.is_paused:
            return False
        
        # Check conversation limits
        if self._check_conversation_limits():
            await self._finish_conversation_automatically()
            return False
        
        try:
            # Send audio to realtime client
            success = await self.realtime_client.send_audio(audio_data)
            
            if success:
                self.response_counter += 1
                self.audio_manager.update_status("Processing your message...")
            
            return success
            
        except Exception as e:
            print(f"Error sending audio message: {e}")
            if self.on_error:
                self.on_error(f"Error sending message: {e}")
            return False
    
    async def send_text_message(self, text: str) -> bool:
        """Send text message to the patient (fallback)"""
        if not self.is_active or self.is_paused:
            return False
        
        # Check conversation limits
        if self._check_conversation_limits():
            await self._finish_conversation_automatically()
            return False
        
        try:
            success = await self.realtime_client.send_text(text)
            
            if success:
                self.response_counter += 1
                # Add to transcript
                self._add_to_transcript("user", text)
                self.audio_manager.update_status("Processing your message...")
            
            return success
            
        except Exception as e:
            print(f"Error sending text message: {e}")
            if self.on_error:
                self.on_error(f"Error sending message: {e}")
            return False
    
    def _check_conversation_limits(self) -> bool:
        """Check if conversation has reached limits"""
        # Check response limit
        if self.response_counter >= self.max_responses:
            return True
        
        # Check time limit
        if self.start_time and (time.time() - self.start_time) > self.max_duration:
            return True
        
        return False
    
    async def _finish_conversation_automatically(self):
        """Automatically finish conversation when limits are reached"""
        # Send final message
        final_message = "Thanks for the help, doc. I think we've covered everything for today."
        
        # Add to transcript
        self._add_to_transcript("assistant", final_message)
        
        # Update status
        self.audio_manager.update_status("Conversation completed")
        
        # End conversation
        await self.end_conversation()
    
    def _handle_audio_received(self, audio_data: str):
        """Handle audio received from the realtime client"""
        try:
            # Play the audio through audio manager
            self.audio_manager.play_audio(audio_data)
            
        except Exception as e:
            print(f"Error handling received audio: {e}")
    
    def _handle_transcript_received(self, speaker: str, text: str):
        """Handle transcript updates from the realtime client"""
        try:
            # Add to current transcript
            self._add_to_transcript(speaker, text)
            
            # Notify callback if set
            if self.on_transcript_update:
                self.on_transcript_update(speaker, text, self.current_transcript)
                
        except Exception as e:
            print(f"Error handling transcript: {e}")
    
    def _handle_error(self, error_message: str):
        """Handle errors from the realtime client"""
        print(f"Realtime client error: {error_message}")
        
        # Update audio manager status
        self.audio_manager.update_status(f"Error: {error_message}")
        
        # Notify callback if set
        if self.on_error:
            self.on_error(error_message)
    
    def _add_to_transcript(self, speaker: str, text: str):
        """Add text to conversation transcript"""
        timestamp = datetime.utcnow()
        
        # Add to conversation history
        self.conversation_history.append({
            "timestamp": timestamp,
            "speaker": speaker,
            "text": text,
            "response_number": self.response_counter
        })
        
        # Update current transcript
        if speaker in self.current_transcript:
            self.current_transcript[speaker] += text
        else:
            self.current_transcript[speaker] = text
    
    def get_conversation_status(self) -> Dict[str, Any]:
        """Get current conversation status"""
        if not self.is_active:
            return {
                "status": "inactive",
                "duration": 0,
                "response_count": 0,
                "is_paused": False
            }
        
        duration = time.time() - self.start_time if self.start_time else 0
        
        return {
            "status": "paused" if self.is_paused else "active",
            "duration": duration,
            "response_count": self.response_counter,
            "is_paused": self.is_paused,
            "time_remaining": max(0, self.max_duration - duration),
            "responses_remaining": max(0, self.max_responses - self.response_counter)
        }
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get the current conversation history"""
        return self.conversation_history.copy()
    
    def set_callbacks(self,
                     on_transcript_update: Optional[Callable] = None,
                     on_conversation_finished: Optional[Callable] = None,
                     on_error: Optional[Callable] = None):
        """Set callback functions"""
        if on_transcript_update:
            self.on_transcript_update = on_transcript_update
        if on_conversation_finished:
            self.on_conversation_finished = on_conversation_finished
        if on_error:
            self.on_error = on_error