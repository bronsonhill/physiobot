import streamlit as st
import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import time
import numpy as np

from Home import setup
from utils.conversation_handler import ConversationHandler, ConversationState
from utils.config_manager import ConfigManager
from utils.mongodb_realtime import log_audio_transcript, get_conversation_history
from utils.audio_manager import AudioManager
from utils.audio_analysis import AudioConversationAnalyzer, create_conversation_analysis_report

# Page configuration
st.set_page_config(
    page_title="Supervisor Conversation - PhysioBot",
    page_icon="👨‍🏫",
    layout="wide"
)

# Custom CSS for enhanced UI
st.markdown("""
<style>
.supervisor-header {
    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
    color: white;
    padding: 20px;
    border-radius: 10px;
    margin-bottom: 20px;
}

.audio-analysis-card {
    background: #f8f9fa;
    padding: 15px;
    border-radius: 8px;
    border-left: 4px solid #007bff;
    margin: 10px 0;
}

.feedback-section {
    background: #e8f4fd;
    padding: 20px;
    border-radius: 10px;
    border: 1px solid #bee5eb;
    margin: 15px 0;
}

.patient-context-card {
    background: #fff3cd;
    padding: 15px;
    border-radius: 8px;
    border-left: 4px solid #ffc107;
    margin: 10px 0;
}

.quality-metric {
    display: inline-block;
    background: #f1f3f4;
    padding: 8px 12px;
    border-radius: 20px;
    margin: 5px;
    border: 1px solid #dadce0;
}

.conversation-stats {
    background: #f8f9fa;
    padding: 15px;
    border-radius: 8px;
    margin: 10px 0;
}
</style>
""", unsafe_allow_html=True)

MAXIMUM_RESPONSES = 50

# Initialize components
@st.cache_resource
def initialize_components():
    """Initialize conversation handler and configuration."""
    config_manager = ConfigManager()
    config = config_manager.config
    
    # Get OpenAI API key
    api_key = st.secrets.get("OPENAI_API_KEY")
    if not api_key:
        st.error("OpenAI API key not found in secrets")
        st.stop()
    
    return config, api_key

def get_patient_conversation_analysis() -> Dict[str, Any]:
    """Analyze the patient conversation for supervisor feedback using advanced audio analysis."""
    if not st.session_state.get("p_chat_history"):
        return {}
    
    try:
        # Convert chat history to transcript segments format
        messages = st.session_state["p_chat_history"]
        transcript_segments = []
        
        for i, message in enumerate(messages):
            segment = {
                'timestamp': datetime.now() - timedelta(minutes=(len(messages) - i)),
                'speaker': 'user' if message['role'] == 'user' else 'assistant',
                'text': message['content'],
                'input_type': 'audio'
            }
            transcript_segments.append(segment)
        
        # Get conversation duration
        duration_seconds = st.session_state.get("p_conversation_duration", 0)
        if duration_seconds == 0:
            # Estimate duration based on content (rough approximation)
            total_words = sum(len(m["content"].split()) for m in messages)
            duration_seconds = (total_words / 150) * 60  # ~150 words per minute
        
        # Initialize analyzer and perform analysis
        analyzer = AudioConversationAnalyzer()
        analysis = analyzer.analyze_conversation(
            transcript_segments,
            duration_seconds
        )
        
        # Convert to legacy format for backward compatibility
        basic_metrics = analysis.get('basic_metrics', {})
        question_analysis = analysis.get('question_analysis', {})
        
        legacy_format = {
            "total_exchanges": basic_metrics.get('total_exchanges', 0),
            "student_words": basic_metrics.get('student_words', 0),
            "patient_words": basic_metrics.get('patient_words', 0),
            "word_ratio": basic_metrics.get('word_ratio', 0),
            "open_ended_questions": question_analysis.get('open_ended_questions', 0),
            "closed_questions": question_analysis.get('closed_ended_questions', 0),
            "question_ratio": question_analysis.get('question_ratio', 0),
            "duration_minutes": duration_seconds / 60,
            "exchanges_per_minute": basic_metrics.get('exchanges_per_minute', 0),
            "avg_student_response_length": basic_metrics.get('avg_student_response_length', 0),
            "conversation_balance": analysis.get('communication_patterns', {}).get('conversation_balance', 'unknown'),
            # Add advanced analysis data
            "advanced_analysis": analysis
        }
        
        return legacy_format
        
    except Exception as e:
        logger.error(f"Error in patient conversation analysis: {e}")
        # Fallback to basic analysis
        return get_basic_conversation_analysis()

def get_basic_conversation_analysis() -> Dict[str, Any]:
    """Fallback basic analysis when advanced analysis fails."""
    if not st.session_state.get("p_chat_history"):
        return {}
    
    messages = st.session_state["p_chat_history"]
    
    # Count exchanges
    student_messages = [m for m in messages if m["role"] == "user"]
    patient_messages = [m for m in messages if m["role"] == "assistant"]
    
    # Calculate word counts
    student_words = sum(len(m["content"].split()) for m in student_messages)
    patient_words = sum(len(m["content"].split()) for m in patient_messages)
    
    # Calculate conversation pace (assuming audio duration from session state)
    duration_minutes = st.session_state.get("p_conversation_duration", 0) / 60
    exchanges_per_minute = len(student_messages) / max(duration_minutes, 1)
    
    return {
        "total_exchanges": len(student_messages),
        "student_words": student_words,
        "patient_words": patient_words,
        "word_ratio": student_words / max(patient_words, 1),
        "open_ended_questions": 0,
        "closed_questions": 0,
        "question_ratio": 0,
        "duration_minutes": duration_minutes,
        "exchanges_per_minute": exchanges_per_minute,
        "avg_student_response_length": student_words / max(len(student_messages), 1),
        "conversation_balance": "balanced" if 0.3 <= (student_words / max(patient_words, 1)) <= 0.8 else "unbalanced"
    }

def format_patient_conversation_context() -> str:
    """Format patient conversation for supervisor context."""
    if not st.session_state.get("p_chat_history"):
        return "No patient conversation available."
    
    messages = st.session_state["p_chat_history"]
    formatted_messages = []
    
    for i, message in enumerate(messages, 1):
        role = "Student" if message["role"] == "user" else "Patient"
        formatted_messages.append(f"{i}. {role}: {message['content']}")
    
    return "\n".join(formatted_messages)

def create_enhanced_supervisor_prompt(patient_context: str, audio_analysis: Dict[str, Any]) -> str:
    """Create enhanced supervisor prompt with comprehensive audio analysis context."""
    
    # Load the audio-specific supervisor prompt
    try:
        with open('prompts/audio_supervisor_prompt.txt', 'r') as f:
            base_prompt = f.read()
    except FileNotFoundError:
        # Fallback to session state supervisor prompt
        base_prompt = st.session_state.get('supervisor_prompt', '')
    
    # Get advanced analysis data if available
    advanced_analysis = audio_analysis.get('advanced_analysis', {})
    
    if advanced_analysis:
        # Use comprehensive analysis data
        basic_metrics = advanced_analysis.get('basic_metrics', {})
        question_analysis = advanced_analysis.get('question_analysis', {})
        pace_analysis = advanced_analysis.get('pace_analysis', {})
        language_quality = advanced_analysis.get('language_quality', {})
        empathy_analysis = advanced_analysis.get('empathy_analysis', {})
        professional_analysis = advanced_analysis.get('professional_analysis', {})
        overall_assessment = advanced_analysis.get('overall_assessment', {})
        
        # Create detailed analysis report
        analysis_report = create_conversation_analysis_report(advanced_analysis)
        
        audio_context = f"""

## Comprehensive Audio Conversation Analysis

{analysis_report}

## Detailed Performance Metrics

**Communication Quality Scores:**
- Overall Communication Score: {overall_assessment.get('overall_score', 0):.1f}/100
- Assessment Level: {overall_assessment.get('assessment_level', 'Unknown')}

**Component Breakdown:**
- Question Quality: {overall_assessment.get('component_scores', {}).get('question_quality', 0):.1f}/100
- Pace & Timing: {overall_assessment.get('component_scores', {}).get('pace_quality', 0):.1f}/100
- Language Fluency: {overall_assessment.get('component_scores', {}).get('language_quality', 0):.1f}/100
- Empathy & Rapport: {overall_assessment.get('component_scores', {}).get('empathy_quality', 0):.1f}/100
- Professionalism: {overall_assessment.get('component_scores', {}).get('professional_quality', 0):.1f}/100

**Specific Audio Analysis Findings:**
- Average response time: {pace_analysis.get('average_response_time', 0):.1f} seconds
- Pace assessment: {pace_analysis.get('pace_assessment', 'Unknown')}
- Filler word usage: {language_quality.get('filler_percentage', 0):.1f}% of speech
- Language clarity: {language_quality.get('language_clarity', 'Unknown')}
- Active listening indicators: {empathy_analysis.get('active_listening_indicators', 0)}
- Empathy indicators: {empathy_analysis.get('empathy_indicators', 0)}
- Rapport assessment: {empathy_analysis.get('rapport_assessment', 'Unknown')}

**Key Strengths Identified:**
""" + "\n".join(f"- {strength}" for strength in overall_assessment.get('key_strengths', []))

        audio_context += f"""

**Priority Improvement Areas:**
""" + "\n".join(f"- {area}" for area in overall_assessment.get('improvement_areas', []))

    else:
        # Fallback to basic analysis
        audio_context = f"""

## Basic Audio Conversation Analysis

**Conversation Metrics:**
- Total exchanges: {audio_analysis.get('total_exchanges', 0)}
- Duration: {audio_analysis.get('duration_minutes', 0):.1f} minutes
- Exchanges per minute: {audio_analysis.get('exchanges_per_minute', 0):.1f}
- Student word count: {audio_analysis.get('student_words', 0)}
- Patient word count: {audio_analysis.get('patient_words', 0)}
- Average student response length: {audio_analysis.get('avg_student_response_length', 0):.1f} words

**Communication Patterns:**
- Open-ended questions: {audio_analysis.get('open_ended_questions', 0)}
- Closed questions: {audio_analysis.get('closed_questions', 0)}
- Question balance: {"Good balance of open-ended questions" if audio_analysis.get('question_ratio', 0) > 1 else "Consider using more open-ended questions"}
- Conversation balance: {audio_analysis.get('conversation_balance', 'unknown')}
"""
    
    audio_context += f"""

## Patient Conversation Transcript

{patient_context}

## Additional Context for Feedback

Please use the above detailed analysis to provide comprehensive feedback that addresses both clinical assessment skills and audio communication excellence. Focus on specific examples from the conversation and provide actionable recommendations for improvement.
"""
    
    return base_prompt + audio_context

def display_patient_conversation_summary():
    """Display summary of patient conversation with analysis."""
    st.markdown('<div class="patient-context-card">', unsafe_allow_html=True)
    st.markdown("### 📋 Patient Conversation Summary")
    
    if not st.session_state.get("p_chat_history"):
        st.warning("No patient conversation found. Please complete the patient conversation first.")
        return
    
    analysis = get_patient_conversation_analysis()
    
    # Display key metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Exchanges", analysis.get('total_exchanges', 0))
    with col2:
        st.metric("Duration", f"{analysis.get('duration_minutes', 0):.1f} min")
    with col3:
        st.metric("Open Questions", analysis.get('open_ended_questions', 0))
    with col4:
        st.metric("Conversation Balance", analysis.get('conversation_balance', 'unknown').title())
    
    # Advanced analysis metrics (if available)
    advanced_analysis = analysis.get('advanced_analysis', {})
    if advanced_analysis and 'overall_assessment' in advanced_analysis:
        st.markdown("---")
        st.markdown("### 🎯 Advanced Communication Analysis")
        
        overall = advanced_analysis.get('overall_assessment', {})
        
        # Overall score
        col1, col2 = st.columns(2)
        with col1:
            overall_score = overall.get('overall_score', 0)
            st.metric(
                "Overall Communication Score", 
                f"{overall_score:.1f}/100",
                help="Composite score based on question quality, pace, fluency, empathy, and professionalism"
            )
        with col2:
            assessment_level = overall.get('assessment_level', 'Unknown')
            level_color = {
                'Excellent': '🟢',
                'Good': '🟡', 
                'Satisfactory': '🟠',
                'Needs Improvement': '🔴'
            }.get(assessment_level, '⚪')
            st.metric("Assessment Level", f"{level_color} {assessment_level}")
        
        # Component scores
        component_scores = overall.get('component_scores', {})
        if component_scores:
            st.markdown("**Communication Component Scores:**")
            score_cols = st.columns(5)
            
            components = [
                ('Question Quality', 'question_quality', '❓'),
                ('Pace & Timing', 'pace_quality', '⏱️'),
                ('Language Fluency', 'language_quality', '🗣️'),
                ('Empathy & Rapport', 'empathy_quality', '❤️'),
                ('Professionalism', 'professional_quality', '👔')
            ]
            
            for i, (name, key, emoji) in enumerate(components):
                with score_cols[i]:
                    score = component_scores.get(key, 0)
                    st.metric(f"{emoji} {name}", f"{score:.0f}/100")
        
        # Key insights
        strengths = overall.get('key_strengths', [])
        improvements = overall.get('improvement_areas', [])
        
        if strengths or improvements:
            insight_col1, insight_col2 = st.columns(2)
            
            with insight_col1:
                if strengths:
                    st.markdown("**🌟 Key Strengths:**")
                    for strength in strengths:
                        st.markdown(f"• {strength}")
            
            with insight_col2:
                if improvements:
                    st.markdown("**📈 Improvement Areas:**")
                    for improvement in improvements:
                        st.markdown(f"• {improvement}")
    
    # Expandable detailed analysis report
    if advanced_analysis:
        with st.expander("📊 Detailed Audio Analysis Report", expanded=False):
            analysis_report = create_conversation_analysis_report(advanced_analysis)
            st.markdown(analysis_report)
    
    # Expandable patient conversation transcript
    with st.expander("📝 View Patient Conversation Transcript", expanded=False):
        messages = st.session_state["p_chat_history"]
        for i, message in enumerate(messages):
            role_emoji = "🎓" if message["role"] == "user" else "🤒"
            role_name = "Student" if message["role"] == "user" else "Patient"
            st.markdown(f"**{role_emoji} {role_name}:** {message['content']}")
            if i < len(messages) - 1:
                st.markdown("---")
    
    st.markdown('</div>', unsafe_allow_html=True)

def display_audio_quality_metrics():
    """Display audio quality metrics from the session."""
    if "audio_quality_metrics" not in st.session_state:
        return
    
    st.markdown('<div class="audio-analysis-card">', unsafe_allow_html=True)
    st.markdown("### 📊 Audio Quality Analysis")
    
    metrics = st.session_state["audio_quality_metrics"]
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Connection Quality**")
        quality_score = metrics.get('connection_quality', 0) * 100
        st.progress(quality_score / 100)
        st.caption(f"{quality_score:.1f}% - {'Excellent' if quality_score > 80 else 'Good' if quality_score > 60 else 'Fair'}")
        
    with col2:
        st.markdown("**Average Latency**")
        latency = metrics.get('latency_ms', 0)
        st.metric("Response Time", f"{latency:.0f}ms")
        st.caption("Lower is better")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Main application
def main():
    st.markdown('<div class="supervisor-header">', unsafe_allow_html=True)
    st.markdown("# 👨‍🏫 Supervisor Conversation")
    st.markdown("### Audio-Enhanced Feedback Session")
    st.markdown("Get detailed feedback on your patient conversation with voice interaction")
    st.markdown('</div>', unsafe_allow_html=True)

    client = setup()
    config, api_key = initialize_components()

    # Check prerequisites
    if not st.session_state.get("part_1_done") or not st.session_state.get("session_id"):
        st.error("❌ Please complete the Patient Conversation first.")
        st.info("Navigate to the Patient Conversation page to begin your audio assessment.")
        st.stop()

    # Initialize supervisor conversation state
    if "s_conversation_initialized" not in st.session_state:
        st.session_state["s_conversation_initialized"] = False
        st.session_state["s_conversation_handler"] = None
        st.session_state["s_conversation_active"] = False
        st.session_state["s_conversation_finished"] = False
        st.session_state["s_chat_history"] = []
        st.session_state["s_response_counter"] = 0
        st.session_state["s_transcript_segments"] = []

    # Display patient conversation summary
    display_patient_conversation_summary()
    
    # Display audio quality metrics if available
    display_audio_quality_metrics()

    # Main conversation interface
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### 🎙️ Audio Controls")
        
        # Initialize conversation handler
        if not st.session_state["s_conversation_initialized"]:
            if st.button("🎙️ Start Supervisor Audio Session", type="primary", use_container_width=True):
                try:
                    # Get patient conversation context and analysis
                    patient_context = format_patient_conversation_context()
                    audio_analysis = get_patient_conversation_analysis()
                    
                    # Create enhanced supervisor prompt
                    enhanced_prompt = create_enhanced_supervisor_prompt(patient_context, audio_analysis)
                    
                    # Initialize conversation handler
                    conversation_handler = ConversationHandler(config, api_key)
                    st.session_state["s_conversation_handler"] = conversation_handler
                    
                    # Start conversation with enhanced prompt
                    async def start_supervisor_conversation():
                        success = await conversation_handler.start_conversation(enhanced_prompt)
                        if success:
                            st.session_state["s_conversation_initialized"] = True
                            st.session_state["s_conversation_active"] = True
                            st.success("✅ Connected to supervisor!")
                            st.rerun()
                        else:
                            st.error("❌ Failed to connect to supervisor")
                    
                    # Run async function
                    asyncio.run(start_supervisor_conversation())
                    
                except Exception as e:
                    st.error(f"❌ Error starting supervisor conversation: {str(e)}")
        
        else:
            # Conversation is initialized
            conversation_handler = st.session_state["s_conversation_handler"]
            
            if conversation_handler and not st.session_state["s_conversation_finished"]:
                # Display conversation status
                status = conversation_handler.get_conversation_status()
                current_state = status.get('state', 'unknown')
                
                # State-specific controls
                if current_state == "waiting_for_user":
                    if st.button("🔴 Start Recording", type="primary", use_container_width=True):
                        async def start_recording():
                            success = await conversation_handler.start_recording()
                            if success:
                                st.rerun()
                        asyncio.run(start_recording())
                
                elif current_state == "user_speaking":
                    if st.button("⏹️ Stop Recording", type="secondary", use_container_width=True):
                        async def stop_recording():
                            success = await conversation_handler.stop_recording()
                            if success:
                                st.rerun()
                        asyncio.run(stop_recording())
                
                # Current status display
                st.markdown("### 📊 Session Status")
                
                # Status indicator
                status_colors = {
                    "waiting_for_user": "🟢 Ready for input",
                    "user_speaking": "🔴 Recording...",
                    "processing": "🟡 Processing...",
                    "ai_responding": "🔵 Supervisor responding...",
                    "completed": "✅ Session complete"
                }
                st.info(status_colors.get(current_state, f"Status: {current_state}"))
                
                # Session metrics
                duration = status.get('duration_seconds', 0)
                st.metric("Duration", f"{duration // 60:.0f}:{duration % 60:02.0f}")
                st.metric("Exchanges", status.get('response_count', 0))
                
                # Progress bars
                if status.get('max_responses', 50) > 0:
                    progress = min(status.get('response_count', 0) / status.get('max_responses', 50), 1.0)
                    st.progress(progress)
                    st.caption(f"{status.get('response_count', 0)}/{status.get('max_responses', 50)} responses")
                
                # Audio quality indicators
                audio_quality = status.get('audio_quality', {})
                if audio_quality:
                    st.markdown("**Audio Quality**")
                    signal_level = audio_quality.get('signal_level', 0)
                    st.progress(min(signal_level * 5, 1.0))  # Normalize signal level
                    
                    connection_quality = audio_quality.get('connection_quality', 0)
                    if connection_quality > 0:
                        st.caption(f"Connection: {connection_quality*100:.0f}%")
                
                # Finish conversation button
                st.markdown("---")
                if st.button("🏁 Finish Supervisor Session", type="secondary", use_container_width=True):
                    async def end_conversation():
                        summary = await conversation_handler.end_conversation()
                        
                        # Log supervisor conversation
                        supervisor_data = {
                            "audio_duration": summary.get('duration_seconds', 0),
                            "transcript_segments": conversation_handler.get_transcript(),
                            "conversation_metrics": {
                                "supervisor_speaking_time": 0,  # Would be calculated from actual audio
                                "student_speaking_time": 0,
                                "average_response_time": 0,
                                "total_exchanges": summary.get('response_count', 0)
                            }
                        }
                        
                        # Save to database
                        session_id = log_audio_transcript(
                            st.session_state["mongodb_uri"],
                            "supervisor",
                            supervisor_data
                        )
                        
                        st.session_state["s_conversation_finished"] = True
                        st.session_state["s_conversation_active"] = False
                        st.success("✅ Supervisor session completed and saved!")
                        st.rerun()
                    
                    asyncio.run(end_conversation())
    
    with col2:
        st.markdown("### 💬 Live Conversation")
        
        # Display conversation transcript
        if st.session_state["s_conversation_handler"]:
            transcript = st.session_state["s_conversation_handler"].get_transcript()
            
            if transcript:
                # Create scrollable transcript area
                transcript_container = st.container()
                with transcript_container:
                    for segment in transcript:
                        timestamp = segment.get('timestamp', datetime.now())
                        speaker = segment.get('speaker', 'unknown')
                        text = segment.get('text', '')
                        
                        if speaker == "user":
                            st.markdown(f"**🎓 Student** _{timestamp.strftime('%H:%M:%S')}_")
                            st.markdown(f"{text}")
                        elif speaker == "assistant":
                            st.markdown(f"**👨‍🏫 Supervisor** _{timestamp.strftime('%H:%M:%S')}_")
                            st.markdown(f"{text}")
                        
                        st.markdown("---")
            else:
                st.info("💭 Start the audio session to begin receiving feedback from your supervisor...")
                
                # Show example feedback topics
                st.markdown("### 📝 Feedback Topics You'll Receive:")
                feedback_topics = [
                    "Communication techniques and questioning skills",
                    "Assessment coverage (WOCCSNOR domains)",
                    "Professional tone and empathy",
                    "Active listening demonstration",
                    "Conversation flow and timing",
                    "Areas for improvement and study tips"
                ]
                
                for topic in feedback_topics:
                    st.markdown(f"• {topic}")
        
        # Text input fallback
        if st.session_state.get("s_conversation_initialized") and not st.session_state.get("s_conversation_finished"):
            st.markdown("---")
            st.markdown("### ⌨️ Text Input (Fallback)")
            
            text_input = st.text_area(
                "Type your response if audio is not working:",
                placeholder="Ask questions about your performance or request specific feedback...",
                height=100
            )
            
            if st.button("Send Text Message", disabled=not text_input):
                if text_input and st.session_state["s_conversation_handler"]:
                    async def send_text():
                        success = await st.session_state["s_conversation_handler"].send_text_message(text_input)
                        if success:
                            st.rerun()
                    
                    asyncio.run(send_text())

    # Conversation completion summary
    if st.session_state.get("s_conversation_finished"):
        st.markdown("---")
        st.markdown('<div class="feedback-section">', unsafe_allow_html=True)
        st.markdown("## 🎉 Supervisor Session Complete!")
        
        # Display session summary
        if st.session_state["s_conversation_handler"]:
            final_status = st.session_state["s_conversation_handler"].get_conversation_status()
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Duration", f"{final_status.get('duration_seconds', 0)//60:.0f} minutes")
            with col2:
                st.metric("Feedback Exchanges", final_status.get('response_count', 0))
            with col3:
                st.metric("Session Quality", "Complete ✅")
        
        # Final transcript download
        if st.button("📥 Download Complete Session", use_container_width=True):
            # Prepare download data
            session_data = {
                "patient_conversation": st.session_state.get("p_chat_history", []),
                "supervisor_feedback": st.session_state["s_conversation_handler"].get_transcript() if st.session_state["s_conversation_handler"] else [],
                "analysis": get_patient_conversation_analysis(),
                "timestamp": datetime.now().isoformat()
            }
            
            st.download_button(
                label="💾 Download Session Data (JSON)",
                data=json.dumps(session_data, indent=2, default=str),
                file_name=f"physiobot_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Navigation prompt
        st.success("🎓 **Well done!** You have completed both the patient conversation and supervisor feedback session.")
        st.info("💡 **Next Steps:** Review the feedback you received and consider practicing the suggested improvements in future sessions.")

if __name__ == "__main__":
    main()





