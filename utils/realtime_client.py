import asyncio
import websockets
import json
import base64
import os
from typing import Dict, Any, Optional, Callable
from utils.config_manager import ConfigManager

class RealtimeClient:
    def __init__(self, api_key: str, config_manager: ConfigManager):
        self.api_key = api_key
        self.config = config_manager
        self.audio_settings = config_manager.get_audio_settings()
        self.conversation_settings = config_manager.get_conversation_settings()
        
        self.websocket: Optional[websockets.WebSocketServerProtocol] = None
        self.is_connected = False
        self.session_config = None
        
        # Callbacks
        self.on_audio_received: Optional[Callable] = None
        self.on_transcript_received: Optional[Callable] = None
        self.on_error: Optional[Callable] = None
        
    async def connect(self) -> bool:
        """Establish WebSocket connection to OpenAI Realtime API"""
        try:
            # OpenAI Realtime API endpoint
            uri = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-10-01"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "OpenAI-Beta": "realtime=v1"
            }
            
            self.websocket = await websockets.connect(uri, extra_headers=headers)
            self.is_connected = True
            
            # Send session configuration
            await self._configure_session()
            
            # Start listening for messages
            asyncio.create_task(self._listen_for_messages())
            
            return True
            
        except Exception as e:
            print(f"Error connecting to OpenAI Realtime API: {e}")
            if self.on_error:
                self.on_error(f"Connection error: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from the WebSocket"""
        if self.websocket and self.is_connected:
            await self.websocket.close()
            self.is_connected = False
    
    async def _configure_session(self):
        """Configure the realtime session with audio settings"""
        session_update = {
            "type": "session.update",
            "session": {
                "modalities": ["text", "audio"],
                "instructions": "You are a helpful assistant. Respond naturally in audio format.",
                "voice": self.audio_settings.get("voice_type", "alloy"),
                "input_audio_format": self.audio_settings.get("quality_settings", {}).get("format", "pcm16"),
                "output_audio_format": self.audio_settings.get("quality_settings", {}).get("format", "pcm16"),
                "input_audio_transcription": {
                    "model": "whisper-1"
                },
                "turn_detection": {
                    "type": "server_vad",
                    "threshold": self.audio_settings.get("conversation_detection", {}).get("volume_threshold", 0.5),
                    "prefix_padding_ms": 300,
                    "silence_duration_ms": int(self.audio_settings.get("conversation_detection", {}).get("silence_threshold", 2.0) * 1000)
                },
                "tools": [],
                "tool_choice": "none",
                "temperature": 0.8,
                "max_response_output_tokens": 4096
            }
        }
        
        await self.websocket.send(json.dumps(session_update))
    
    async def _listen_for_messages(self):
        """Listen for incoming messages from the WebSocket"""
        try:
            async for message in self.websocket:
                try:
                    data = json.loads(message)
                    await self._handle_message(data)
                except json.JSONDecodeError as e:
                    print(f"Error parsing message: {e}")
                    
        except websockets.exceptions.ConnectionClosed:
            print("WebSocket connection closed")
            self.is_connected = False
        except Exception as e:
            print(f"Error listening for messages: {e}")
            if self.on_error:
                self.on_error(f"Listening error: {e}")
    
    async def _handle_message(self, data: Dict[str, Any]):
        """Handle incoming messages from the API"""
        message_type = data.get("type")
        
        if message_type == "session.created":
            print("Session created successfully")
            self.session_config = data.get("session")
            
        elif message_type == "response.audio.delta":
            # Audio chunk received
            audio_data = data.get("delta", "")
            if self.on_audio_received and audio_data:
                self.on_audio_received(audio_data)
                
        elif message_type == "conversation.item.input_audio_transcription.completed":
            # User's audio transcription completed
            transcript = data.get("transcript", "")
            if self.on_transcript_received:
                self.on_transcript_received("user", transcript)
                
        elif message_type == "response.text.delta":
            # Text response chunk
            text_delta = data.get("delta", "")
            if self.on_transcript_received:
                self.on_transcript_received("assistant", text_delta)
                
        elif message_type == "response.audio_transcript.delta":
            # Assistant's audio transcription
            transcript_delta = data.get("delta", "")
            if self.on_transcript_received:
                self.on_transcript_received("assistant", transcript_delta)
                
        elif message_type == "error":
            error_message = data.get("error", {}).get("message", "Unknown error")
            print(f"API Error: {error_message}")
            if self.on_error:
                self.on_error(error_message)
                
        else:
            # Handle other message types as needed
            print(f"Received message type: {message_type}")
    
    async def send_audio(self, audio_data: str):
        """Send audio data to the API (base64 encoded)"""
        if not self.is_connected or not self.websocket:
            print("Not connected to WebSocket")
            return False
            
        try:
            # Create conversation item with audio
            audio_message = {
                "type": "conversation.item.create",
                "item": {
                    "type": "message",
                    "role": "user",
                    "content": [
                        {
                            "type": "input_audio",
                            "audio": audio_data
                        }
                    ]
                }
            }
            
            await self.websocket.send(json.dumps(audio_message))
            
            # Trigger response generation
            response_create = {
                "type": "response.create",
                "response": {
                    "modalities": ["text", "audio"],
                    "instructions": "Respond naturally as the physiotherapy patient character."
                }
            }
            
            await self.websocket.send(json.dumps(response_create))
            return True
            
        except Exception as e:
            print(f"Error sending audio: {e}")
            if self.on_error:
                self.on_error(f"Send audio error: {e}")
            return False
    
    async def send_text(self, text: str):
        """Send text message to the API"""
        if not self.is_connected or not self.websocket:
            print("Not connected to WebSocket")
            return False
            
        try:
            text_message = {
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
            
            await self.websocket.send(json.dumps(text_message))
            
            # Trigger response
            response_create = {
                "type": "response.create",
                "response": {
                    "modalities": ["text", "audio"],
                    "instructions": "Respond naturally as the physiotherapy patient character."
                }
            }
            
            await self.websocket.send(json.dumps(response_create))
            return True
            
        except Exception as e:
            print(f"Error sending text: {e}")
            if self.on_error:
                self.on_error(f"Send text error: {e}")
            return False
    
    async def update_session_instructions(self, instructions: str):
        """Update the session instructions (for changing patient persona)"""
        if not self.is_connected or not self.websocket:
            return False
            
        try:
            session_update = {
                "type": "session.update",
                "session": {
                    "instructions": instructions
                }
            }
            
            await self.websocket.send(json.dumps(session_update))
            return True
            
        except Exception as e:
            print(f"Error updating instructions: {e}")
            return False
    
    def set_callbacks(self, 
                     on_audio_received: Optional[Callable] = None,
                     on_transcript_received: Optional[Callable] = None,
                     on_error: Optional[Callable] = None):
        """Set callback functions for handling responses"""
        if on_audio_received:
            self.on_audio_received = on_audio_received
        if on_transcript_received:
            self.on_transcript_received = on_transcript_received
        if on_error:
            self.on_error = on_error