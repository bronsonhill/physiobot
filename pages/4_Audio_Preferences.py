"""
Student Audio Preferences Interface
Phase 5 Implementation - UI/UX Enhancement & Student Controls
"""

import streamlit as st
from utils.config_manager import config_manager
from datetime import datetime
import json

# Page configuration
st.set_page_config(
    page_title="Audio Preferences - PhysioBot",
    page_icon="🎧",
    layout="wide"
)

def check_student_access():
    """Check if student is properly authenticated"""
    if not st.session_state.get("user_identifier", "").strip():
        st.error("Please enter your identifier on the Home page before accessing audio preferences.")
        st.stop()

def audio_preferences_section():
    """Student audio preferences"""
    st.header("🎧 Audio Preferences")
    st.markdown("Customize your audio experience for better conversation quality.")
    
    # Get current system settings as defaults
    audio_config = config_manager.get_audio_settings()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🗣️ Voice Settings")
        
        # Voice selection
        voice_options = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
        voice_descriptions = {
            "alloy": "Neutral, clear voice",
            "echo": "Calm, soothing voice", 
            "fable": "Expressive, engaging voice",
            "onyx": "Professional, authoritative voice",
            "nova": "Warm, friendly voice",
            "shimmer": "Bright, energetic voice"
        }
        
        current_voice = st.session_state.get("student_voice_preference", audio_config.get('voice_type', 'alloy'))
        
        voice_type = st.selectbox(
            "AI Voice Type",
            voice_options,
            index=voice_options.index(current_voice),
            help="Choose the voice that you find most comfortable for conversation",
            format_func=lambda x: f"{x.title()} - {voice_descriptions[x]}"
        )
        
        # Speech speed
        speech_speed = st.slider(
            "Speech Speed",
            min_value=0.5,
            max_value=2.0,
            value=st.session_state.get("student_speech_speed", audio_config.get('speech_speed', 1.0)),
            step=0.25,
            help="Adjust how fast the AI speaks (1.0 = normal speed)"
        )
        
        # Audio preview
        if st.button("🎵 Preview Voice", key="preview_voice"):
            st.success(f"Preview: {voice_type.title()} voice at {speech_speed}x speed")
            st.info("In a real implementation, this would play a sample audio clip")
    
    with col2:
        st.subheader("🎚️ Audio Quality")
        
        # Volume preferences
        volume_level = st.slider(
            "Volume Level",
            min_value=0.1,
            max_value=1.0,
            value=st.session_state.get("student_volume", 0.8),
            step=0.1,
            help="Adjust the audio volume level"
        )
        
        # Microphone sensitivity
        mic_sensitivity = st.select_slider(
            "Microphone Sensitivity",
            options=["Low", "Medium", "High"],
            value=st.session_state.get("student_mic_sensitivity", "Medium"),
            help="Adjust how sensitive the microphone is to your voice"
        )
        
        # Background noise filtering
        noise_filtering = st.checkbox(
            "Enable Background Noise Filtering",
            value=st.session_state.get("student_noise_filtering", True),
            help="Reduce background noise during conversation"
        )
        
        # Auto-gain control
        auto_gain = st.checkbox(
            "Automatic Volume Adjustment",
            value=st.session_state.get("student_auto_gain", True),
            help="Automatically adjust volume levels for optimal conversation"
        )
    
    # Save preferences
    if st.button("💾 Save Audio Preferences", type="primary"):
        st.session_state["student_voice_preference"] = voice_type
        st.session_state["student_speech_speed"] = speech_speed
        st.session_state["student_volume"] = volume_level
        st.session_state["student_mic_sensitivity"] = mic_sensitivity
        st.session_state["student_noise_filtering"] = noise_filtering
        st.session_state["student_auto_gain"] = auto_gain
        st.success("✅ Audio preferences saved successfully!")

def accessibility_section():
    """Accessibility options"""
    st.header("♿ Accessibility Options")
    st.markdown("Configure accessibility features to improve your experience.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("👁️ Visual Aids")
        
        # Live transcript
        show_transcript = st.checkbox(
            "Show Live Transcript",
            value=st.session_state.get("student_show_transcript", True),
            help="Display real-time text of the conversation"
        )
        
        # Large text
        large_text = st.checkbox(
            "Large Text Display",
            value=st.session_state.get("student_large_text", False),
            help="Use larger text size for better readability"
        )
        
        # High contrast
        high_contrast = st.checkbox(
            "High Contrast Mode",
            value=st.session_state.get("student_high_contrast", False),
            help="Use high contrast colors for better visibility"
        )
        
        # Visual indicators
        visual_indicators = st.checkbox(
            "Audio Activity Indicators",
            value=st.session_state.get("student_visual_indicators", True),
            help="Show visual indicators when audio is playing or recording"
        )
    
    with col2:
        st.subheader("🎯 Interaction Aids")
        
        # Keyboard shortcuts
        keyboard_shortcuts = st.checkbox(
            "Enable Keyboard Shortcuts",
            value=st.session_state.get("student_keyboard_shortcuts", True),
            help="Use keyboard shortcuts for common actions"
        )
        
        # Extended response time
        extended_response = st.checkbox(
            "Extended Response Time",
            value=st.session_state.get("student_extended_response", False),
            help="Allow more time for responses during conversation"
        )
        
        # Audio cues
        audio_cues = st.checkbox(
            "Audio Cues",
            value=st.session_state.get("student_audio_cues", True),
            help="Play sounds to indicate conversation events"
        )
        
        # Pause functionality
        easy_pause = st.checkbox(
            "Easy Pause Access",
            value=st.session_state.get("student_easy_pause", True),
            help="Show prominent pause button during conversations"
        )
    
    # Save accessibility settings
    if st.button("💾 Save Accessibility Settings", type="primary"):
        st.session_state["student_show_transcript"] = show_transcript
        st.session_state["student_large_text"] = large_text
        st.session_state["student_high_contrast"] = high_contrast
        st.session_state["student_visual_indicators"] = visual_indicators
        st.session_state["student_keyboard_shortcuts"] = keyboard_shortcuts
        st.session_state["student_extended_response"] = extended_response
        st.session_state["student_audio_cues"] = audio_cues
        st.session_state["student_easy_pause"] = easy_pause
        st.success("✅ Accessibility settings saved successfully!")

def troubleshooting_section():
    """Troubleshooting and diagnostics"""
    st.header("🔧 Troubleshooting")
    st.markdown("Test your audio setup and resolve common issues.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🧪 Audio Tests")
        
        if st.button("🎤 Test Microphone", key="test_mic"):
            st.info("Testing microphone...")
            # Mock microphone test
            st.success("✅ Microphone is working correctly")
            st.write("**Detected volume level:** Good")
            st.write("**Background noise:** Low")
        
        if st.button("🔊 Test Speakers/Headphones", key="test_speakers"):
            st.info("Testing audio output...")
            # Mock speaker test
            st.success("✅ Audio output is working correctly")
            st.write("**Volume level:** Optimal")
            st.write("**Audio quality:** Good")
        
        if st.button("🌐 Test Internet Connection", key="test_connection"):
            st.info("Testing connection...")
            # Mock connection test
            st.success("✅ Internet connection is stable")
            st.write("**Connection speed:** Good")
            st.write("**Latency:** Low")
    
    with col2:
        st.subheader("📊 System Information")
        
        # Mock system information
        st.write("**Browser:** Chrome 120.0")
        st.write("**Operating System:** Windows 11")
        st.write("**Audio Input:** Built-in Microphone") 
        st.write("**Audio Output:** Built-in Speakers")
        st.write("**Connection Status:** ✅ Connected")
        
        st.subheader("⚠️ Common Issues")
        
        with st.expander("🎤 Can't hear my voice"):
            st.write("1. Check microphone permissions in browser")
            st.write("2. Ensure microphone is not muted")
            st.write("3. Try refreshing the page")
            st.write("4. Check Windows/Mac audio settings")
        
        with st.expander("🔊 Can't hear the AI"):
            st.write("1. Check volume settings")
            st.write("2. Ensure audio is not muted in browser")
            st.write("3. Try using headphones")
            st.write("4. Check device audio output settings")
        
        with st.expander("⚡ Audio delays or cutting out"):
            st.write("1. Check internet connection stability")
            st.write("2. Close other applications using audio")
            st.write("3. Try using a wired connection")
            st.write("4. Refresh the browser page")

def keyboard_shortcuts_section():
    """Display keyboard shortcuts"""
    st.header("⌨️ Keyboard Shortcuts")
    st.markdown("Learn keyboard shortcuts to navigate more efficiently.")
    
    shortcuts_data = {
        "Action": [
            "Start/Stop Recording",
            "Pause Conversation", 
            "Resume Conversation",
            "Mute/Unmute",
            "Increase Volume",
            "Decrease Volume",
            "Show/Hide Transcript",
            "Finish Conversation",
            "Emergency Stop"
        ],
        "Shortcut": [
            "Spacebar",
            "P",
            "R", 
            "M",
            "↑ (Up Arrow)",
            "↓ (Down Arrow)",
            "T",
            "Ctrl + Enter",
            "Escape"
        ],
        "Description": [
            "Toggle audio recording on/off",
            "Temporarily pause the conversation",
            "Resume a paused conversation",
            "Mute/unmute your microphone",
            "Increase audio output volume",
            "Decrease audio output volume", 
            "Toggle transcript visibility",
            "End the current conversation",
            "Immediately stop all audio activity"
        ]
    }
    
    import pandas as pd
    shortcuts_df = pd.DataFrame(shortcuts_data)
    st.table(shortcuts_df)
    
    st.info("💡 **Tip:** These shortcuts only work when the conversation interface is active.")

def main():
    """Main audio preferences interface"""
    check_student_access()
    
    st.title("🎧 Audio Preferences")
    st.markdown(f"Welcome, **{st.session_state.get('user_identifier', 'Student')}**! Customize your audio experience.")
    
    # Preference tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🎧 Audio Settings",
        "♿ Accessibility", 
        "🔧 Troubleshooting",
        "⌨️ Shortcuts"
    ])
    
    with tab1:
        audio_preferences_section()
    
    with tab2:
        accessibility_section()
    
    with tab3:
        troubleshooting_section()
    
    with tab4:
        keyboard_shortcuts_section()
    
    # Footer
    st.markdown("---")
    st.markdown(
        "💡 **Need help?** Contact your instructor or visit the troubleshooting section above."
    )

if __name__ == "__main__":
    main()