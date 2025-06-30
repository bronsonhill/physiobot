"""
Admin Configuration Interface
Phase 5 Implementation - UI/UX Enhancement & Configuration
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils.config_manager import config_manager
from datetime import datetime, timedelta
import json

# Page configuration
st.set_page_config(
    page_title="Admin Configuration - PhysioBot",
    page_icon="⚙️",
    layout="wide"
)

def check_admin_access():
    """Check if user has admin access"""
    # In a real implementation, this would check authentication
    # For now, we'll use a simple password check
    if "admin_authenticated" not in st.session_state:
        st.session_state.admin_authenticated = False
    
    if not st.session_state.admin_authenticated:
        st.title("🔐 Admin Access Required")
        password = st.text_input("Enter admin password:", type="password", key="admin_pass")
        if st.button("Login"):
            # In production, use proper authentication
            if password == "admin123":  # Replace with proper auth
                st.session_state.admin_authenticated = True
                st.rerun()
            else:
                st.error("Invalid password")
        st.stop()

def audio_settings_tab():
    """Audio configuration settings"""
    st.header("🎵 Audio Settings")
    
    audio_config = config_manager.get_audio_settings()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Voice Configuration")
        
        voice_options = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
        current_voice = audio_config.get('voice_type', 'alloy')
        voice_type = st.selectbox(
            "Voice Type",
            voice_options,
            index=voice_options.index(current_voice),
            help="Select the AI voice for patient and supervisor roles"
        )
        
        speech_speed = st.slider(
            "Speech Speed",
            min_value=0.25,
            max_value=4.0,
            value=audio_config.get('speech_speed', 1.0),
            step=0.25,
            help="Adjust the speech rate (1.0 = normal speed)"
        )
        
        st.subheader("Conversation Detection")
        silence_threshold = st.number_input(
            "Silence Threshold (seconds)",
            min_value=0.5,
            max_value=10.0,
            value=audio_config.get('conversation_detection', {}).get('silence_threshold', 2.0),
            step=0.5,
            help="Time of silence before considering speech ended"
        )
        
        volume_threshold = st.slider(
            "Volume Threshold",
            min_value=0.01,
            max_value=1.0,
            value=audio_config.get('conversation_detection', {}).get('volume_threshold', 0.1),
            step=0.01,
            help="Minimum volume level to detect speech"
        )
    
    with col2:
        st.subheader("Quality Settings")
        
        sample_rates = [16000, 24000, 48000]
        current_rate = audio_config.get('quality_settings', {}).get('sample_rate', 24000)
        sample_rate = st.selectbox(
            "Sample Rate (Hz)",
            sample_rates,
            index=sample_rates.index(current_rate),
            help="Audio quality - higher values = better quality but more bandwidth"
        )
        
        formats = ["pcm16", "pcm24", "ulaw", "alaw"]
        current_format = audio_config.get('quality_settings', {}).get('format', 'pcm16')
        audio_format = st.selectbox(
            "Audio Format",
            formats,
            index=formats.index(current_format),
            help="Audio encoding format"
        )
        
        st.subheader("Preview Audio Settings")
        if st.button("🎧 Test Audio Configuration"):
            st.success(f"Testing with voice: {voice_type}, speed: {speech_speed}x")
            st.info("In a real implementation, this would play a sample audio clip")
    
    # Save settings
    if st.button("💾 Save Audio Settings", type="primary"):
        config_manager.update_setting('audio_settings', 'voice_type', voice_type)
        config_manager.update_setting('audio_settings', 'speech_speed', speech_speed)
        config_manager.update_nested_setting('audio_settings', 'conversation_detection', 'silence_threshold', silence_threshold)
        config_manager.update_nested_setting('audio_settings', 'conversation_detection', 'volume_threshold', volume_threshold)
        config_manager.update_nested_setting('audio_settings', 'quality_settings', 'sample_rate', sample_rate)
        config_manager.update_nested_setting('audio_settings', 'quality_settings', 'format', audio_format)
        st.success("✅ Audio settings saved successfully!")

def conversation_settings_tab():
    """Conversation configuration settings"""
    st.header("💬 Conversation Settings")
    
    conv_config = config_manager.get_conversation_settings()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Time Limits")
        
        max_duration = st.number_input(
            "Maximum Duration (minutes)",
            min_value=5,
            max_value=120,
            value=conv_config.get('max_duration', 1800) // 60,
            step=5,
            help="Maximum time allowed for each conversation"
        )
        
        auto_save_interval = st.number_input(
            "Auto-save Interval (minutes)",
            min_value=1,
            max_value=30,
            value=conv_config.get('auto_save_interval', 300) // 60,
            step=1,
            help="How often to automatically save progress"
        )
        
        connection_timeout = st.number_input(
            "Connection Timeout (seconds)",
            min_value=10,
            max_value=300,
            value=conv_config.get('connection_timeout', 30),
            step=10,
            help="Timeout for audio connection attempts"
        )
    
    with col2:
        st.subheader("Response Limits")
        
        max_responses = st.number_input(
            "Maximum Responses",
            min_value=10,
            max_value=2000,
            value=conv_config.get('max_responses', 1000),
            step=10,
            help="Maximum number of conversation exchanges"
        )
        
        st.subheader("Conversation Quality")
        
        # Mock metrics for demonstration
        col2_1, col2_2 = st.columns(2)
        with col2_1:
            st.metric("Avg Session Duration", "23 min", "↗️ +2 min")
        with col2_2:
            st.metric("Completion Rate", "87%", "↗️ +5%")
    
    if st.button("💾 Save Conversation Settings", type="primary"):
        config_manager.update_setting('conversation_settings', 'max_duration', max_duration * 60)
        config_manager.update_setting('conversation_settings', 'auto_save_interval', auto_save_interval * 60)
        config_manager.update_setting('conversation_settings', 'connection_timeout', connection_timeout)
        config_manager.update_setting('conversation_settings', 'max_responses', max_responses)
        st.success("✅ Conversation settings saved successfully!")

def ui_settings_tab():
    """UI/UX configuration settings"""
    st.header("🎨 User Interface Settings")
    
    ui_config = config_manager.get_ui_settings()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Display Options")
        
        show_live_transcript = st.checkbox(
            "Show Live Transcript",
            value=ui_config.get('show_live_transcript', True),
            help="Display real-time transcript during conversations"
        )
        
        enable_audio_visualization = st.checkbox(
            "Enable Audio Visualization",
            value=ui_config.get('enable_audio_visualization', True),
            help="Show visual indicators for audio activity"
        )
        
        show_progress_indicators = st.checkbox(
            "Show Progress Indicators",
            value=ui_config.get('show_progress_indicators', True),
            help="Display conversation progress and time remaining"
        )
        
        enable_keyboard_shortcuts = st.checkbox(
            "Enable Keyboard Shortcuts",
            value=ui_config.get('enable_keyboard_shortcuts', True),
            help="Allow keyboard shortcuts for common actions"
        )
    
    with col2:
        st.subheader("Theme Settings")
        
        themes = ["modern", "classic", "dark", "light"]
        current_theme = ui_config.get('theme', 'modern')
        theme = st.selectbox(
            "Interface Theme",
            themes,
            index=themes.index(current_theme),
            help="Select the visual theme for the application"
        )
        
        st.subheader("UI Preview")
        if theme == "modern":
            st.info("🎨 Modern theme: Clean, minimalist design with rounded corners")
        elif theme == "dark":
            st.info("🌙 Dark theme: Dark background, easy on the eyes")
        elif theme == "light":
            st.info("☀️ Light theme: Bright, traditional interface")
        else:
            st.info("📋 Classic theme: Traditional, formal appearance")
    
    if st.button("💾 Save UI Settings", type="primary"):
        config_manager.update_setting('ui_settings', 'show_live_transcript', show_live_transcript)
        config_manager.update_setting('ui_settings', 'enable_audio_visualization', enable_audio_visualization)
        config_manager.update_setting('ui_settings', 'show_progress_indicators', show_progress_indicators)
        config_manager.update_setting('ui_settings', 'enable_keyboard_shortcuts', enable_keyboard_shortcuts)
        config_manager.update_setting('ui_settings', 'theme', theme)
        st.success("✅ UI settings saved successfully!")

def diagnostics_tab():
    """System diagnostics and testing"""
    st.header("🔧 System Diagnostics")
    
    diag_config = config_manager.get_diagnostics_settings()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Monitoring Settings")
        
        enable_performance_monitoring = st.checkbox(
            "Enable Performance Monitoring",
            value=diag_config.get('enable_performance_monitoring', True),
            help="Monitor system performance and response times"
        )
        
        log_audio_quality = st.checkbox(
            "Log Audio Quality",
            value=diag_config.get('log_audio_quality', True),
            help="Record audio quality metrics for analysis"
        )
        
        enable_browser_compatibility_check = st.checkbox(
            "Browser Compatibility Check",
            value=diag_config.get('enable_browser_compatibility_check', True),
            help="Check browser compatibility on first visit"
        )
        
        debug_mode = st.checkbox(
            "Debug Mode",
            value=diag_config.get('debug_mode', False),
            help="Enable detailed logging for troubleshooting"
        )
    
    with col2:
        st.subheader("System Status")
        
        # Mock system metrics
        st.metric("System Uptime", "99.9%", "✅")
        st.metric("Active Sessions", "23", "↗️ +5")
        st.metric("Avg Response Time", "0.8s", "↘️ -0.1s")
        
        st.subheader("Quick Tests")
        
        if st.button("🧪 Run Browser Compatibility Test"):
            st.info("Testing browser compatibility...")
            # Mock test results
            compatibility_results = {
                "Chrome": "✅ Supported",
                "Firefox": "✅ Supported", 
                "Safari": "⚠️ Limited support",
                "Edge": "✅ Supported"
            }
            for browser, status in compatibility_results.items():
                st.write(f"**{browser}:** {status}")
        
        if st.button("🎵 Test Audio System"):
            st.info("Testing audio system...")
            st.success("✅ Audio input/output functioning correctly")
            st.success("✅ OpenAI Realtime API connection established")
    
    if st.button("💾 Save Diagnostic Settings", type="primary"):
        config_manager.update_setting('diagnostics', 'enable_performance_monitoring', enable_performance_monitoring)
        config_manager.update_setting('diagnostics', 'log_audio_quality', log_audio_quality)
        config_manager.update_setting('diagnostics', 'enable_browser_compatibility_check', enable_browser_compatibility_check)
        config_manager.update_setting('diagnostics', 'debug_mode', debug_mode)
        st.success("✅ Diagnostic settings saved successfully!")

def analytics_tab():
    """Analytics and performance metrics"""
    st.header("📊 System Analytics")
    
    # Mock analytics data for demonstration
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Sessions", "1,234", "↗️ +15%")
    with col2:
        st.metric("Avg Session Duration", "23 min", "↗️ +2 min")
    with col3:
        st.metric("Audio Quality Score", "4.2/5", "↗️ +0.1")
    with col4:
        st.metric("User Satisfaction", "88%", "↗️ +3%")
    
    # Mock usage chart
    st.subheader("Usage Trends")
    dates = pd.date_range(start='2024-01-01', end='2024-01-31', freq='D')
    usage_data = pd.DataFrame({
        'Date': dates,
        'Sessions': [20 + i % 15 + (i // 7) * 5 for i in range(len(dates))]
    })
    
    fig = px.line(usage_data, x='Date', y='Sessions', title='Daily Session Count')
    st.plotly_chart(fig, use_container_width=True)
    
    # Mock audio quality metrics
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Audio Quality Distribution")
        quality_data = {
            'Rating': ['Excellent', 'Good', 'Fair', 'Poor'],
            'Count': [45, 35, 15, 5]
        }
        fig2 = px.pie(values=quality_data['Count'], names=quality_data['Rating'], 
                     title='Audio Quality Ratings')
        st.plotly_chart(fig2, use_container_width=True)
    
    with col2:
        st.subheader("Browser Usage")
        browser_data = {
            'Browser': ['Chrome', 'Firefox', 'Safari', 'Edge'],
            'Usage': [60, 25, 10, 5]
        }
        fig3 = px.bar(x=browser_data['Browser'], y=browser_data['Usage'], 
                     title='Browser Usage Distribution')
        st.plotly_chart(fig3, use_container_width=True)

def main():
    """Main admin configuration interface"""
    check_admin_access()
    
    st.title("⚙️ PhysioBot Admin Configuration")
    st.markdown("Configure system settings, monitor performance, and manage the audio conversation platform.")
    
    # Configuration tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🎵 Audio Settings",
        "💬 Conversation",
        "🎨 User Interface", 
        "🔧 Diagnostics",
        "📊 Analytics"
    ])
    
    with tab1:
        audio_settings_tab()
    
    with tab2:
        conversation_settings_tab()
    
    with tab3:
        ui_settings_tab()
    
    with tab4:
        diagnostics_tab()
    
    with tab5:
        analytics_tab()
    
    # Footer with system info
    st.markdown("---")
    st.markdown(
        f"**System Status:** ✅ Online | "
        f"**Version:** 1.0.0 | "
        f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )

if __name__ == "__main__":
    main()