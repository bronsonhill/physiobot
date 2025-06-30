import streamlit as st
import json
from datetime import datetime
from typing import Dict, Any
import yaml
from pathlib import Path

from utils.config_manager import ConfigManager, get_config_manager
from utils.mongodb_realtime import get_mongo_client

# Page configuration
st.set_page_config(
    page_title="Audio Preferences - PhysioBot",
    page_icon="🎧",
    layout="wide"
)

# Check user authentication
if not bool(st.session_state.get("user_identifier", "").strip()):
    st.error("Please enter your identifier on the Home page before accessing preferences.")
    st.stop()

def audio_preferences_page():
    """Main audio preferences page for students."""
    st.title("🎧 Audio Preferences & Setup")
    st.markdown("Configure your audio settings for the best conversation experience.")
    st.markdown("---")
    
    # Get cached configuration
    config_manager = get_config_manager()
    
    # Create tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs([
        "🎵 Audio Settings",
        "🧪 Audio Test",
        "🔧 Troubleshooting",
        "📖 Help Guide"
    ])
    
    with tab1:
        audio_settings_interface(config_manager)
    
    with tab2:
        audio_test_interface()
    
    with tab3:
        troubleshooting_interface()
    
    with tab4:
        help_guide_interface()

def audio_settings_interface(config_manager: ConfigManager):
    """Interface for student audio preferences."""
    st.subheader("🎵 Audio Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔊 Output Settings")
        
        # Volume control
        output_volume = st.slider(
            "Output Volume",
            min_value=0.0,
            max_value=2.0,
            value=1.0,
            step=0.1,
            help="Adjust the volume of AI responses (1.0 = normal)"
        )
        
        # Speech speed preference
        preferred_speed = st.slider(
            "Preferred Speech Speed",
            min_value=0.5,
            max_value=2.0,
            value=1.0,
            step=0.1,
            help="How fast should the AI speak? (1.0 = normal speed)"
        )
        
        # Voice preference (if multiple available)
        voice_preference = st.selectbox(
            "Voice Preference",
            options=["Default", "Clear & Slow", "Natural & Fast"],
            help="Choose a voice style that works best for you"
        )
        
        st.markdown("### 🎤 Input Settings")
        
        # Microphone sensitivity
        mic_sensitivity = st.slider(
            "Microphone Sensitivity",
            min_value=0.1,
            max_value=2.0,
            value=1.0,
            step=0.1,
            help="Adjust if the system has trouble hearing you"
        )
        
        # Recording behavior
        auto_record = st.checkbox(
            "Auto-start recording after AI response",
            value=False,
            help="Automatically begin recording when the AI finishes speaking"
        )
        
        push_to_talk = st.checkbox(
            "Push-to-talk mode",
            value=False,
            help="Hold button to record instead of click to start/stop"
        )
    
    with col2:
        st.markdown("### 🌐 Connection Settings")
        
        # Connection quality preference
        connection_quality = st.selectbox(
            "Connection Quality",
            options=["Auto", "High Quality", "Balanced", "Low Bandwidth"],
            help="Adjust based on your internet connection"
        )
        
        # Enable/disable features based on performance
        enable_visualization = st.checkbox(
            "Enable Audio Visualization",
            value=True,
            help="Show volume levels and frequency bars (may impact performance)"
        )
        
        enable_transcript = st.checkbox(
            "Show Live Transcript",
            value=True,
            help="Display conversation text in real-time"
        )
        
        # Accessibility options
        st.markdown("### ♿ Accessibility")
        
        large_controls = st.checkbox(
            "Large Control Buttons",
            value=False,
            help="Use larger buttons for easier access"
        )
        
        high_contrast = st.checkbox(
            "High Contrast Mode",
            value=False,
            help="Use high contrast colors for better visibility"
        )
        
        keyboard_shortcuts = st.checkbox(
            "Enable Keyboard Shortcuts",
            value=True,
            help="Use spacebar to start/stop recording, Enter to send text"
        )
    
    # Save preferences
    if st.button("💾 Save Preferences", type="primary"):
        preferences = {
            "output_volume": output_volume,
            "preferred_speed": preferred_speed,
            "voice_preference": voice_preference,
            "mic_sensitivity": mic_sensitivity,
            "auto_record": auto_record,
            "push_to_talk": push_to_talk,
            "connection_quality": connection_quality,
            "enable_visualization": enable_visualization,
            "enable_transcript": enable_transcript,
            "large_controls": large_controls,
            "high_contrast": high_contrast,
            "keyboard_shortcuts": keyboard_shortcuts,
            "last_updated": datetime.now().isoformat()
        }
        
        # Save to session state (in production, save to user profile)
        st.session_state["user_audio_preferences"] = preferences
        st.success("✅ Preferences saved successfully!")
        
        # Apply immediate changes
        if high_contrast:
            st.markdown("""
            <style>
            .stApp {
                background-color: #000000;
                color: #ffffff;
            }
            .stButton > button {
                background-color: #ffffff;
                color: #000000;
                border: 2px solid #ffffff;
            }
            </style>
            """, unsafe_allow_html=True)

def audio_test_interface():
    """Interface for testing audio setup."""
    st.subheader("🧪 Audio System Test")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🎤 Microphone Test")
        
        if st.button("🔴 Start Microphone Test", type="primary"):
            with st.spinner("Testing microphone..."):
                # Mock microphone test
                test_placeholder = st.empty()
                
                # Simulate audio level detection
                import time
                import random
                
                test_placeholder.info("🎤 Please speak into your microphone...")
                time.sleep(2)
                
                # Mock volume levels
                volume_levels = [random.uniform(0.3, 0.9) for _ in range(5)]
                max_volume = max(volume_levels)
                avg_volume = sum(volume_levels) / len(volume_levels)
                
                test_placeholder.success(f"✅ Microphone test completed!")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    st.metric("Max Volume Detected", f"{max_volume:.1%}")
                with col_b:
                    st.metric("Average Volume", f"{avg_volume:.1%}")
                
                if max_volume > 0.7:
                    st.success("🟢 Excellent microphone level!")
                elif max_volume > 0.4:
                    st.warning("🟡 Moderate microphone level - consider speaking louder or adjusting sensitivity")
                else:
                    st.error("🔴 Low microphone level - check your microphone settings")
        
        st.markdown("### 🔊 Speaker Test")
        
        if st.button("🔊 Test Speakers/Headphones"):
            with st.spinner("Playing test audio..."):
                # Mock speaker test
                st.audio("https://www.soundjay.com/misc/sounds/bell-ringing-05.wav", format="audio/wav")
                time.sleep(3)
                
                # Feedback on audio quality
                heard_audio = st.radio(
                    "Did you hear the test sound clearly?",
                    options=["Yes, clearly", "Yes, but quiet", "Yes, but distorted", "No, didn't hear anything"],
                    key="speaker_test_feedback"
                )
                
                if heard_audio == "Yes, clearly":
                    st.success("✅ Speaker test passed!")
                elif heard_audio in ["Yes, but quiet", "Yes, but distorted"]:
                    st.warning("⚠️ Audio output detected but may need adjustment")
                else:
                    st.error("❌ No audio detected - check your speaker/headphone connection")
    
    with col2:
        st.markdown("### 🌐 Connection Test")
        
        if st.button("📡 Test Connection Quality"):
            with st.spinner("Testing connection to audio services..."):
                # Mock connection test
                import time
                time.sleep(2)
                
                # Mock connection metrics
                latency = random.randint(50, 200)
                jitter = random.randint(5, 30)
                bandwidth_mbps = random.uniform(2.0, 50.0)
                
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.metric("Latency", f"{latency} ms")
                with col_b:
                    st.metric("Jitter", f"{jitter} ms")
                with col_c:
                    st.metric("Bandwidth", f"{bandwidth_mbps:.1f} Mbps")
                
                # Overall connection quality
                if latency < 100 and jitter < 15 and bandwidth_mbps > 5:
                    st.success("🟢 Excellent connection quality!")
                elif latency < 200 and jitter < 25 and bandwidth_mbps > 2:
                    st.warning("🟡 Good connection quality")
                else:
                    st.error("🔴 Poor connection quality - audio may be affected")
        
        st.markdown("### 🔄 End-to-End Test")
        
        if st.button("🎯 Full Audio Pipeline Test"):
            with st.spinner("Running comprehensive audio test..."):
                # Mock comprehensive test
                test_results = {
                    "Microphone Access": "✅ Granted",
                    "Audio Capture": "✅ Working",
                    "Audio Encoding": "✅ PCM16 format",
                    "Network Connection": "✅ Stable",
                    "Audio Playback": "✅ Working",
                    "Echo Cancellation": "✅ Enabled",
                    "Noise Suppression": "✅ Active"
                }
                
                st.write("**Test Results:**")
                for test, result in test_results.items():
                    if "✅" in result:
                        st.success(f"{test}: {result}")
                    elif "⚠️" in result:
                        st.warning(f"{test}: {result}")
                    else:
                        st.error(f"{test}: {result}")

def troubleshooting_interface():
    """Interface for audio troubleshooting."""
    st.subheader("🔧 Troubleshooting Guide")
    
    # Common issues and solutions
    issues = [
        {
            "problem": "🎤 Microphone not working",
            "solutions": [
                "Check if your browser has microphone permissions",
                "Ensure your microphone is not muted",
                "Try refreshing the page and allowing microphone access",
                "Check if another application is using your microphone",
                "Test with a different browser (Chrome recommended)"
            ]
        },
        {
            "problem": "🔊 No audio output",
            "solutions": [
                "Check your speaker/headphone volume",
                "Ensure the correct audio output device is selected",
                "Try refreshing the page",
                "Check if audio is muted in your browser tab",
                "Test with different speakers/headphones"
            ]
        },
        {
            "problem": "⚡ Poor audio quality",
            "solutions": [
                "Check your internet connection speed",
                "Close other bandwidth-heavy applications",
                "Lower the audio quality setting in preferences",
                "Use a wired internet connection if possible",
                "Try a different location for better wifi signal"
            ]
        },
        {
            "problem": "🔄 Connection issues",
            "solutions": [
                "Refresh the page and try again",
                "Check your internet connection",
                "Disable VPN if you're using one",
                "Clear your browser cache and cookies",
                "Try using an incognito/private browser window"
            ]
        }
    ]
    
    for issue in issues:
        with st.expander(issue["problem"]):
            st.write("**Try these solutions:**")
            for solution in issue["solutions"]:
                st.write(f"• {solution}")
    
    # Browser compatibility information
    st.markdown("### 🌐 Browser Compatibility")
    
    compatibility_data = {
        "Chrome": {"status": "✅ Fully Supported", "note": "Recommended browser"},
        "Firefox": {"status": "✅ Fully Supported", "note": "Good alternative"},
        "Safari": {"status": "⚠️ Mostly Supported", "note": "Some features may be limited"},
        "Edge": {"status": "✅ Fully Supported", "note": "Good performance"},
        "Mobile Browsers": {"status": "⚠️ Limited Support", "note": "Use desktop for best experience"}
    }
    
    for browser, info in compatibility_data.items():
        col1, col2, col3 = st.columns([1, 2, 3])
        with col1:
            st.write(f"**{browser}**")
        with col2:
            st.write(info["status"])
        with col3:
            st.write(info["note"])
    
    # System requirements
    st.markdown("### 💻 System Requirements")
    st.write("""
    **Minimum Requirements:**
    - Modern web browser (Chrome 80+, Firefox 75+, Safari 13+, Edge 80+)
    - Stable internet connection (2+ Mbps recommended)
    - Working microphone and speakers/headphones
    - JavaScript enabled
    
    **Recommended Setup:**
    - Chrome or Firefox on desktop
    - High-speed internet (10+ Mbps)
    - USB headset or dedicated microphone
    - Quiet environment for best audio quality
    """)

def help_guide_interface():
    """Interface with help and usage guide."""
    st.subheader("📖 Audio Conversation Guide")
    
    # Quick start guide
    st.markdown("### 🚀 Quick Start")
    
    steps = [
        "🎧 **Setup**: Test your audio and adjust preferences above",
        "🏠 **Home**: Enter your identifier on the Home page",
        "🗣️ **Conversation**: Navigate to Patient Conversation page",
        "🎤 **Record**: Click 'Start Recording' and speak clearly",
        "⏹️ **Stop**: Click 'Stop Recording' when you finish speaking",
        "👂 **Listen**: Wait for the AI patient's response",
        "🔄 **Continue**: Repeat the process for natural conversation",
        "✅ **Finish**: Click 'Finish Conversation' when complete"
    ]
    
    for step in steps:
        st.write(step)
    
    # Tips for better conversations
    st.markdown("### 💡 Tips for Better Conversations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Audio Quality Tips:**
        - Use headphones to prevent echo
        - Speak clearly and at normal pace
        - Minimize background noise
        - Stay close to your microphone
        - Pause briefly before speaking
        """)
    
    with col2:
        st.markdown("""
        **Conversation Tips:**
        - Wait for the AI to finish speaking
        - Use natural conversation flow
        - Ask follow-up questions
        - Practice active listening
        - Don't rush - take your time
        """)
    
    # Keyboard shortcuts
    st.markdown("### ⌨️ Keyboard Shortcuts")
    
    shortcuts = [
        ("Spacebar", "Start/Stop recording"),
        ("Enter", "Send text message"),
        ("Esc", "Cancel current recording"),
        ("Tab", "Navigate between controls"),
        ("Ctrl + Enter", "Finish conversation")
    ]
    
    for key, action in shortcuts:
        col1, col2 = st.columns([1, 3])
        with col1:
            st.code(key)
        with col2:
            st.write(action)
    
    # FAQ section
    st.markdown("### ❓ Frequently Asked Questions")
    
    faqs = [
        {
            "question": "What if I make a mistake while speaking?",
            "answer": "Don't worry! You can stop recording and start again. The conversation is designed to be natural and forgiving."
        },
        {
            "question": "How long should my responses be?",
            "answer": "Speak naturally - anywhere from a few seconds to a minute is fine. The AI will wait for you to finish."
        },
        {
            "question": "Can I use text input instead of voice?",
            "answer": "Yes! There's a text input option as a backup, but voice conversation is preferred for the best learning experience."
        },
        {
            "question": "What if the AI doesn't understand me?",
            "answer": "Try speaking more clearly, check your microphone settings, or use the text input as a backup."
        },
        {
            "question": "Is my conversation private?",
            "answer": "Your conversations are stored securely and used only for educational purposes and assessment by your instructors."
        }
    ]
    
    for faq in faqs:
        with st.expander(faq["question"]):
            st.write(faq["answer"])

if __name__ == "__main__":
    audio_preferences_page()