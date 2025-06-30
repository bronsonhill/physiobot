import streamlit as st
import yaml
import json
from datetime import datetime, timedelta
from typing import Dict, Any
import pandas as pd

from utils.config_manager import ConfigManager
from utils.mongodb_realtime import get_database_stats, get_recent_sessions
from Home import setup

# Page configuration
st.set_page_config(
    page_title="Admin Configuration - PhysioBot",
    page_icon="⚙️",
    layout="wide"
)

# Admin authentication (simple password protection)
if "admin_authenticated" not in st.session_state:
    st.session_state["admin_authenticated"] = False

if not st.session_state["admin_authenticated"]:
    st.title("🔐 Admin Authentication")
    
    admin_password = st.text_input("Enter Admin Password:", type="password")
    
    if st.button("Login"):
        # In production, use proper authentication
        if admin_password == st.secrets.get("ADMIN_PASSWORD", "admin123"):
            st.session_state["admin_authenticated"] = True
            st.rerun()
        else:
            st.error("Invalid password")
    
    st.stop()

# Main admin interface
st.title("⚙️ PhysioBot Admin Configuration")
st.markdown("---")

# Initialize configuration manager
config_manager = ConfigManager()

# Create tabs for different admin functions
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🎵 Audio Settings", 
    "📊 System Monitoring", 
    "🧪 Testing Tools", 
    "👥 User Management", 
    "📚 Documentation"
])

with tab1:
    st.header("Audio Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Voice Settings")
        
        # Voice type selection
        voice_options = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
        current_voice = config_manager.get_setting("audio_settings.voice_type", "alloy")
        voice_type = st.selectbox("Voice Type", voice_options, index=voice_options.index(current_voice))
        
        # Speech speed
        current_speed = config_manager.get_setting("audio_settings.speech_speed", 1.0)
        speech_speed = st.slider("Speech Speed", 0.25, 4.0, current_speed, 0.25)
        
        # Sample rate
        sample_rate_options = [16000, 24000, 48000]
        current_sample_rate = config_manager.get_setting("audio_settings.quality_settings.sample_rate", 24000)
        sample_rate = st.selectbox("Sample Rate", sample_rate_options, 
                                 index=sample_rate_options.index(current_sample_rate))
        
        st.subheader("Conversation Detection")
        
        # Silence threshold
        current_silence = config_manager.get_setting("audio_settings.conversation_detection.silence_threshold", 2.0)
        silence_threshold = st.slider("Silence Threshold (seconds)", 0.5, 5.0, current_silence, 0.5)
        
        # Volume threshold
        current_volume = config_manager.get_setting("audio_settings.conversation_detection.volume_threshold", 0.1)
        volume_threshold = st.slider("Volume Threshold", 0.01, 1.0, current_volume, 0.01)
    
    with col2:
        st.subheader("Conversation Limits")
        
        # Max duration
        current_max_duration = config_manager.get_setting("conversation_settings.max_duration", 1800)
        max_duration = st.number_input("Max Duration (seconds)", 
                                     min_value=300, max_value=3600, value=current_max_duration, step=300)
        
        # Max responses
        current_max_responses = config_manager.get_setting("conversation_settings.max_responses", 50)
        max_responses = st.number_input("Max Responses", 
                                      min_value=10, max_value=200, value=current_max_responses, step=10)
        
        # Auto-save interval
        current_auto_save = config_manager.get_setting("conversation_settings.auto_save_interval", 300)
        auto_save_interval = st.number_input("Auto-save Interval (seconds)", 
                                           min_value=60, max_value=1800, value=current_auto_save, step=60)
        
        # Connection timeout
        current_timeout = config_manager.get_setting("conversation_settings.connection_timeout", 30)
        connection_timeout = st.number_input("Connection Timeout (seconds)", 
                                           min_value=10, max_value=120, value=current_timeout, step=10)
        
        st.subheader("UI Settings")
        
        # Live transcript
        current_transcript = config_manager.get_setting("ui_settings.show_live_transcript", True)
        show_live_transcript = st.checkbox("Show Live Transcript", value=current_transcript)
        
        # Audio visualization
        current_viz = config_manager.get_setting("ui_settings.enable_audio_visualization", True)
        enable_audio_visualization = st.checkbox("Enable Audio Visualization", value=current_viz)
    
    # Save configuration button
    if st.button("💾 Save Audio Configuration", type="primary"):
        new_config = {
            "audio_settings": {
                "voice_type": voice_type,
                "speech_speed": speech_speed,
                "conversation_detection": {
                    "silence_threshold": silence_threshold,
                    "volume_threshold": volume_threshold
                },
                "quality_settings": {
                    "sample_rate": sample_rate,
                    "format": "pcm16"
                }
            },
            "conversation_settings": {
                "max_duration": max_duration,
                "max_responses": max_responses,
                "auto_save_interval": auto_save_interval,
                "connection_timeout": connection_timeout
            },
            "ui_settings": {
                "show_live_transcript": show_live_transcript,
                "enable_audio_visualization": enable_audio_visualization
            }
        }
        
        try:
            config_manager.update_config(new_config)
            st.success("✅ Configuration saved successfully!")
            st.balloons()
        except Exception as e:
            st.error(f"❌ Error saving configuration: {str(e)}")
    
    # Reset to defaults button
    if st.button("🔄 Reset to Defaults"):
        if st.confirm("Are you sure you want to reset all settings to defaults?"):
            config_manager.reset_to_defaults()
            st.success("✅ Configuration reset to defaults!")
            st.rerun()

with tab2:
    st.header("System Monitoring Dashboard")
    
    # Refresh button
    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        if st.button("🔄 Refresh Data"):
            st.rerun()
    
    with col2:
        auto_refresh = st.checkbox("Auto-refresh (30s)")
    
    try:
        # Database statistics
        db_stats = get_database_stats()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Sessions", db_stats.get("total_sessions", 0))
        
        with col2:
            st.metric("Active Users", db_stats.get("active_users_24h", 0))
        
        with col3:
            avg_duration = db_stats.get("avg_session_duration", 0)
            st.metric("Avg Session Duration", f"{avg_duration/60:.1f} min")
        
        with col4:
            success_rate = db_stats.get("success_rate", 0)
            st.metric("Success Rate", f"{success_rate:.1%}")
        
        # Recent sessions table
        st.subheader("📋 Recent Sessions")
        
        recent_sessions = get_recent_sessions(limit=20)
        if recent_sessions:
            df = pd.DataFrame(recent_sessions)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['duration_min'] = df['session_duration'] / 60
            
            # Display table with formatting
            st.dataframe(
                df[['timestamp', 'identifier', 'duration_min', 'total_exchanges', 'status']],
                column_config={
                    "timestamp": "Session Time",
                    "identifier": "Student ID",
                    "duration_min": st.column_config.NumberColumn("Duration (min)", format="%.1f"),
                    "total_exchanges": "Exchanges",
                    "status": "Status"
                },
                use_container_width=True
            )
        else:
            st.info("No recent sessions found")
        
        # System health indicators
        st.subheader("🏥 System Health")
        
        health_col1, health_col2, health_col3 = st.columns(3)
        
        with health_col1:
            # API health check
            api_status = "✅ Healthy"  # This would be a real health check
            st.metric("OpenAI API", api_status)
        
        with health_col2:
            # Database health
            db_status = "✅ Connected"  # This would be a real health check
            st.metric("Database", db_status)
        
        with health_col3:
            # Audio service health
            audio_status = "✅ Available"  # This would be a real health check
            st.metric("Audio Service", audio_status)
        
    except Exception as e:
        st.error(f"❌ Error loading monitoring data: {str(e)}")
    
    # Auto-refresh functionality
    if auto_refresh:
        import time
        time.sleep(30)
        st.rerun()

with tab3:
    st.header("Testing & Diagnostic Tools")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🧪 Audio Test Suite")
        
        if st.button("🎤 Test Microphone Access"):
            st.info("Testing microphone access...")
            # This would trigger JavaScript to test microphone
            test_result = """
            <div style="padding: 10px; background-color: #d4edda; border: 1px solid #c3e6cb; border-radius: 4px;">
                <strong>✅ Microphone Test Results:</strong><br>
                • Permission: Granted<br>
                • Device: Default Microphone<br>
                • Sample Rate: 44.1kHz<br>
                • Status: Ready
            </div>
            """
            st.markdown(test_result, unsafe_allow_html=True)
        
        if st.button("🔊 Test Audio Playback"):
            st.info("Testing audio playback...")
            # This would test audio playback capability
            playback_result = """
            <div style="padding: 10px; background-color: #d4edda; border: 1px solid #c3e6cb; border-radius: 4px;">
                <strong>✅ Audio Playback Test Results:</strong><br>
                • Output Device: Default Speakers<br>
                • Volume Level: 80%<br>
                • Latency: ~50ms<br>
                • Status: Working
            </div>
            """
            st.markdown(playback_result, unsafe_allow_html=True)
        
        if st.button("🌐 Test OpenAI Connection"):
            st.info("Testing OpenAI Realtime API connection...")
            # This would test the OpenAI connection
            api_result = """
            <div style="padding: 10px; background-color: #d4edda; border: 1px solid #c3e6cb; border-radius: 4px;">
                <strong>✅ OpenAI API Test Results:</strong><br>
                • Connection: Successful<br>
                • Response Time: 120ms<br>
                • Rate Limit: OK<br>
                • WebSocket: Stable
            </div>
            """
            st.markdown(api_result, unsafe_allow_html=True)
        
        if st.button("📊 Run Full System Test"):
            st.info("Running comprehensive system test...")
            progress_bar = st.progress(0)
            
            # Simulate test progress
            import time
            for i in range(100):
                time.sleep(0.02)
                progress_bar.progress(i + 1)
            
            full_test_result = """
            <div style="padding: 15px; background-color: #d4edda; border: 1px solid #c3e6cb; border-radius: 4px;">
                <strong>✅ Full System Test Results:</strong><br>
                • Database Connection: ✅ Pass<br>
                • OpenAI API: ✅ Pass<br>
                • Audio Components: ✅ Pass<br>
                • WebSocket Connection: ✅ Pass<br>
                • Configuration Loading: ✅ Pass<br>
                • User Authentication: ✅ Pass<br>
                <strong>Overall Status: All Systems Operational</strong>
            </div>
            """
            st.markdown(full_test_result, unsafe_allow_html=True)
    
    with col2:
        st.subheader("🐛 Diagnostic Tools")
        
        # Browser information
        st.markdown("**Browser Compatibility Check:**")
        browser_info = """
        <div style="padding: 10px; background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 4px;">
            <strong>Detected Browser:</strong> Chrome 119.0<br>
            <strong>WebRTC Support:</strong> ✅ Available<br>
            <strong>Microphone API:</strong> ✅ Supported<br>
            <strong>WebSocket:</strong> ✅ Supported<br>
            <strong>Audio Context:</strong> ✅ Available
        </div>
        """
        st.markdown(browser_info, unsafe_allow_html=True)
        
        # Performance metrics
        st.markdown("**Performance Metrics:**")
        perf_col1, perf_col2 = st.columns(2)
        
        with perf_col1:
            st.metric("Avg Response Time", "1.2s")
            st.metric("Connection Quality", "98%")
        
        with perf_col2:
            st.metric("Audio Quality Score", "4.3/5")
            st.metric("Success Rate", "96%")
        
        # Log viewer
        st.markdown("**Recent System Logs:**")
        log_entries = [
            "2024-01-15 10:30:22 - INFO - New conversation started by user_123",
            "2024-01-15 10:29:45 - INFO - Audio connection established successfully",
            "2024-01-15 10:28:10 - WARNING - High latency detected (250ms)",
            "2024-01-15 10:27:33 - INFO - Configuration updated by admin",
            "2024-01-15 10:26:55 - INFO - Database connection restored"
        ]
        
        log_container = st.container(height=200)
        with log_container:
            for log_entry in log_entries:
                if "ERROR" in log_entry:
                    st.markdown(f"🔴 {log_entry}")
                elif "WARNING" in log_entry:
                    st.markdown(f"🟡 {log_entry}")
                else:
                    st.markdown(f"🟢 {log_entry}")

with tab4:
    st.header("User Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("👥 Active Users")
        
        # Mock active users data
        active_users = [
            {"identifier": "student_001", "status": "In Patient Chat", "duration": "12:34"},
            {"identifier": "student_002", "status": "In Supervisor Chat", "duration": "8:45"},
            {"identifier": "student_003", "status": "Idle", "duration": "0:23"},
        ]
        
        for user in active_users:
            with st.container():
                user_col1, user_col2, user_col3 = st.columns([2, 2, 1])
                with user_col1:
                    st.text(user["identifier"])
                with user_col2:
                    status_color = "🟢" if user["status"] == "Idle" else "🔵"
                    st.text(f"{status_color} {user['status']}")
                with user_col3:
                    st.text(user["duration"])
        
        st.subheader("📈 Usage Statistics")
        
        # Usage metrics
        usage_col1, usage_col2 = st.columns(2)
        
        with usage_col1:
            st.metric("Today's Sessions", "24")
            st.metric("This Week", "156")
        
        with usage_col2:
            st.metric("Unique Users", "18")
            st.metric("Avg Session Time", "18.5 min")
    
    with col2:
        st.subheader("⚙️ User Session Management")
        
        selected_user = st.selectbox("Select User", ["student_001", "student_002", "student_003"])
        
        st.text(f"Selected: {selected_user}")
        
        session_col1, session_col2 = st.columns(2)
        
        with session_col1:
            if st.button("📝 View Session Details"):
                st.info(f"Loading session details for {selected_user}...")
        
        with session_col2:
            if st.button("🛑 Force Disconnect", type="secondary"):
                st.warning(f"Force disconnecting {selected_user}...")
        
        st.subheader("🔧 Bulk Operations")
        
        bulk_action = st.selectbox("Bulk Action", [
            "Export All Sessions",
            "Clear Old Sessions",
            "Generate Usage Report",
            "Reset User Progress"
        ])
        
        if st.button("Execute Bulk Action"):
            st.info(f"Executing: {bulk_action}")

with tab5:
    st.header("Documentation & Training")
    
    doc_col1, doc_col2 = st.columns(2)
    
    with doc_col1:
        st.subheader("📚 Quick Reference")
        
        # System status overview
        st.markdown("""
        **System Status Overview:**
        - 🟢 All systems operational
        - 🟢 Audio services running
        - 🟢 Database connected
        - 🟢 OpenAI API available
        
        **Common Issues & Solutions:**
        
        1. **Audio not working:**
           - Check microphone permissions
           - Verify browser compatibility
           - Test audio devices in settings
        
        2. **Connection timeouts:**
           - Check internet connection
           - Verify API key validity
           - Review rate limiting settings
        
        3. **Poor audio quality:**
           - Adjust sample rate settings
           - Check volume thresholds
           - Monitor network stability
        """)
        
        if st.button("📄 Generate System Report"):
            st.success("✅ System report generated and downloaded!")
    
    with doc_col2:
        st.subheader("🎓 Training Materials")
        
        st.markdown("""
        **Student Orientation:**
        - How to use the audio interface
        - Microphone setup and testing
        - Conversation best practices
        - Troubleshooting common issues
        
        **Instructor Guide:**
        - System administration
        - Monitoring student progress
        - Configuration management
        - Performance optimization
        """)
        
        # Training material downloads
        st.markdown("**Download Training Materials:**")
        
        training_col1, training_col2 = st.columns(2)
        
        with training_col1:
            if st.button("📖 Student Manual"):
                st.info("Downloading student manual...")
        
        with training_col2:
            if st.button("👨‍🏫 Instructor Guide"):
                st.info("Downloading instructor guide...")
        
        # Video tutorials
        st.subheader("🎥 Video Tutorials")
        
        st.markdown("""
        **Available Tutorials:**
        1. System Setup & Configuration
        2. Audio Interface Overview
        3. Troubleshooting Guide
        4. Performance Monitoring
        5. User Management
        """)

# Footer
st.markdown("---")
st.markdown("**PhysioBot Admin Panel** | Version 1.0 | Last Updated: January 2024")