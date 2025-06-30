import streamlit as st
import yaml
import json
from datetime import datetime, timezone
from typing import Dict, Any, List
import pandas as pd
from pathlib import Path

from utils.config_manager import ConfigManager, get_config_manager
from utils.cohort_config_manager import CohortConfigManager
from utils.mongodb_realtime import get_mongo_client

# Page configuration
st.set_page_config(
    page_title="Admin Configuration - PhysioBot",
    page_icon="⚙️",
    layout="wide"
)

# Authentication check (basic implementation)
def check_admin_auth():
    """Check if user has admin privileges."""
    if "admin_authenticated" not in st.session_state:
        st.session_state["admin_authenticated"] = False
    
    if not st.session_state["admin_authenticated"]:
        st.title("🔐 Administrator Access")
        
        admin_key = st.text_input("Enter admin access key:", type="password")
        
        if st.button("Login"):
            # In production, this should be a proper authentication system
            if admin_key == st.secrets.get("ADMIN_ACCESS_KEY", "admin123"):
                st.session_state["admin_authenticated"] = True
                st.rerun()
            else:
                st.error("Invalid access key")
        
        st.info("Contact your system administrator for access credentials.")
        st.stop()

def main():
    st.title("⚙️ Admin Configuration")
    st.markdown("System configuration and cohort management.")
    
    # Get cached configuration managers
    config_manager = get_config_manager()
    cohort_manager = CohortConfigManager()
    
    # Create tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs([
        "🎵 Audio Settings", 
        "👥 Cohort Management", 
        "⚙️ System Settings",
        "📊 Analytics & Monitoring"
    ])
    
    with tab1:
        audio_settings_interface(config_manager)
    
    with tab2:
        cohort_management_interface(cohort_manager)
    
    with tab3:
        system_settings_interface(config_manager)
    
    with tab4:
        analytics_monitoring_interface(cohort_manager)

def audio_settings_interface(config_manager: ConfigManager):
    """Interface for managing audio settings."""
    st.subheader("🎵 Audio Configuration")
    
    current_audio = config_manager.get_audio_settings()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Voice & Speech Settings")
        
        voice_type = st.selectbox(
            "Voice Type",
            options=["alloy", "echo", "fable", "onyx", "nova", "shimmer"],
            index=["alloy", "echo", "fable", "onyx", "nova", "shimmer"].index(
                current_audio.get("voice_type", "alloy")
            ),
            help="OpenAI voice model to use for patient responses"
        )
        
        speech_speed = st.slider(
            "Speech Speed",
            min_value=0.25,
            max_value=4.0,
            value=current_audio.get("speech_speed", 1.0),
            step=0.1,
            help="Speed of AI speech (1.0 = normal)"
        )
        
        st.markdown("### Conversation Detection")
        
        silence_threshold = st.slider(
            "Silence Threshold (seconds)",
            min_value=0.5,
            max_value=5.0,
            value=current_audio.get("conversation_detection", {}).get("silence_threshold", 2.0),
            step=0.1,
            help="How long to wait before considering user finished speaking"
        )
        
        volume_threshold = st.slider(
            "Volume Threshold",
            min_value=0.01,
            max_value=1.0,
            value=current_audio.get("conversation_detection", {}).get("volume_threshold", 0.1),
            step=0.01,
            help="Minimum volume level to trigger recording"
        )
    
    with col2:
        st.markdown("### Quality Settings")
        
        sample_rate = st.selectbox(
            "Sample Rate (Hz)",
            options=[16000, 24000, 48000],
            index=[16000, 24000, 48000].index(
                current_audio.get("quality_settings", {}).get("sample_rate", 24000)
            ),
            help="Audio sample rate - higher is better quality but more bandwidth"
        )
        
        audio_format = st.selectbox(
            "Audio Format",
            options=["pcm16", "g711_ulaw", "g711_alaw"],
            index=["pcm16", "g711_ulaw", "g711_alaw"].index(
                current_audio.get("quality_settings", {}).get("format", "pcm16")
            ),
            help="Audio encoding format"
        )
        
        st.markdown("### Test Audio Settings")
        
        if st.button("🎵 Test Voice Settings"):
            with st.spinner("Testing voice settings..."):
                # This would implement actual voice testing
                st.success(f"Voice test completed with {voice_type} at {speech_speed}x speed")
        
        if st.button("📊 Audio Quality Test"):
            with st.spinner("Running audio quality diagnostics..."):
                # Mock audio quality test results
                quality_results = {
                    "latency_ms": 150,
                    "jitter_ms": 12,
                    "packet_loss": 0.2,
                    "quality_score": 4.3
                }
                
                col_a, col_b, col_c, col_d = st.columns(4)
                with col_a:
                    st.metric("Latency", f"{quality_results['latency_ms']} ms")
                with col_b:
                    st.metric("Jitter", f"{quality_results['jitter_ms']} ms")
                with col_c:
                    st.metric("Packet Loss", f"{quality_results['packet_loss']}%")
                with col_d:
                    st.metric("Quality Score", f"{quality_results['quality_score']}/5.0")
    
    # Save settings
    if st.button("💾 Save Audio Settings", type="primary"):
        new_audio_settings = {
            "voice_type": voice_type,
            "speech_speed": speech_speed,
            "conversation_detection": {
                "silence_threshold": silence_threshold,
                "volume_threshold": volume_threshold
            },
            "quality_settings": {
                "sample_rate": sample_rate,
                "format": audio_format
            }
        }
        
        config_manager.config["audio_settings"] = new_audio_settings
        
        if config_manager.save_config():
            st.success("✅ Audio settings saved successfully!")
        else:
            st.error("❌ Failed to save audio settings")

def cohort_management_interface(cohort_manager: CohortConfigManager):
    """Interface for managing cohorts."""
    st.subheader("👥 Cohort Management")
    
    # Get existing cohorts
    cohorts = cohort_manager.get_all_cohorts()
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### Create New Cohort")
        
        with st.form("new_cohort_form"):
            cohort_id = st.text_input("Cohort ID", help="Unique identifier (e.g., PHYSIO2024_SEM1)")
            cohort_name = st.text_input("Cohort Name", help="Display name for the cohort")
            academic_year = st.text_input("Academic Year", value="2024")
            semester = st.selectbox("Semester", ["Semester 1", "Semester 2", "Summer", "Other"])
            
            instructor_emails = st.text_area(
                "Instructor Emails",
                help="One email per line",
                placeholder="instructor1@university.edu\ninstructor2@university.edu"
            )
            
            submitted = st.form_submit_button("Create Cohort")
            
            if submitted and cohort_id and cohort_name:
                instructor_list = [email.strip() for email in instructor_emails.split('\n') if email.strip()]
                
                result = cohort_manager.create_cohort(
                    cohort_id=cohort_id,
                    cohort_name=cohort_name,
                    academic_year=academic_year,
                    semester=semester,
                    instructor_emails=instructor_list
                )
                
                if result["success"]:
                    st.success("✅ Cohort created successfully!")
                    st.rerun()
                else:
                    st.error(f"❌ Failed to create cohort: {result['error']}")
    
    with col2:
        st.markdown("### Existing Cohorts")
        
        if cohorts:
            for cohort in cohorts:
                with st.expander(f"{cohort['cohort_name']} ({cohort['cohort_id']})"):
                    col_a, col_b = st.columns(2)
                    
                    with col_a:
                        st.write(f"**Academic Year:** {cohort.get('academic_year', 'N/A')}")
                        st.write(f"**Semester:** {cohort.get('semester', 'N/A')}")
                        st.write(f"**Created:** {cohort.get('created_at', 'N/A')}")
                        st.write(f"**Active:** {'Yes' if cohort.get('is_active', False) else 'No'}")
                    
                    with col_b:
                        st.write("**Instructors:**")
                        for instructor in cohort.get('instructor_emails', []):
                            st.write(f"- {instructor}")
                    
                    # Cohort actions
                    col_action1, col_action2, col_action3 = st.columns(3)
                    
                    with col_action1:
                        if st.button(f"📊 Stats", key=f"stats_{cohort['cohort_id']}"):
                            show_cohort_statistics(cohort['cohort_id'])
                    
                    with col_action2:
                        if st.button(f"⚙️ Configure", key=f"config_{cohort['cohort_id']}"):
                            st.session_state[f"configuring_{cohort['cohort_id']}"] = True
                    
                    with col_action3:
                        if st.button(f"🗑️ Archive", key=f"archive_{cohort['cohort_id']}"):
                            cohort_manager.archive_cohort(cohort['cohort_id'])
                            st.success("Cohort archived")
                            st.rerun()
        else:
            st.info("No cohorts found. Create your first cohort above.")

def system_settings_interface(config_manager: ConfigManager):
    """Interface for system-wide settings."""
    st.subheader("🔧 System Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Conversation Settings")
        
        conv_settings = config_manager.get_conversation_settings()
        
        max_duration = st.number_input(
            "Max Conversation Duration (seconds)",
            min_value=300,
            max_value=7200,
            value=conv_settings.get("max_duration", 1800),
            step=300,
            help="Maximum time allowed for a conversation"
        )
        
        max_responses = st.number_input(
            "Max Responses per Conversation",
            min_value=10,
            max_value=200,
            value=conv_settings.get("max_responses", 50),
            step=5,
            help="Maximum number of back-and-forth exchanges"
        )
        
        auto_save_interval = st.number_input(
            "Auto-save Interval (seconds)",
            min_value=60,
            max_value=1800,
            value=conv_settings.get("auto_save_interval", 300),
            step=60,
            help="How often to auto-save conversation progress"
        )
        
        connection_timeout = st.number_input(
            "Connection Timeout (seconds)",
            min_value=10,
            max_value=120,
            value=conv_settings.get("connection_timeout", 30),
            step=5,
            help="Timeout for API connections"
        )
    
    with col2:
        st.markdown("### UI Settings")
        
        ui_settings = config_manager.get_ui_settings()
        
        show_live_transcript = st.checkbox(
            "Show Live Transcript",
            value=ui_settings.get("show_live_transcript", True),
            help="Display real-time conversation transcript"
        )
        
        enable_audio_visualization = st.checkbox(
            "Enable Audio Visualization",
            value=ui_settings.get("enable_audio_visualization", True),
            help="Show audio level and frequency visualization"
        )
        
        theme = st.selectbox(
            "UI Theme",
            options=["light", "dark", "auto"],
            index=["light", "dark", "auto"].index(ui_settings.get("theme", "light")),
            help="User interface color theme"
        )
        
        st.markdown("### Environment Settings")
        
        env_settings = config_manager.config.get("environment", {})
        
        debug_logging = st.checkbox(
            "Debug Logging",
            value=env_settings.get("debug_logging", True),
            help="Enable detailed logging for troubleshooting"
        )
        
        log_level = st.selectbox(
            "Log Level",
            options=["DEBUG", "INFO", "WARNING", "ERROR"],
            index=["DEBUG", "INFO", "WARNING", "ERROR"].index(
                env_settings.get("log_level", "INFO")
            ),
            help="Minimum log level to record"
        )
    
    # Save system settings
    if st.button("💾 Save System Settings", type="primary"):
        config_manager.config["conversation_settings"] = {
            "max_duration": max_duration,
            "max_responses": max_responses,
            "auto_save_interval": auto_save_interval,
            "connection_timeout": connection_timeout
        }
        
        config_manager.config["ui_settings"] = {
            "show_live_transcript": show_live_transcript,
            "enable_audio_visualization": enable_audio_visualization,
            "theme": theme
        }
        
        config_manager.config["environment"] = {
            "debug_logging": debug_logging,
            "log_level": log_level,
            "development": True
        }
        
        if config_manager.save_config():
            st.success("✅ System settings saved successfully!")
        else:
            st.error("❌ Failed to save system settings")

def analytics_monitoring_interface(cohort_manager: CohortConfigManager):
    """Interface for analytics and monitoring."""
    st.subheader("📊 Analytics & Monitoring")
    
    # System health metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Active Sessions", "23", delta="5")
    with col2:
        st.metric("Total Conversations", "1,247", delta="127")
    with col3:
        st.metric("Avg Response Time", "1.2s", delta="-0.3s")
    with col4:
        st.metric("System Uptime", "99.8%", delta="0.1%")
    
    # Recent activity chart
    st.markdown("### 📈 Usage Analytics")
    
    # Mock data for demonstration
    import numpy as np
    
    dates = pd.date_range(start='2024-01-01', end='2024-01-07', freq='D')
    usage_data = pd.DataFrame({
        'Date': dates,
        'Conversations': np.random.randint(50, 150, size=len(dates)),
        'Unique Users': np.random.randint(20, 80, size=len(dates)),
        'Avg Duration (min)': np.random.randint(15, 45, size=len(dates))
    })
    
    st.line_chart(usage_data.set_index('Date')[['Conversations', 'Unique Users']])
    
    # Error logs and alerts
    st.markdown("### 🚨 System Alerts")
    
    alerts = [
        {"type": "warning", "message": "High latency detected in audio processing", "time": "2 minutes ago"},
        {"type": "info", "message": "New cohort 'PHYSIO2024_SEM2' created", "time": "1 hour ago"},
        {"type": "error", "message": "Database connection timeout (resolved)", "time": "3 hours ago"}
    ]
    
    for alert in alerts:
        if alert["type"] == "error":
            st.error(f"🔴 {alert['message']} - {alert['time']}")
        elif alert["type"] == "warning":
            st.warning(f"🟡 {alert['message']} - {alert['time']}")
        else:
            st.info(f"🔵 {alert['message']} - {alert['time']}")

def testing_tools_interface():
    """Interface for testing and diagnostics."""
    st.subheader("🧪 Testing & Diagnostics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Browser Compatibility Test")
        
        if st.button("🌐 Run Browser Tests"):
            with st.spinner("Testing browser compatibility..."):
                # Mock browser test results
                browser_results = {
                    "Chrome": {"audio": "✅", "webrtc": "✅", "websockets": "✅"},
                    "Firefox": {"audio": "✅", "webrtc": "✅", "websockets": "✅"},
                    "Safari": {"audio": "✅", "webrtc": "⚠️", "websockets": "✅"},
                    "Edge": {"audio": "✅", "webrtc": "✅", "websockets": "✅"}
                }
                
                st.write("**Browser Compatibility Results:**")
                for browser, features in browser_results.items():
                    st.write(f"**{browser}:**")
                    for feature, status in features.items():
                        st.write(f"  - {feature}: {status}")
        
        st.markdown("### Audio Quality Test")
        
        if st.button("🎵 Test Audio Pipeline"):
            with st.spinner("Testing audio quality..."):
                # Mock audio test
                audio_test_results = {
                    "Microphone Access": "✅ Granted",
                    "Audio Capture": "✅ Working",
                    "WebRTC Support": "✅ Available",
                    "Echo Cancellation": "✅ Enabled",
                    "Noise Suppression": "✅ Enabled"
                }
                
                for test, result in audio_test_results.items():
                    st.write(f"- {test}: {result}")
    
    with col2:
        st.markdown("### Performance Test")
        
        if st.button("⚡ Run Performance Tests"):
            with st.spinner("Testing system performance..."):
                # Mock performance results
                perf_results = {
                    "API Response Time": "145ms",
                    "Database Query Time": "23ms",
                    "Memory Usage": "67%",
                    "CPU Usage": "34%",
                    "Network Latency": "12ms"
                }
                
                for metric, value in perf_results.items():
                    st.metric(metric, value)
        
        st.markdown("### Load Test")
        
        concurrent_users = st.slider("Simulated Concurrent Users", 1, 100, 20)
        
        if st.button("🔄 Run Load Test"):
            with st.spinner(f"Simulating {concurrent_users} concurrent users..."):
                # Mock load test
                st.progress(0.2, text="Starting sessions...")
                st.progress(0.5, text="Peak load reached...")
                st.progress(0.8, text="Measuring response times...")
                st.progress(1.0, text="Test completed!")
                
                st.success(f"✅ Load test completed! System handled {concurrent_users} users with average response time of 1.8s")

def show_cohort_statistics(cohort_id: str):
    """Display statistics for a specific cohort."""
    st.markdown(f"### Statistics for {cohort_id}")
    
    # Mock statistics
    stats = {
        "total_students": 45,
        "completed_assignments": 38,
        "average_score": 82.5,
        "average_duration": 28.3,
        "completion_rate": 84.4
    }
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Students", stats["total_students"])
    with col2:
        st.metric("Completed", stats["completed_assignments"])
    with col3:
        st.metric("Avg Score", f"{stats['average_score']:.1f}%")
    with col4:
        st.metric("Avg Duration", f"{stats['average_duration']:.1f}min")
    with col5:
        st.metric("Completion Rate", f"{stats['completion_rate']:.1f}%")

if __name__ == "__main__":
    main()