import streamlit as st
import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional

from Home import setup
from utils.conversation_handler import ConversationHandler, ConversationState
from utils.config_manager import ConfigManager
from utils.mongodb_realtime import log_audio_transcript

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Patient Conversation - PhysioBot",
    page_icon="🗣️",
    layout="wide"
)

# Check user authentication
if not bool(st.session_state.get("user_identifier", "").strip()):
    st.error("Please enter your identifier on the Home page before starting the conversation.")
    st.stop()

# Initialize session state for audio conversation
if "audio_conversation_handler" not in st.session_state:
    st.session_state["audio_conversation_handler"] = None

if "audio_conversation_active" not in st.session_state:
    st.session_state["audio_conversation_active"] = False

if "audio_transcript_segments" not in st.session_state:
    st.session_state["audio_transcript_segments"] = []

if "audio_conversation_state" not in st.session_state:
    st.session_state["audio_conversation_state"] = "idle"

if "audio_volume_level" not in st.session_state:
    st.session_state["audio_volume_level"] = 0.0

if "audio_quality_metrics" not in st.session_state:
    st.session_state["audio_quality_metrics"] = {}

if "conversation_start_time" not in st.session_state:
    st.session_state["conversation_start_time"] = None

if "conversation_duration" not in st.session_state:
    st.session_state["conversation_duration"] = 0

# Setup OpenAI client and configuration
client = setup()
config_manager = ConfigManager()
config = config_manager.config

# Page title and header
st.title("🗣️ Audio Conversation with your Patient")
st.markdown("---")

# Create main layout
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("🎤 Audio Controls")
    
    # Audio status indicator
    status_container = st.container()
    with status_container:
        if st.session_state["audio_conversation_state"] == "idle":
            st.info("🔵 Ready to start conversation")
        elif st.session_state["audio_conversation_state"] == "connecting":
            st.warning("🟡 Connecting to audio service...")
        elif st.session_state["audio_conversation_state"] == "waiting_for_user":
            st.success("🟢 Ready for your input")
        elif st.session_state["audio_conversation_state"] == "user_speaking":
            st.success("🔴 Recording your voice...")
        elif st.session_state["audio_conversation_state"] == "processing":
            st.warning("🟡 Processing...")
        elif st.session_state["audio_conversation_state"] == "ai_responding":
            st.info("🎵 Patient is responding...")
        elif st.session_state["audio_conversation_state"] == "completed":
            st.success("✅ Conversation completed")
        elif st.session_state["audio_conversation_state"] == "error":
            st.error("❌ Connection error")
    
    # Volume level indicator
    if st.session_state["audio_volume_level"] > 0:
        volume_percentage = min(100, st.session_state["audio_volume_level"] * 100)
        st.progress(volume_percentage / 100, text=f"Volume: {volume_percentage:.1f}%")
    
    # Conversation timing
    if st.session_state["conversation_start_time"] and st.session_state["audio_conversation_active"]:
        duration = (datetime.now(timezone.utc) - st.session_state["conversation_start_time"]).total_seconds()
        minutes = int(duration // 60)
        seconds = int(duration % 60)
        st.metric("Duration", f"{minutes:02d}:{seconds:02d}")
    
    # Audio controls
    st.subheader("Controls")
    
    # Start conversation button
    if not st.session_state["audio_conversation_active"]:
        if st.button("🎙️ Start Audio Conversation", type="primary", use_container_width=True):
            try:
                # Initialize conversation handler
                api_key = st.secrets["OPENAI_API_KEY"]
                conversation_handler = ConversationHandler(config, api_key)
                
                # Set up callbacks
                def on_state_change(old_state, new_state):
                    st.session_state["audio_conversation_state"] = new_state
                    st.rerun()
                
                def on_transcript_update(text, speaker, is_complete):
                    if is_complete and text.strip():
                        segment = {
                            'timestamp': datetime.now(timezone.utc),
                            'speaker': speaker,
                            'text': text.strip(),
                            'is_complete': is_complete
                        }
                        st.session_state["audio_transcript_segments"].append(segment)
                        st.rerun()
                
                def on_audio_level(level):
                    st.session_state["audio_volume_level"] = level
                
                def on_error(error_message):
                    st.error(f"Audio error: {error_message}")
                    st.session_state["audio_conversation_state"] = "error"
                    st.rerun()
                
                def on_conversation_complete(summary):
                     st.session_state["audio_conversation_active"] = False
                     st.session_state["p_conversation_finished"] = True
                     
                     # Prepare transcript data for database
                     transcript_data = {
                         "transcript_segments": st.session_state["audio_transcript_segments"],
                         "session_summary": summary,
                         "audio_duration": summary.get("duration_seconds", 0),
                         "conversation_metrics": {
                             "total_exchanges": len(st.session_state["audio_transcript_segments"]),
                             "user_segments": len([s for s in st.session_state["audio_transcript_segments"] if s['speaker'] == 'user']),
                             "assistant_segments": len([s for s in st.session_state["audio_transcript_segments"] if s['speaker'] == 'assistant'])
                         }
                     }
                     
                     # Log transcript to database
                     session_id = log_audio_transcript(
                         st.session_state["mongodb_uri"],
                         "patient",
                         transcript_data
                     )
                     st.session_state["session_id"] = session_id
                     st.success("Conversation completed and saved!")
                     st.rerun()
                
                conversation_handler.set_callbacks(
                    on_state_change=on_state_change,
                    on_transcript_update=on_transcript_update,
                    on_audio_level=on_audio_level,
                    on_error=on_error,
                    on_conversation_complete=on_conversation_complete
                )
                
                st.session_state["audio_conversation_handler"] = conversation_handler
                st.session_state["audio_conversation_active"] = True
                st.session_state["conversation_start_time"] = datetime.now(timezone.utc)
                st.session_state["audio_transcript_segments"] = []
                
                # Load audio-specific patient prompt
                try:
                    with open("./prompts/audio_patient_prompt.txt", "r") as file:
                        audio_patient_instructions = file.read()
                except FileNotFoundError:
                    # Fallback to regular prompt with audio adaptations
                    patient_instructions = st.session_state["patient_prompt"]
                    audio_patient_instructions = f"""
{patient_instructions}

IMPORTANT AUDIO CONVERSATION GUIDELINES:
- You are having a spoken conversation, not a text chat
- Speak naturally and conversationally
- Keep responses concise and clear
- Use verbal acknowledgments like "mm-hmm", "I see", "okay"
- If you don't understand something, ask for clarification naturally
- Express emotions through your tone of voice appropriately
- Remember this is a learning experience for a physiotherapy student
- Be patient and encouraging while staying in character
"""
                
                # Start the conversation asynchronously
                asyncio.run(conversation_handler.start_conversation(audio_patient_instructions))
                st.rerun()
                
            except Exception as e:
                st.error(f"Failed to start conversation: {str(e)}")
                logger.error(f"Conversation start error: {e}")
    
    else:
        # Recording controls
        col_record, col_stop = st.columns(2)
        
        with col_record:
            if st.session_state["audio_conversation_state"] == "waiting_for_user":
                if st.button("🔴 Start Recording", type="primary", use_container_width=True):
                    if st.session_state["audio_conversation_handler"]:
                        try:
                            asyncio.run(st.session_state["audio_conversation_handler"].start_recording())
                        except Exception as e:
                            st.error(f"Recording failed: {str(e)}")
        
        with col_stop:
            if st.session_state["audio_conversation_state"] == "user_speaking":
                if st.button("⏹️ Stop Recording", type="secondary", use_container_width=True):
                    if st.session_state["audio_conversation_handler"]:
                        try:
                            asyncio.run(st.session_state["audio_conversation_handler"].stop_recording())
                        except Exception as e:
                            st.error(f"Stop recording failed: {str(e)}")
        
        # Send text message option
        st.subheader("💬 Text Input")
        st.caption("Alternative to voice input")
        
        text_input = st.text_input(
            "Type your message:",
            key="text_message_input",
            disabled=st.session_state["audio_conversation_state"] != "waiting_for_user"
        )
        
        if st.button("Send Text", disabled=st.session_state["audio_conversation_state"] != "waiting_for_user"):
            if text_input.strip() and st.session_state["audio_conversation_handler"]:
                try:
                    asyncio.run(st.session_state["audio_conversation_handler"].send_text_message(text_input.strip()))
                    st.session_state["text_message_input"] = ""
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to send text: {str(e)}")
        
        # Finish conversation button
        st.subheader("🏁 End Conversation")
        if st.button("Finish Conversation", type="secondary", use_container_width=True):
            if st.session_state["audio_conversation_handler"]:
                try:
                    summary = asyncio.run(st.session_state["audio_conversation_handler"].end_conversation())
                    st.session_state["part_1_done"] = True
                    st.success("Conversation finished successfully!")
                except Exception as e:
                    st.error(f"Failed to end conversation: {str(e)}")

with col2:
    st.subheader("📝 Live Conversation Transcript")
    
    # Transcript display container
    transcript_container = st.container()
    
    with transcript_container:
        if not st.session_state["audio_transcript_segments"]:
            st.info("Conversation transcript will appear here as you talk...")
        else:
            # Display transcript segments
            for i, segment in enumerate(st.session_state["audio_transcript_segments"]):
                timestamp = segment['timestamp'].strftime("%H:%M:%S")
                speaker = segment['speaker']
                text = segment['text']
                
                if speaker == "user":
                    st.markdown(f"**🧑‍⚕️ You** _{timestamp}_\n\n{text}")
                elif speaker == "assistant":
                    st.markdown(f"**🤒 Patient** _{timestamp}_\n\n{text}")
                
                if i < len(st.session_state["audio_transcript_segments"]) - 1:
                    st.markdown("---")
    
    # Audio visualization area
    if st.session_state["audio_conversation_active"]:
        st.subheader("🎵 Audio Visualization")
        
        # Create placeholder for JavaScript audio visualization
        audio_viz_placeholder = st.empty()
        
        # Add JavaScript for audio interface
        audio_interface_js = """
        <div id="audio-visualization">
            <div style="margin-bottom: 10px;">
                <label>Volume Level:</label>
                <div style="background-color: #f0f0f0; height: 20px; border-radius: 10px; overflow: hidden;">
                    <div id="volume-indicator" style="height: 100%; background-color: #44ff44; width: 0%; transition: width 0.1s;"></div>
                </div>
            </div>
            
            <div style="margin-bottom: 10px;">
                <label>Frequency Visualization:</label>
                <div style="display: flex; height: 50px; align-items: end; gap: 2px;">
                    <div class="frequency-bar" style="background-color: #4CAF50; width: 8px; height: 0%; transition: height 0.1s;"></div>
                    <div class="frequency-bar" style="background-color: #4CAF50; width: 8px; height: 0%; transition: height 0.1s;"></div>
                    <div class="frequency-bar" style="background-color: #4CAF50; width: 8px; height: 0%; transition: height 0.1s;"></div>
                    <div class="frequency-bar" style="background-color: #4CAF50; width: 8px; height: 0%; transition: height 0.1s;"></div>
                    <div class="frequency-bar" style="background-color: #4CAF50; width: 8px; height: 0%; transition: height 0.1s;"></div>
                    <div class="frequency-bar" style="background-color: #4CAF50; width: 8px; height: 0%; transition: height 0.1s;"></div>
                    <div class="frequency-bar" style="background-color: #4CAF50; width: 8px; height: 0%; transition: height 0.1s;"></div>
                    <div class="frequency-bar" style="background-color: #4CAF50; width: 8px; height: 0%; transition: height 0.1s;"></div>
                </div>
            </div>
        </div>
        
        <script>
            // Initialize audio interface if not already done
            if (typeof window.audioInterface === 'undefined') {
                const script = document.createElement('script');
                script.src = '/static/js/audio_interface.js';
                document.head.appendChild(script);
                
                script.onload = function() {
                    window.audioInterface = new AudioInterface({
                        visualizationEnabled: true,
                        sampleRate: 24000
                    });
                };
            }
        </script>
        """
        
        audio_viz_placeholder.markdown(audio_interface_js, unsafe_allow_html=True)

# Sidebar with conversation info and settings
with st.sidebar:
    st.subheader("📊 Conversation Statistics")
    
    if st.session_state["audio_transcript_segments"]:
        total_segments = len(st.session_state["audio_transcript_segments"])
        user_segments = len([s for s in st.session_state["audio_transcript_segments"] if s['speaker'] == 'user'])
        patient_segments = len([s for s in st.session_state["audio_transcript_segments"] if s['speaker'] == 'assistant'])
        
        st.metric("Total Exchanges", total_segments)
        st.metric("Your Messages", user_segments)
        st.metric("Patient Responses", patient_segments)
    
    st.subheader("⚙️ Audio Settings")
    
    # Volume control (if conversation is active)
    if st.session_state["audio_conversation_active"]:
        volume_level = st.slider("Output Volume", 0.0, 2.0, 1.0, 0.1)
        # This would be passed to the audio interface for volume control
    
    # Audio quality metrics
    if st.session_state["audio_quality_metrics"]:
        st.subheader("📡 Connection Quality")
        metrics = st.session_state["audio_quality_metrics"]
        
        if "connection_quality" in metrics:
            quality_score = metrics["connection_quality"]
            st.metric("Connection Quality", f"{quality_score:.1%}")
        
        if "latency_ms" in metrics:
            latency = metrics["latency_ms"]
            st.metric("Latency", f"{latency:.0f} ms")
    
    st.subheader("ℹ️ Instructions")
    st.markdown("""
    **How to use:**
    1. Click "Start Audio Conversation" to begin
    2. Use "Start Recording" to speak to the patient
    3. Click "Stop Recording" when you finish speaking
    4. Wait for the patient's audio response
    5. Continue the conversation naturally
    6. Use "Finish Conversation" when done
    
    **Tips:**
    - Speak clearly and at normal pace
    - Wait for responses before speaking again
    - Use the text input as backup if needed
    - Monitor your volume level indicator
    """)

# Add custom CSS for better styling
st.markdown("""
<style>
.stButton > button {
    width: 100%;
}

.audio-control-button {
    padding: 10px;
    margin: 5px 0;
    border-radius: 5px;
    border: none;
    font-weight: bold;
    cursor: pointer;
}

.recording-button {
    background-color: #ff4444;
    color: white;
}

.stop-button {
    background-color: #666666;
    color: white;
}

.transcript-segment {
    padding: 10px;
    margin: 5px 0;
    border-radius: 8px;
    border-left: 4px solid #4CAF50;
}

.user-message {
    background-color: #e3f2fd;
    border-left-color: #2196F3;
}

.assistant-message {
    background-color: #f3e5f5;
    border-left-color: #9C27B0;
}
</style>
""", unsafe_allow_html=True)

# Auto-refresh for live updates during conversation
if st.session_state["audio_conversation_active"]:
    st.rerun()