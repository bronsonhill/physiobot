import streamlit as st
import asyncio
import os
import time
from datetime import datetime
from typing import Dict, Any, List

# Import utilities
from Home import setup
from utils.config_manager import ConfigManager
from utils.audio_manager import AudioManager
from utils.conversation_handler import ConversationHandler
from utils.mongodb_realtime import MongoDBRealtimeClient

# Check if user is authenticated
if not bool(st.session_state.get("user_identifier", "").strip()):
    st.error("Please enter your identifier on the Home page before starting the conversation.")
    st.stop()

# Initialize configuration
config_manager = ConfigManager()
conversation_settings = config_manager.get_conversation_settings()
ui_settings = config_manager.get_ui_settings()

# Initialize OpenAI client for API key
client = setup()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    st.error("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
    st.stop()

# Initialize session state for audio conversation
if "audio_conversation_handler" not in st.session_state:
    st.session_state.audio_conversation_handler = None

if "audio_conversation_active" not in st.session_state:
    st.session_state.audio_conversation_active = False

if "audio_transcript" not in st.session_state:
    st.session_state.audio_transcript = []

if "conversation_status" not in st.session_state:
    st.session_state.conversation_status = {"status": "inactive"}

if "audio_session_id" not in st.session_state:
    st.session_state.audio_session_id = None

# Page title
st.title("🎤 Audio Conversation with your Patient")

# Load patient prompt
def load_patient_prompt():
    """Load the audio patient prompt"""
    try:
        with open("prompts/audio_patient_prompt.txt", "r") as f:
            return f.read()
    except FileNotFoundError:
        # Fallback to regular prompt if audio prompt not found
        try:
            with open("prompts/pprompt.txt", "r") as f:
                return f.read()
        except FileNotFoundError:
            return "You are a helpful physiotherapy patient named Tau. Respond naturally to the student's questions about your hip pain."

# Patient prompt
patient_prompt = load_patient_prompt()

# Conversation status display
def display_conversation_status():
    """Display current conversation status"""
    status = st.session_state.conversation_status
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if status["status"] == "active":
            st.success("🟢 Active")
        elif status["status"] == "paused":
            st.warning("🟡 Paused")
        else:
            st.info("⚪ Inactive")
    
    with col2:
        duration = status.get("duration", 0)
        minutes = int(duration // 60)
        seconds = int(duration % 60)
        st.metric("Duration", f"{minutes}:{seconds:02d}")
    
    with col3:
        st.metric("Responses", status.get("response_count", 0))
    
    with col4:
        remaining = status.get("responses_remaining", 0)
        st.metric("Remaining", remaining)

# Display status
display_conversation_status()

# Audio conversation controls
def start_conversation():
    """Start audio conversation"""
    try:
        # Initialize conversation handler
        handler = ConversationHandler(config_manager, api_key)
        
        # Set up callbacks
        handler.set_callbacks(
            on_transcript_update=on_transcript_update,
            on_conversation_finished=on_conversation_finished,
            on_error=on_conversation_error
        )
        
        # Start conversation
        if asyncio.run(handler.start_conversation(patient_prompt)):
            st.session_state.audio_conversation_handler = handler
            st.session_state.audio_conversation_active = True
            st.session_state.conversation_status = handler.get_conversation_status()
            st.success("Conversation started! You can now speak with the patient.")
            st.rerun()
        else:
            st.error("Failed to start conversation. Please try again.")
            
    except Exception as e:
        st.error(f"Error starting conversation: {e}")

def end_conversation():
    """End audio conversation"""
    try:
        if st.session_state.audio_conversation_handler:
            # End conversation and get data
            conversation_data = asyncio.run(
                st.session_state.audio_conversation_handler.end_conversation()
            )
            
            # Save to database
            if conversation_data:
                save_conversation_to_db(conversation_data)
            
            # Reset session state
            st.session_state.audio_conversation_handler = None
            st.session_state.audio_conversation_active = False
            st.session_state.conversation_status = {"status": "inactive"}
            
            st.success("Conversation ended and saved successfully!")
            st.rerun()
            
    except Exception as e:
        st.error(f"Error ending conversation: {e}")

def pause_conversation():
    """Pause audio conversation"""
    try:
        if st.session_state.audio_conversation_handler:
            asyncio.run(st.session_state.audio_conversation_handler.pause_conversation())
            st.session_state.conversation_status = st.session_state.audio_conversation_handler.get_conversation_status()
            st.info("Conversation paused.")
            st.rerun()
    except Exception as e:
        st.error(f"Error pausing conversation: {e}")

def resume_conversation():
    """Resume audio conversation"""
    try:
        if st.session_state.audio_conversation_handler:
            asyncio.run(st.session_state.audio_conversation_handler.resume_conversation())
            st.session_state.conversation_status = st.session_state.audio_conversation_handler.get_conversation_status()
            st.info("Conversation resumed.")
            st.rerun()
    except Exception as e:
        st.error(f"Error resuming conversation: {e}")

# Callback functions
def on_transcript_update(speaker: str, text: str, full_transcript: Dict[str, str]):
    """Handle transcript updates"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    
    # Add to transcript history
    st.session_state.audio_transcript.append({
        "timestamp": timestamp,
        "speaker": speaker,
        "text": text
    })
    
    # Update conversation status
    if st.session_state.audio_conversation_handler:
        st.session_state.conversation_status = st.session_state.audio_conversation_handler.get_conversation_status()

def on_conversation_finished(conversation_data: Dict[str, Any]):
    """Handle conversation completion"""
    save_conversation_to_db(conversation_data)
    st.session_state.audio_conversation_active = False
    st.session_state.conversation_status = {"status": "inactive"}

def on_conversation_error(error_message: str):
    """Handle conversation errors"""
    st.error(f"Conversation error: {error_message}")

def save_conversation_to_db(conversation_data: Dict[str, Any]):
    """Save conversation data to MongoDB"""
    try:
        mongodb_uri = st.session_state.get("mongodb_uri", "")
        if not mongodb_uri:
            st.warning("MongoDB URI not configured. Conversation not saved.")
            return
        
        # Initialize MongoDB client
        mongo_client = MongoDBRealtimeClient(mongodb_uri)
        if mongo_client.connect():
            # Save conversation
            session_id = mongo_client.log_audio_transcript(
                identifier=st.session_state.get("user_identifier", "unknown"),
                conversation_type="patient",
                conversation_data=conversation_data
            )
            
            if session_id:
                st.session_state.audio_session_id = session_id
                st.session_state["part_1_done"] = True
                st.success("Conversation saved successfully!")
            else:
                st.error("Failed to save conversation to database.")
                
            mongo_client.disconnect()
        else:
            st.error("Failed to connect to database.")
            
    except Exception as e:
        st.error(f"Error saving conversation: {e}")

# Audio interface
st.subheader("🎙️ Audio Interface")

# Initialize audio manager
if "audio_manager" not in st.session_state:
    st.session_state.audio_manager = AudioManager(config_manager)

# Display audio controls
audio_manager = st.session_state.audio_manager
audio_manager.initialize_audio_interface()

# Handle audio messages from browser
if "audio_message_queue" not in st.session_state:
    st.session_state.audio_message_queue = []

# Process audio messages
def process_audio_message(audio_data: str):
    """Process audio message from browser"""
    try:
        if st.session_state.audio_conversation_handler and st.session_state.audio_conversation_active:
            # Send audio to conversation handler
            success = asyncio.run(
                st.session_state.audio_conversation_handler.send_audio_message(audio_data)
            )
            
            if success:
                st.session_state.conversation_status = st.session_state.audio_conversation_handler.get_conversation_status()
            else:
                st.error("Failed to send audio message.")
                
    except Exception as e:
        st.error(f"Error processing audio: {e}")

# Conversation control buttons
st.subheader("🎮 Conversation Controls")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if not st.session_state.audio_conversation_active:
        if st.button("🎙️ Start Conversation", use_container_width=True):
            start_conversation()
    else:
        st.button("🎙️ Start Conversation", disabled=True, use_container_width=True)

with col2:
    if st.session_state.audio_conversation_active:
        if st.session_state.conversation_status.get("is_paused", False):
            if st.button("▶️ Resume", use_container_width=True):
                resume_conversation()
        else:
            if st.button("⏸️ Pause", use_container_width=True):
                pause_conversation()
    else:
        st.button("⏸️ Pause", disabled=True, use_container_width=True)

with col3:
    if st.session_state.audio_conversation_active:
        if st.button("🛑 End Conversation", use_container_width=True):
            end_conversation()
    else:
        st.button("🛑 End Conversation", disabled=True, use_container_width=True)

with col4:
    if st.button("🔄 Refresh Status", use_container_width=True):
        if st.session_state.audio_conversation_handler:
            st.session_state.conversation_status = st.session_state.audio_conversation_handler.get_conversation_status()
        st.rerun()

# Live transcript display
if ui_settings.get("show_live_transcript", True):
    st.subheader("📝 Live Transcript")
    
    # Create transcript container
    transcript_container = st.container()
    
    with transcript_container:
        if st.session_state.audio_transcript:
            # Display transcript in chat format
            for entry in st.session_state.audio_transcript[-10:]:  # Show last 10 entries
                timestamp = entry["timestamp"]
                speaker = entry["speaker"]
                text = entry["text"]
                
                if speaker == "user":
                    with st.chat_message("user"):
                        st.write(f"**[{timestamp}]** {text}")
                else:
                    with st.chat_message("assistant"):
                        st.write(f"**[{timestamp}]** {text}")
        else:
            st.info("Start the conversation to see the live transcript here.")

# Text fallback option
st.subheader("💬 Text Fallback")
st.info("If audio isn't working, you can send a text message as a backup.")

text_input = st.text_input(
    "Send text message:",
    disabled=not st.session_state.audio_conversation_active,
    placeholder="Type your message here..."
)

if st.button("Send Text", disabled=not st.session_state.audio_conversation_active):
    if text_input.strip():
        try:
            if st.session_state.audio_conversation_handler:
                success = asyncio.run(
                    st.session_state.audio_conversation_handler.send_text_message(text_input)
                )
                
                if success:
                    st.session_state.conversation_status = st.session_state.audio_conversation_handler.get_conversation_status()
                    st.success("Text message sent!")
                else:
                    st.error("Failed to send text message.")
                    
        except Exception as e:
            st.error(f"Error sending text: {e}")

# Settings and help
with st.expander("⚙️ Audio Settings & Help"):
    st.markdown("""
    ### Audio Settings
    - **Voice**: The patient speaks with a natural conversational voice
    - **Volume**: Adjust using the volume slider in the audio interface
    - **Quality**: High-quality audio processing for clear conversation
    
    ### How to Use
    1. Click "Start Conversation" to begin
    2. Click the microphone button to start speaking
    3. Speak naturally - the patient will respond automatically
    4. Use pause/resume controls as needed
    5. End conversation when complete
    
    ### Troubleshooting
    - **Microphone not working**: Check browser permissions
    - **No audio playback**: Check device volume and speakers
    - **Poor quality**: Ensure good internet connection
    - **Stuck or frozen**: Use the "Refresh Status" button
    
    ### Backup Options
    - Use text input if audio fails
    - Conversation will be saved regardless of method used
    """)

# Progress to next phase
if st.session_state.get("part_1_done", False) and not st.session_state.audio_conversation_active:
    st.success("✅ Patient conversation completed!")
    st.info("You can now proceed to the Supervisor Conversation page.")
    
    if st.button("➡️ Go to Supervisor Conversation", use_container_width=True):
        st.switch_page("pages/2_Supervisor_Conversation.py")

# Auto-refresh for status updates
if st.session_state.audio_conversation_active:
    # Auto-refresh every 5 seconds when conversation is active
    time.sleep(0.1)  # Small delay to prevent excessive refreshing
    if st.session_state.audio_conversation_handler:
        current_status = st.session_state.audio_conversation_handler.get_conversation_status()
        if current_status != st.session_state.conversation_status:
            st.session_state.conversation_status = current_status
            st.rerun()

# JavaScript for handling audio messages
st.components.v1.html("""
<script>
    // Listen for audio messages from the audio interface
    window.addEventListener('message', function(event) {
        if (event.data.type === 'audio_data') {
            // Send audio data to Streamlit
            window.parent.postMessage({
                type: 'streamlit_audio_data',
                audio: event.data.data
            }, '*');
        }
    });
</script>
""", height=0)