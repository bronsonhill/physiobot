import streamlit as st
import json
import logging
from datetime import datetime, timezone

from Home import setup
from utils.mongodb_realtime import log_audio_transcript
from components.audio_conversation import audio_conversation

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

# Check if patient conversation is already finished
if st.session_state.get("p_conversation_finished", False):
    st.success("✅ Patient conversation completed! You can now proceed to the Supervisor conversation.")
    st.stop()

# Setup OpenAI client
client = setup()

def get_patient_instructions():
    """Get patient instructions for the conversation"""
    try:
        with open("./prompts/audio_patient_prompt.txt", "r") as file:
            return file.read()
    except FileNotFoundError:
        # Fallback to regular prompt with audio adaptations
        patient_instructions = st.session_state.get("patient_prompt", "")
        return f"""{patient_instructions}

IMPORTANT AUDIO CONVERSATION GUIDELINES:
- You are having a spoken conversation, not a text chat
- Speak naturally and conversationally
- Keep responses concise and clear (2-3 sentences max)
- Use verbal acknowledgments like "mm-hmm", "I see", "okay"
- If you don't understand something, ask for clarification naturally
- Express emotions through your tone of voice appropriately
- Remember this is a learning experience for a physiotherapy student
- Be patient and encouraging while staying in character
- Stay focused on the physiotherapy consultation scenario
"""

# Page title and header
st.title("🗣️ Audio Conversation with your Patient")
st.markdown("---")

# Add a test button for debugging (can be removed in production)
col1, col2 = st.columns([1, 1])

with col1:
    if st.button("🔧 Test Conversation Completion (Debug)"):
        test_data = {
            "transcript_segments": [
                {
                    "timestamp": "2025-06-30T08:00:00.000Z",
                    "speaker": "assistant",
                    "text": "Hi, I've been having some lower back pain."
                },
                {
                    "timestamp": "2025-06-30T08:01:00.000Z", 
                    "speaker": "user",
                    "text": "Tell me more about your symptoms."
                }
            ],
            "session_summary": {
                "duration_seconds": 60,
                "total_exchanges": 2
            },
            "conversation_metrics": {
                "total_exchanges": 2,
                "user_segments": 1,
                "assistant_segments": 1
            }
        }
        st.session_state["conversation_complete_data"] = test_data
        logger.info("=== TEST CONVERSATION DATA SET ===")
        st.success("✅ Test conversation data set! Check the logs below.")
        st.rerun()

with col2:
    if st.button("🗑️ Clear Test Data"):
        if "conversation_complete_data" in st.session_state:
            del st.session_state["conversation_complete_data"]
        logger.info("Test data cleared")
        st.success("Test data cleared")
        st.rerun()

# Create the audio conversation component
st.markdown("### Audio Conversation Interface")

# Get patient instructions and API key
instructions = get_patient_instructions()
api_key = st.secrets["OPENAI_API_KEY"]

# Use the custom audio conversation component
conversation_result = audio_conversation(
    instructions=instructions,
    api_key=api_key,
    conversation_id=f"patient_conv_{st.session_state.get('user_identifier', 'anonymous')}",
    user_identifier=st.session_state.get("user_identifier", "anonymous"),
    key="patient_conversation",
    height=1000
)

# Handle conversation completion
if conversation_result:
    logger.info("=== CONVERSATION COMPLETION FLOW STARTED ===")
    logger.info(f"Received conversation result: {type(conversation_result)}")
    logger.info(f"Result keys: {list(conversation_result.keys()) if isinstance(conversation_result, dict) else 'Not a dict'}")
    
    # Store in session state
    st.session_state["conversation_complete_data"] = conversation_result
    logger.info("Stored conversation data in session state")
    
    # Show immediate feedback
    st.success("🎉 Conversation data received from component!")
    st.rerun()

# Process completed conversation data
if st.session_state.get("conversation_complete_data"):
    logger.info("=== PROCESSING CONVERSATION COMPLETION ===")
    transcript_data = st.session_state["conversation_complete_data"]
    
    logger.info(f"Processing transcript data: {type(transcript_data)}")
    logger.info(f"Transcript data keys: {list(transcript_data.keys()) if isinstance(transcript_data, dict) else 'Not a dict'}")
    logger.info(f"Session state keys: {list(st.session_state.keys())}")
    logger.info(f"User identifier: {st.session_state.get('user_identifier', 'NOT_FOUND')}")
    logger.info(f"MongoDB URI available: {bool(st.session_state.get('mongodb_uri', None))}")
    
    # Log transcript to database
    try:
        logger.info("Attempting to log transcript to database...")
        session_id = log_audio_transcript(
            st.session_state["mongodb_uri"],
            "patient",
            transcript_data
        )
        
        logger.info(f"Database logging result - Session ID: {session_id}")
        
        if session_id:
            st.session_state["session_id"] = session_id
            st.session_state["p_conversation_finished"] = True
            st.session_state["part_1_done"] = True
            
            logger.info("Successfully updated session state")
            logger.info(f"Session ID stored: {st.session_state.get('session_id')}")
            logger.info(f"Conversation finished flag: {st.session_state.get('p_conversation_finished')}")
            
            # Clear the completion data
            del st.session_state["conversation_complete_data"]
            logger.info("Cleared conversation_complete_data from session state")
            
            st.success("✅ Conversation completed and saved successfully!")
            st.balloons()
            
            # Show next steps
            st.info("🎯 **Next Step:** Go to the 'Supervisor Conversation' page to get feedback on your conversation.")
            
            # Show conversation summary
            with st.expander("📝 Conversation Summary", expanded=True):
                segments = transcript_data.get("transcript_segments", [])
                if segments:
                    st.write(f"**Total exchanges:** {len(segments)}")
                    st.write(f"**User messages:** {len([s for s in segments if s.get('speaker') == 'user'])}")
                    st.write(f"**Patient responses:** {len([s for s in segments if s.get('speaker') == 'assistant'])}")
                    
                    # Show a sample of the conversation
                    st.write("**Sample conversation:**")
                    for i, segment in enumerate(segments[:4]):  # Show first 4 exchanges
                        speaker_icon = "🧑‍⚕️" if segment.get('speaker') == 'user' else "🤒"
                        speaker_label = "You" if segment.get('speaker') == 'user' else "Patient"
                        st.write(f"{speaker_icon} **{speaker_label}:** {segment.get('text', '')}")
                    
                    if len(segments) > 4:
                        st.write(f"... and {len(segments) - 4} more exchanges")
                else:
                    st.write("No conversation segments found")
            
        else:
            logger.error("Database logging returned None - no session ID created")
            st.error("❌ Failed to save conversation to database. Please try again.")
            
    except Exception as e:
        logger.error(f"=== DATABASE LOGGING ERROR ===")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Error message: {str(e)}")
        logger.error(f"Error details: {e}")
        
        # Log additional debugging info
        logger.error(f"MongoDB URI length: {len(st.session_state.get('mongodb_uri', '')) if st.session_state.get('mongodb_uri') else 'None'}")
        logger.error(f"Transcript data type: {type(transcript_data)}")
        logger.error(f"Transcript data sample: {str(transcript_data)[:200] if transcript_data else 'None'}")
        
        st.error(f"Error saving conversation: {str(e)}")
        
        # Show error details in expander for debugging
        with st.expander("🔍 Error Details (for debugging)"):
            st.write(f"**Error type:** {type(e).__name__}")
            st.write(f"**Error message:** {str(e)}")
            st.write(f"**MongoDB URI available:** {bool(st.session_state.get('mongodb_uri'))}")
            st.write(f"**Transcript data type:** {type(transcript_data)}")
            if transcript_data:
                st.write(f"**Transcript sample:** {str(transcript_data)[:200]}...")

# Add debug information in sidebar
st.sidebar.markdown("### 🔍 Debug Information")
st.sidebar.write(f"**User ID:** {st.session_state.get('user_identifier', 'Not set')}")
st.sidebar.write(f"**Session ID:** {st.session_state.get('session_id', 'Not set')}")
st.sidebar.write(f"**Conversation finished:** {st.session_state.get('p_conversation_finished', False)}")
st.sidebar.write(f"**MongoDB URI available:** {bool(st.session_state.get('mongodb_uri'))}")

if st.session_state.get("conversation_complete_data"):
    st.sidebar.write("✅ Conversation data ready for processing")
    data = st.session_state["conversation_complete_data"]
    if isinstance(data, dict):
        st.sidebar.write(f"**Data keys:** {list(data.keys())}")
        segments = data.get("transcript_segments", [])
        st.sidebar.write(f"**Segments:** {len(segments)}")
else:
    st.sidebar.write("❌ No conversation data pending")

# Add custom CSS for better styling
st.markdown("""
<style>
    .stButton > button {
        width: 100%;
        margin: 5px 0;
    }
    
    /* Hide the default Streamlit elements for cleaner look */
    .stDeployButton {
        display: none;
    }
    
    #MainMenu {
        visibility: hidden;
    }
    
    footer {
        visibility: hidden;
    }
    
    /* Make component container full width */
    .element-container iframe {
        width: 100% !important;
    }
</style>
""", unsafe_allow_html=True)