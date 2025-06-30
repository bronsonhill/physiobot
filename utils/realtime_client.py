import asyncio
import websockets
import json
import logging
import os
from typing import Optional, Callable, Dict, Any, List
import time
import base64
from datetime import datetime
import ssl

logger = logging.getLogger(__name__)

class RealtimeClient:
    """
    WebSocket client for OpenAI Realtime Audio API.
    Handles connection, audio streaming, and conversation management.
    """
    
    def __init__(self, api_key: str, config: Dict[str, Any]):
        """
        Initialize realtime client.
        
        Args:
            api_key: OpenAI API key
            config: Configuration dictionary
        """
        self.api_key = api_key
        self.config = config
        self.realtime_config = config.get('openai_realtime', {})
        
        # Connection state
        self.websocket: Optional[websockets.WebSocketServerProtocol] = None
        self.is_connected = False
        self.connection_id: Optional[str] = None
        
        # API endpoint
        self.url = "wss://api.openai.com/v1/realtime"
        
        # Session configuration
        self.model = self.realtime_config.get('model', 'gpt-4o-realtime-preview-2024-10-01')
        self.voice = self.realtime_config.get('voice', 'alloy')
        self.input_audio_format = self.realtime_config.get('input_audio_format', 'pcm16')
        self.output_audio_format = self.realtime_config.get('output_audio_format', 'pcm16')
        
        # Turn detection settings
        turn_detection = self.realtime_config.get('turn_detection', {})
        self.turn_detection_type = turn_detection.get('type', 'server_vad')
        self.vad_threshold = turn_detection.get('threshold', 0.5)
        self.vad_prefix_padding_ms = turn_detection.get('prefix_padding_ms', 300)
        self.vad_silence_duration_ms = turn_detection.get('silence_duration_ms', 200)
        
        # Transcription settings
        transcription_config = self.realtime_config.get('input_audio_transcription', {})
        self.transcription_model = transcription_config.get('model', 'whisper-1')
        
        # Event callbacks
        self.on_audio_response: Optional[Callable] = None
        self.on_transcript: Optional[Callable] = None
        self.on_error: Optional[Callable] = None
        self.on_conversation_item: Optional[Callable] = None
        self.on_response_done: Optional[Callable] = None
        
        # Session state
        self.session_id: Optional[str] = None
        self.conversation_items: List[Dict] = []
        self.current_response_id: Optional[str] = None
        
        logger.info(f"RealtimeClient initialized with model={self.model}, voice={self.voice}")
    
    async def connect(self) -> bool:
        """
        Establish WebSocket connection to OpenAI Realtime API.
        
        Returns:
            True if connection successful, False otherwise
        """
        if self.is_connected:
            logger.warning("Already connected to Realtime API")
            return True
        
        try:
            # Set up headers
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "OpenAI-Beta": "realtime=v1"
            }
            
            # Create SSL context
            ssl_context = ssl.create_default_context()
            
            # Connect to WebSocket
            logger.info(f"Connecting to {self.url}")
            self.websocket = await websockets.connect(
                f"{self.url}?model={self.model}",
                extra_headers=headers,
                ssl=ssl_context,
                ping_interval=20,
                ping_timeout=10
            )
            
            self.is_connected = True
            self.connection_id = str(int(time.time() * 1000))
            
            # Start listening for messages
            asyncio.create_task(self._listen_for_messages())
            
            # Configure session
            await self._configure_session()
            
            logger.info(f"Connected to Realtime API with connection_id={self.connection_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Realtime API: {e}")
            self.is_connected = False
            return False
    
    async def disconnect(self) -> None:
        """Disconnect from Realtime API."""
        if not self.is_connected:
            return
        
        try:
            self.is_connected = False
            if self.websocket:
                await self.websocket.close()
                self.websocket = None
            
            logger.info("Disconnected from Realtime API")
        except Exception as e:
            logger.error(f"Error during disconnect: {e}")
    
    async def _configure_session(self) -> None:
        """Configure the session with initial settings."""
        session_config = {
            "type": "session.update",
            "session": {
                "modalities": ["text", "audio"],
                "instructions": "You are a helpful assistant.",
                "voice": self.voice,
                "input_audio_format": self.input_audio_format,
                "output_audio_format": self.output_audio_format,
                "input_audio_transcription": {
                    "model": self.transcription_model
                },
                "turn_detection": {
                    "type": self.turn_detection_type,
                    "threshold": self.vad_threshold,
                    "prefix_padding_ms": self.vad_prefix_padding_ms,
                    "silence_duration_ms": self.vad_silence_duration_ms
                }
            }
        }
        
        await self._send_message(session_config)
        logger.info("Session configured")
    
    async def send_audio(self, audio_data: bytes) -> bool:
        """
        Send audio data to the API.
        
        Args:
            audio_data: Raw audio data bytes
            
        Returns:
            True if sent successfully, False otherwise
        """
        if not self.is_connected:
            logger.error("Not connected to Realtime API")
            return False
        
        try:
            # Encode audio data
            encoded_audio = base64.b64encode(audio_data).decode('utf-8')
            
            message = {
                "type": "input_audio_buffer.append",
                "audio": encoded_audio
            }
            
            await self._send_message(message)
            return True
            
        except Exception as e:
            logger.error(f"Failed to send audio: {e}")
            return False
    
    async def commit_audio(self) -> bool:
        """
        Commit the audio buffer to trigger response generation.
        
        Returns:
            True if committed successfully, False otherwise
        """
        if not self.is_connected:
            logger.error("Not connected to Realtime API")
            return False
        
        try:
            message = {
                "type": "input_audio_buffer.commit"
            }
            
            await self._send_message(message)
            logger.debug("Audio buffer committed")
            return True
            
        except Exception as e:
            logger.error(f"Failed to commit audio: {e}")
            return False
    
    async def send_text(self, text: str) -> bool:
        """
        Send text message to the conversation.
        
        Args:
            text: Text message to send
            
        Returns:
            True if sent successfully, False otherwise
        """
        if not self.is_connected:
            logger.error("Not connected to Realtime API")
            return False
        
        try:
            message = {
                "type": "conversation.item.create",
                "item": {
                    "type": "message",
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": text
                        }
                    ]
                }
            }
            
            await self._send_message(message)
            
            # Trigger response
            response_message = {
                "type": "response.create"
            }
            await self._send_message(response_message)
            
            logger.debug(f"Sent text message: {text[:50]}...")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send text: {e}")
            return False
    
    async def update_session_instructions(self, instructions: str) -> bool:
        """
        Update session instructions (system prompt).
        
        Args:
            instructions: New instructions for the assistant
            
        Returns:
            True if updated successfully, False otherwise
        """
        if not self.is_connected:
            logger.error("Not connected to Realtime API")
            return False
        
        try:
            message = {
                "type": "session.update",
                "session": {
                    "instructions": instructions
                }
            }
            
            await self._send_message(message)
            logger.info("Session instructions updated")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update instructions: {e}")
            return False
    
    async def _send_message(self, message: Dict[str, Any]) -> None:
        """Send message through WebSocket."""
        if not self.websocket:
            raise Exception("WebSocket not connected")
        
        await self.websocket.send(json.dumps(message))
        logger.debug(f"Sent message: {message['type']}")
    
    async def _listen_for_messages(self) -> None:
        """Listen for incoming WebSocket messages."""
        if not self.websocket:
            logger.error("WebSocket not available for listening")
            return
            
        try:
            async for message in self.websocket:
                await self._handle_message(json.loads(message))
        except websockets.exceptions.ConnectionClosed:
            logger.info("WebSocket connection closed")
            self.is_connected = False
        except Exception as e:
            logger.error(f"Error listening for messages: {e}")
            self.is_connected = False
    
    async def _handle_message(self, message: Dict[str, Any]) -> None:
        """Handle incoming message from the API."""
        message_type = message.get('type')
        
        try:
            if message_type == 'session.created':
                self.session_id = message.get('session', {}).get('id')
                logger.info(f"Session created: {self.session_id}")
            
            elif message_type == 'session.updated':
                logger.debug("Session updated")
            
            elif message_type == 'response.audio.delta':
                # Audio response chunk
                audio_data = message.get('delta')
                if audio_data and self.on_audio_response:
                    decoded_audio = base64.b64decode(audio_data)
                    await self._safe_callback(self.on_audio_response, decoded_audio)
            
            elif message_type == 'response.audio_transcript.delta':
                # Transcript chunk
                transcript = message.get('delta')
                if transcript and self.on_transcript:
                    await self._safe_callback(self.on_transcript, transcript, False)
            
            elif message_type == 'response.audio_transcript.done':
                # Complete transcript
                transcript = message.get('transcript')
                if transcript and self.on_transcript:
                    await self._safe_callback(self.on_transcript, transcript, True)
            
            elif message_type == 'conversation.item.created':
                # New conversation item
                item = message.get('item')
                if item:
                    self.conversation_items.append(item)
                    if self.on_conversation_item:
                        await self._safe_callback(self.on_conversation_item, item)
            
            elif message_type == 'response.done':
                # Response completed
                response = message.get('response')
                if response and self.on_response_done:
                    await self._safe_callback(self.on_response_done, response)
            
            elif message_type == 'error':
                # Error message
                error = message.get('error', {})
                error_message = error.get('message', 'Unknown error')
                logger.error(f"API Error: {error_message}")
                if self.on_error:
                    await self._safe_callback(self.on_error, error)
            
            else:
                logger.debug(f"Unhandled message type: {message_type}")
        
        except Exception as e:
            logger.error(f"Error handling message {message_type}: {e}")
    
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
                     on_audio_response: Optional[Callable] = None,
                     on_transcript: Optional[Callable] = None,
                     on_error: Optional[Callable] = None,
                     on_conversation_item: Optional[Callable] = None,
                     on_response_done: Optional[Callable] = None) -> None:
        """
        Set callback functions for various events.
        
        Args:
            on_audio_response: Callback for audio response chunks
            on_transcript: Callback for transcript updates
            on_error: Callback for error events
            on_conversation_item: Callback for new conversation items
            on_response_done: Callback for response completion
        """
        self.on_audio_response = on_audio_response
        self.on_transcript = on_transcript
        self.on_error = on_error
        self.on_conversation_item = on_conversation_item
        self.on_response_done = on_response_done
    
    def get_conversation_items(self) -> List[Dict]:
        """Get current conversation items."""
        return self.conversation_items.copy()
    
    def get_connection_status(self) -> Dict[str, Any]:
        """Get current connection status."""
        return {
            'is_connected': self.is_connected,
            'connection_id': self.connection_id,
            'session_id': self.session_id,
            'url': self.url,
            'model': self.model,
            'voice': self.voice
        }