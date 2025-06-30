import asyncio
import streamlit as st
import base64
import json
from typing import Dict, Any, Optional, Callable
from utils.config_manager import ConfigManager

class AudioManager:
    def __init__(self, config_manager: ConfigManager):
        self.config = config_manager
        self.audio_settings = config_manager.get_audio_settings()
        self.is_recording = False
        self.is_playing = False
        self.audio_queue = []
        self.transcript_callback: Optional[Callable] = None
        
    def initialize_audio_interface(self):
        """Initialize the audio interface in the Streamlit app"""
        # Audio interface HTML/JS will be embedded
        audio_interface_html = self._get_audio_interface_html()
        st.components.v1.html(audio_interface_html, height=300, scrolling=False)
        
    def _get_audio_interface_html(self) -> str:
        """Generate HTML/JS for audio interface"""
        return f"""
        <div id="audio-interface">
            <style>
                .audio-controls {{
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    gap: 15px;
                    padding: 20px;
                    background: #f0f2f6;
                    border-radius: 10px;
                    margin: 10px 0;
                }}
                
                .record-button {{
                    width: 80px;
                    height: 80px;
                    border-radius: 50%;
                    border: none;
                    font-size: 24px;
                    cursor: pointer;
                    transition: all 0.3s ease;
                }}
                
                .record-button.inactive {{
                    background: #ff4b4b;
                    color: white;
                }}
                
                .record-button.active {{
                    background: #ff8080;
                    color: white;
                    animation: pulse 2s infinite;
                }}
                
                @keyframes pulse {{
                    0% {{ box-shadow: 0 0 0 0 rgba(255, 75, 75, 0.7); }}
                    70% {{ box-shadow: 0 0 0 10px rgba(255, 75, 75, 0); }}
                    100% {{ box-shadow: 0 0 0 0 rgba(255, 75, 75, 0); }}
                }}
                
                .audio-status {{
                    font-size: 16px;
                    font-weight: bold;
                    color: #333;
                }}
                
                .volume-controls {{
                    display: flex;
                    align-items: center;
                    gap: 10px;
                }}
                
                .volume-slider {{
                    width: 150px;
                }}
                
                .audio-visualizer {{
                    width: 200px;
                    height: 50px;
                    background: #333;
                    border-radius: 5px;
                    position: relative;
                    overflow: hidden;
                }}
                
                .audio-bar {{
                    position: absolute;
                    bottom: 0;
                    width: 3px;
                    background: #00ff00;
                    transition: height 0.1s ease;
                }}
            </style>
            
            <div class="audio-controls">
                <button id="recordButton" class="record-button inactive" onclick="toggleRecording()">
                    🎤
                </button>
                
                <div class="audio-status" id="audioStatus">
                    Ready to start conversation
                </div>
                
                <div class="volume-controls">
                    <span>🔊</span>
                    <input type="range" id="volumeSlider" class="volume-slider" 
                           min="0" max="1" step="0.1" value="0.8" onchange="updateVolume()">
                    <span id="volumeValue">80%</span>
                </div>
                
                <div class="audio-visualizer" id="audioVisualizer" style="display: none;">
                    <!-- Audio bars will be dynamically generated -->
                </div>
            </div>
            
            <audio id="audioPlayer" preload="auto"></audio>
        </div>
        
        <script>
            let mediaRecorder;
            let audioChunks = [];
            let isRecording = false;
            let audioContext;
            let analyser;
            let microphone;
            let dataArray;
            
            // Initialize audio context for visualization
            async function initializeAudio() {{
                try {{
                    const stream = await navigator.mediaDevices.getUserMedia({{ audio: true }});
                    audioContext = new (window.AudioContext || window.webkitAudioContext)();
                    analyser = audioContext.createAnalyser();
                    microphone = audioContext.createMediaStreamSource(stream);
                    microphone.connect(analyser);
                    
                    analyser.fftSize = 256;
                    const bufferLength = analyser.frequencyBinCount;
                    dataArray = new Uint8Array(bufferLength);
                    
                    mediaRecorder = new MediaRecorder(stream);
                    setupMediaRecorder();
                }} catch (error) {{
                    console.error('Error accessing microphone:', error);
                    document.getElementById('audioStatus').textContent = 'Microphone access denied';
                }}
            }}
            
            function setupMediaRecorder() {{
                mediaRecorder.ondataavailable = event => {{
                    audioChunks.push(event.data);
                }};
                
                mediaRecorder.onstop = () => {{
                    const audioBlob = new Blob(audioChunks, {{ type: 'audio/wav' }});
                    audioChunks = [];
                    
                    // Convert to base64 and send to Streamlit
                    const reader = new FileReader();
                    reader.onloadend = () => {{
                        const base64Audio = reader.result.split(',')[1];
                        window.parent.postMessage({{
                            type: 'audio_data',
                            data: base64Audio
                        }}, '*');
                    }};
                    reader.readAsDataURL(audioBlob);
                }};
            }}
            
            async function toggleRecording() {{
                const button = document.getElementById('recordButton');
                const status = document.getElementById('audioStatus');
                
                if (!mediaRecorder) {{
                    await initializeAudio();
                }}
                
                if (!isRecording) {{
                    // Start recording
                    try {{
                        mediaRecorder.start();
                        isRecording = true;
                        button.className = 'record-button active';
                        status.textContent = 'Listening...';
                        
                        // Show visualizer
                        document.getElementById('audioVisualizer').style.display = 'block';
                        visualizeAudio();
                        
                        // Send recording started event
                        window.parent.postMessage({{
                            type: 'recording_started'
                        }}, '*');
                        
                    }} catch (error) {{
                        console.error('Error starting recording:', error);
                        status.textContent = 'Error starting recording';
                    }}
                }} else {{
                    // Stop recording
                    mediaRecorder.stop();
                    isRecording = false;
                    button.className = 'record-button inactive';
                    status.textContent = 'Processing...';
                    
                    // Hide visualizer
                    document.getElementById('audioVisualizer').style.display = 'none';
                    
                    // Send recording stopped event
                    window.parent.postMessage({{
                        type: 'recording_stopped'
                    }}, '*');
                }}
            }}
            
            function visualizeAudio() {{
                if (!isRecording || !analyser) return;
                
                analyser.getByteFrequencyData(dataArray);
                
                const visualizer = document.getElementById('audioVisualizer');
                visualizer.innerHTML = '';
                
                const barCount = 50;
                const barWidth = visualizer.offsetWidth / barCount;
                
                for (let i = 0; i < barCount; i++) {{
                    const bar = document.createElement('div');
                    bar.className = 'audio-bar';
                    bar.style.left = i * barWidth + 'px';
                    bar.style.width = (barWidth - 1) + 'px';
                    
                    const height = (dataArray[i] / 255) * visualizer.offsetHeight;
                    bar.style.height = height + 'px';
                    
                    visualizer.appendChild(bar);
                }}
                
                requestAnimationFrame(visualizeAudio);
            }}
            
            function updateVolume() {{
                const slider = document.getElementById('volumeSlider');
                const valueDisplay = document.getElementById('volumeValue');
                const audio = document.getElementById('audioPlayer');
                
                const volume = parseFloat(slider.value);
                valueDisplay.textContent = Math.round(volume * 100) + '%';
                audio.volume = volume;
                
                // Send volume change to Streamlit
                window.parent.postMessage({{
                    type: 'volume_changed',
                    volume: volume
                }}, '*');
            }}
            
            function playAudio(base64Audio) {{
                const audio = document.getElementById('audioPlayer');
                audio.src = 'data:audio/wav;base64,' + base64Audio;
                
                audio.onplay = () => {{
                    document.getElementById('audioStatus').textContent = 'Patient speaking...';
                }};
                
                audio.onended = () => {{
                    document.getElementById('audioStatus').textContent = 'Ready to respond';
                }};
                
                audio.play().catch(error => {{
                    console.error('Error playing audio:', error);
                    document.getElementById('audioStatus').textContent = 'Audio playback error';
                }});
            }}
            
            // Listen for messages from Streamlit
            window.addEventListener('message', (event) => {{
                if (event.data.type === 'play_audio') {{
                    playAudio(event.data.audio);
                }} else if (event.data.type === 'update_status') {{
                    document.getElementById('audioStatus').textContent = event.data.status;
                }}
            }});
            
            // Initialize on load
            document.addEventListener('DOMContentLoaded', function() {{
                updateVolume();
            }});
        </script>
        """
    
    def set_transcript_callback(self, callback: Callable):
        """Set callback function for transcript updates"""
        self.transcript_callback = callback
        
    def play_audio(self, audio_data: str):
        """Play audio data (base64 encoded)"""
        st.components.v1.html(f"""
            <script>
                const iframe = parent.document.querySelector('iframe[title*="audio-interface"]');
                if (iframe) {{
                    iframe.contentWindow.postMessage({{
                        type: 'play_audio',
                        audio: '{audio_data}'
                    }}, '*');
                }}
            </script>
        """, height=0)
        
    def update_status(self, status: str):
        """Update the audio interface status"""
        st.components.v1.html(f"""
            <script>
                const iframe = parent.document.querySelector('iframe[title*="audio-interface"]');
                if (iframe) {{
                    iframe.contentWindow.postMessage({{
                        type: 'update_status',
                        status: '{status}'
                    }}, '*');
                }}
            </script>
        """, height=0)
        
    def get_audio_settings_for_api(self) -> Dict[str, Any]:
        """Get audio settings formatted for OpenAI Realtime API"""
        return {
            "voice": self.audio_settings.get("voice_type", "alloy"),
            "input_audio_format": self.audio_settings.get("quality_settings", {}).get("format", "pcm16"),
            "output_audio_format": self.audio_settings.get("quality_settings", {}).get("format", "pcm16"),
            "input_audio_transcription": {
                "model": "whisper-1"
            }
        }