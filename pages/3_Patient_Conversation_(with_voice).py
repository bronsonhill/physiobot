import streamlit as st
from st_realtime_audio import realtime_audio_conversation
from Home import setup
from utils.mongodb import log_transcript

# Check if user has entered identifier
if not bool(st.session_state.get("user_identifier", "").strip()):
    st.error("Please enter your identifier on the Home page before starting the conversation.")
    st.stop()

# Setup the application
client = setup()

# Page configuration
st.set_page_config(
    page_title="PhysioBot Audio Conversation",
    page_icon="🎤",
    layout="wide"
)

st.title("Conversation with Patient")
st.markdown("Your patient has just sat down in front of you in the consultation room. Start a conversation with them!")

# Check if OpenAI API key is available
if not st.secrets.get("OPENAI_API_KEY"):
    st.error("OpenAI API key not configured. Please check your secrets configuration.")
    st.stop()


# Only show the audio conversation component if not finished
if not st.session_state.get("audio_conversation_finished", False):
    # Create the real-time audio conversation component
    conversation_result = realtime_audio_conversation(
        api_key=st.secrets["OPENAI_API_KEY"],
        voice="alloy",
        instructions=st.session_state["patient_prompt"],
        auto_start=False,
        temperature=0.8,
        turn_detection_threshold=0.5,
        key="audio_conversation"
    )

    # Display any errors
    if conversation_result.get("error"):
        st.error(f"Error: {conversation_result['error']}")

    # Display conversation transcript
    if conversation_result.get("transcript"):
        st.subheader("Conversation Transcript")
        
        # Sort transcript by sequence to ensure correct chronological order
        sorted_transcript = sorted(
            conversation_result["transcript"], 
            key=lambda x: x.get("sequence", x.get("timestamp", 0))
        )
        
        # Display transcript in chat format
        for message in sorted_transcript:
            if message["type"] == "user":
                st.chat_message("user").write(message["content"])
            else:
                st.chat_message("assistant").write(message["content"])
        
        # Store transcript in session state for logging
        if sorted_transcript and not st.session_state.get("audio_transcript_logged", False):
            # Convert transcript to chat history format
            chat_history = []
            for message in sorted_transcript:
                role = "user" if message["type"] == "user" else "assistant"
                chat_history.append({"role": role, "content": message["content"]})
            
            st.session_state["audio_chat_history"] = chat_history

    # Add finish conversation button
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if conversation_result.get("transcript") and st.session_state.get("audio_chat_history"):
            if st.button("Finish Audio Conversation", key="finish_audio", use_container_width=True):
                st.session_state.audio_conversation_finished = True
                
                # Log the transcript
                session_id = log_transcript(
                    st.session_state["mongodb_uri"],
                    "patient_audio",
                    st.session_state.audio_chat_history
                )
                st.session_state.audio_session_id = session_id
                st.success("Audio conversation logged successfully!")
                st.rerun()

else:
    # Show completed conversation transcript
    if st.session_state.get("audio_chat_history"):
        st.subheader("Completed Audio Conversation")
        st.success("✅ Audio conversation completed and logged successfully!")
        
        # Display the logged transcript
        for message in st.session_state.audio_chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Show session ID
        if st.session_state.get("audio_session_id"):
            st.info(f"Session ID: {st.session_state.audio_session_id}")

# Simple help section
with st.expander("How to Use Audio Conversation"):
    st.markdown("""
    **Getting Started:**
    1. Click "Start Conversation" 
    2. Allow microphone access when prompted
    3. Start speaking naturally!
    
    **Tips:**
    - Speak clearly and at normal volume
    - Wait for the AI to finish before speaking
    - Remember to click "Finish Audio Conversation" when done
    
    **Requirements:**
    - Microphone access
    - Stable internet connection
    - Chrome browser recommended for best experience
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>Real-time audio conversation powered by OpenAI's Real-time API</p>
</div>
""", unsafe_allow_html=True) 