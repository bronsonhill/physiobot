"""
Audio Conversation Analysis Module for PhysioBot

This module provides comprehensive analysis of audio conversations for educational feedback,
including pace analysis, speaking time ratios, communication patterns, and quality metrics.
"""

import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import logging
import re
from collections import Counter

logger = logging.getLogger(__name__)

class AudioConversationAnalyzer:
    """
    Analyzes audio conversation data to provide detailed metrics and insights
    for educational feedback in physiotherapy training.
    """
    
    def __init__(self):
        """Initialize the audio conversation analyzer."""
        self.analysis_cache = {}
        
        # Question patterns for analysis
        self.open_ended_patterns = [
            r'\bhow\b.*\?',
            r'\bwhat\b.*\?',
            r'\bwhy\b.*\?',
            r'\bwhen\b.*\?',
            r'\bwhere\b.*\?',
            r'\bdescribe\b.*\?',
            r'\btell me\b.*\?',
            r'\bexplain\b.*\?',
            r'\bcan you.*\?'
        ]
        
        self.closed_ended_patterns = [
            r'\bis\b.*\?',
            r'\bare\b.*\?',
            r'\bdo\b.*\?',
            r'\bdoes\b.*\?',
            r'\bhave\b.*\?',
            r'\bhas\b.*\?',
            r'\bwill\b.*\?',
            r'\bwould\b.*\?',
            r'\bcan\b.*\?'
        ]
        
        # Filler words for fluency analysis
        self.filler_words = [
            'um', 'uh', 'ah', 'er', 'like', 'you know', 'sort of', 'kind of',
            'actually', 'basically', 'literally', 'obviously', 'definitely'
        ]
        
        # Active listening indicators
        self.listening_indicators = [
            'mm-hmm', 'mhm', 'i see', 'okay', 'right', 'yes', 'uh-huh',
            'i understand', 'that makes sense', 'go on', 'continue'
        ]
        
        # Empathy indicators
        self.empathy_indicators = [
            'i\'m sorry', 'that must be', 'sounds like', 'i can imagine',
            'that\'s difficult', 'i understand', 'how frustrating',
            'that\'s concerning', 'i hear you'
        ]
    
    def analyze_conversation(self, 
                           transcript_segments: List[Dict[str, Any]], 
                           audio_duration: float = 0,
                           session_metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Perform comprehensive analysis of an audio conversation.
        
        Args:
            transcript_segments: List of conversation segments with timestamps
            audio_duration: Total duration of conversation in seconds
            session_metadata: Additional session metadata
            
        Returns:
            Dictionary containing comprehensive conversation analysis
        """
        try:
            # Basic conversation metrics
            basic_metrics = self._analyze_basic_metrics(transcript_segments, audio_duration)
            
            # Communication patterns
            communication_patterns = self._analyze_communication_patterns(transcript_segments)
            
            # Question analysis
            question_analysis = self._analyze_questions(transcript_segments)
            
            # Pace and timing analysis
            pace_analysis = self._analyze_pace_and_timing(transcript_segments, audio_duration)
            
            # Language quality analysis
            language_quality = self._analyze_language_quality(transcript_segments)
            
            # Empathy and rapport analysis
            empathy_analysis = self._analyze_empathy_and_rapport(transcript_segments)
            
            # Professional communication analysis
            professional_analysis = self._analyze_professional_communication(transcript_segments)
            
            # Overall assessment
            overall_assessment = self._generate_overall_assessment(
                basic_metrics, communication_patterns, question_analysis,
                pace_analysis, language_quality, empathy_analysis, professional_analysis
            )
            
            return {
                'basic_metrics': basic_metrics,
                'communication_patterns': communication_patterns,
                'question_analysis': question_analysis,
                'pace_analysis': pace_analysis,
                'language_quality': language_quality,
                'empathy_analysis': empathy_analysis,
                'professional_analysis': professional_analysis,
                'overall_assessment': overall_assessment,
                'analysis_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing conversation: {e}")
            return {'error': str(e)}
    
    def _analyze_basic_metrics(self, segments: List[Dict[str, Any]], duration: float) -> Dict[str, Any]:
        """Analyze basic conversation metrics."""
        if not segments:
            return {}
        
        student_segments = [s for s in segments if s.get('speaker') == 'user']
        patient_segments = [s for s in segments if s.get('speaker') == 'assistant']
        
        # Word counts
        student_words = sum(len(s.get('text', '').split()) for s in student_segments)
        patient_words = sum(len(s.get('text', '').split()) for s in patient_segments)
        
        # Character counts (for speech length estimation)
        student_chars = sum(len(s.get('text', '')) for s in student_segments)
        patient_chars = sum(len(s.get('text', '')) for s in patient_segments)
        
        # Calculate speaking time estimates (rough approximation)
        # Average reading speed: ~200 words per minute
        estimated_student_time = (student_words / 200) * 60  # seconds
        estimated_patient_time = (patient_words / 200) * 60  # seconds
        
        return {
            'total_exchanges': len(student_segments),
            'student_words': student_words,
            'patient_words': patient_words,
            'total_words': student_words + patient_words,
            'student_chars': student_chars,
            'patient_chars': patient_chars,
            'word_ratio': student_words / max(patient_words, 1),
            'estimated_student_speaking_time': estimated_student_time,
            'estimated_patient_speaking_time': estimated_patient_time,
            'speaking_time_ratio': estimated_student_time / max(estimated_patient_time, 1),
            'words_per_minute': (student_words + patient_words) / max(duration / 60, 1),
            'exchanges_per_minute': len(student_segments) / max(duration / 60, 1),
            'avg_student_response_length': student_words / max(len(student_segments), 1),
            'avg_patient_response_length': patient_words / max(len(patient_segments), 1)
        }
    
    def _analyze_communication_patterns(self, segments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze communication patterns and flow."""
        if not segments:
            return {}
        
        student_segments = [s for s in segments if s.get('speaker') == 'user']
        
        # Response length variability
        response_lengths = [len(s.get('text', '').split()) for s in student_segments]
        length_std = np.std(response_lengths) if response_lengths else 0
        
        # Conversation balance assessment
        total_words = sum(len(s.get('text', '').split()) for s in segments)
        student_word_percentage = sum(len(s.get('text', '').split()) for s in student_segments) / max(total_words, 1) * 100
        
        balance_assessment = self._assess_conversation_balance(student_word_percentage)
        
        # Turn-taking analysis
        turn_taking = self._analyze_turn_taking(segments)
        
        return {
            'response_length_variability': length_std,
            'student_word_percentage': student_word_percentage,
            'conversation_balance': balance_assessment,
            'turn_taking_analysis': turn_taking,
            'conversation_flow_score': self._calculate_flow_score(segments)
        }
    
    def _analyze_questions(self, segments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze question types and quality."""
        student_segments = [s for s in segments if s.get('speaker') == 'user']
        
        open_ended_count = 0
        closed_ended_count = 0
        total_questions = 0
        
        for segment in student_segments:
            text = segment.get('text', '').lower()
            
            # Count questions
            question_count = text.count('?')
            total_questions += question_count
            
            # Analyze question types
            for pattern in self.open_ended_patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    open_ended_count += 1
                    break
            else:
                for pattern in self.closed_ended_patterns:
                    if re.search(pattern, text, re.IGNORECASE):
                        closed_ended_count += 1
                        break
        
        question_ratio = open_ended_count / max(closed_ended_count, 1) if closed_ended_count > 0 else float('inf')
        question_percentage = total_questions / max(len(student_segments), 1) * 100
        
        return {
            'total_questions': total_questions,
            'open_ended_questions': open_ended_count,
            'closed_ended_questions': closed_ended_count,
            'question_ratio': question_ratio,
            'question_percentage': question_percentage,
            'question_quality_score': self._calculate_question_quality_score(
                open_ended_count, closed_ended_count, total_questions
            )
        }
    
    def _analyze_pace_and_timing(self, segments: List[Dict[str, Any]], duration: float) -> Dict[str, Any]:
        """Analyze conversation pace and timing patterns."""
        if not segments or duration <= 0:
            return {}
        
        # Calculate response intervals
        response_intervals = []
        for i in range(1, len(segments)):
            if segments[i].get('speaker') != segments[i-1].get('speaker'):
                # Different speakers - this represents a response time
                prev_time = segments[i-1].get('timestamp')
                curr_time = segments[i].get('timestamp')
                if prev_time and curr_time:
                    if isinstance(prev_time, str):
                        prev_time = datetime.fromisoformat(prev_time)
                    if isinstance(curr_time, str):
                        curr_time = datetime.fromisoformat(curr_time)
                    interval = (curr_time - prev_time).total_seconds()
                    response_intervals.append(interval)
        
        avg_response_time = np.mean(response_intervals) if response_intervals else 0
        response_time_std = np.std(response_intervals) if response_intervals else 0
        
        # Overall pace assessment
        pace_score = self._calculate_pace_score(duration, len(segments), avg_response_time)
        
        return {
            'average_response_time': avg_response_time,
            'response_time_variability': response_time_std,
            'total_duration': duration,
            'pace_score': pace_score,
            'pace_assessment': self._assess_pace(pace_score),
            'response_intervals': response_intervals[:10]  # Keep only first 10 for size
        }
    
    def _analyze_language_quality(self, segments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze language quality including fluency and filler words."""
        student_segments = [s for s in segments if s.get('speaker') == 'user']
        
        total_words = 0
        filler_count = 0
        
        for segment in student_segments:
            text = segment.get('text', '').lower()
            words = text.split()
            total_words += len(words)
            
            # Count filler words
            for filler in self.filler_words:
                filler_count += words.count(filler)
        
        filler_percentage = (filler_count / max(total_words, 1)) * 100
        fluency_score = max(0, 100 - filler_percentage * 2)  # Penalize filler words
        
        return {
            'total_student_words': total_words,
            'filler_word_count': filler_count,
            'filler_percentage': filler_percentage,
            'fluency_score': fluency_score,
            'language_clarity': self._assess_language_clarity(filler_percentage)
        }
    
    def _analyze_empathy_and_rapport(self, segments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze empathy and rapport-building indicators."""
        student_segments = [s for s in segments if s.get('speaker') == 'user']
        
        listening_indicator_count = 0
        empathy_indicator_count = 0
        
        for segment in student_segments:
            text = segment.get('text', '').lower()
            
            # Count active listening indicators
            for indicator in self.listening_indicators:
                if indicator in text:
                    listening_indicator_count += 1
            
            # Count empathy indicators
            for indicator in self.empathy_indicators:
                if indicator in text:
                    empathy_indicator_count += 1
        
        total_segments = len(student_segments)
        listening_score = (listening_indicator_count / max(total_segments, 1)) * 100
        empathy_score = (empathy_indicator_count / max(total_segments, 1)) * 100
        
        return {
            'active_listening_indicators': listening_indicator_count,
            'empathy_indicators': empathy_indicator_count,
            'listening_score': listening_score,
            'empathy_score': empathy_score,
            'rapport_assessment': self._assess_rapport(listening_score, empathy_score)
        }
    
    def _analyze_professional_communication(self, segments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze professional communication patterns."""
        student_segments = [s for s in segments if s.get('speaker') == 'user']
        
        # Professional language indicators
        professional_terms = [
            'patient', 'assessment', 'symptoms', 'condition', 'treatment',
            'therapy', 'rehabilitation', 'examination', 'diagnosis', 'prognosis'
        ]
        
        casual_language = [
            'yeah', 'yep', 'nah', 'gonna', 'wanna', 'gotta', 'kinda', 'sorta'
        ]
        
        professional_term_count = 0
        casual_language_count = 0
        
        for segment in student_segments:
            text = segment.get('text', '').lower()
            
            for term in professional_terms:
                professional_term_count += text.count(term)
            
            for casual in casual_language:
                casual_language_count += text.count(casual)
        
        professionalism_score = max(0, professional_term_count - casual_language_count)
        
        return {
            'professional_term_count': professional_term_count,
            'casual_language_count': casual_language_count,
            'professionalism_score': professionalism_score,
            'professional_communication_assessment': self._assess_professionalism(professionalism_score)
        }
    
    def _assess_conversation_balance(self, student_percentage: float) -> str:
        """Assess conversation balance based on student speaking percentage."""
        if student_percentage < 20:
            return "Too passive - student needs to ask more questions"
        elif student_percentage > 60:
            return "Too dominant - student should allow more patient responses"
        else:
            return "Well balanced"
    
    def _calculate_flow_score(self, segments: List[Dict[str, Any]]) -> float:
        """Calculate a conversation flow score based on turn-taking patterns."""
        if len(segments) < 2:
            return 100.0
        
        # Analyze turn-taking patterns
        interruptions = 0
        natural_transitions = 0
        
        for i in range(1, len(segments)):
            prev_speaker = segments[i-1].get('speaker')
            curr_speaker = segments[i].get('speaker')
            
            if prev_speaker == curr_speaker:
                # Same speaker continuing - potential interruption recovery
                interruptions += 1
            else:
                # Different speakers - natural transition
                natural_transitions += 1
        
        flow_score = (natural_transitions / max(natural_transitions + interruptions, 1)) * 100
        return min(100, max(0, flow_score))
    
    def _calculate_question_quality_score(self, open_ended: int, closed_ended: int, total: int) -> float:
        """Calculate question quality score based on question types."""
        if total == 0:
            return 0
        
        # Prefer open-ended questions but allow some closed questions
        ideal_ratio = 0.7  # 70% open-ended, 30% closed
        actual_ratio = open_ended / total if total > 0 else 0
        
        # Score based on how close to ideal ratio
        ratio_score = 100 - abs(ideal_ratio - actual_ratio) * 100
        
        # Bonus for having any questions at all
        question_presence_bonus = min(total * 10, 50)
        
        return min(100, max(0, ratio_score + question_presence_bonus))
    
    def _calculate_pace_score(self, duration: float, segments: int, avg_response_time: float) -> float:
        """Calculate pace score based on conversation dynamics."""
        if duration <= 0 or segments <= 0:
            return 0
        
        # Ideal pace: 2-5 exchanges per minute, 2-8 second response times
        exchanges_per_minute = segments / (duration / 60)
        
        pace_score = 100
        
        # Penalize too fast or too slow exchange rate
        if exchanges_per_minute < 1:
            pace_score -= 30  # Too slow
        elif exchanges_per_minute > 8:
            pace_score -= 20  # Too fast
        
        # Penalize inappropriate response times
        if avg_response_time > 15:
            pace_score -= 25  # Too slow to respond
        elif avg_response_time < 1:
            pace_score -= 15  # Too quick, might be interrupting
        
        return max(0, min(100, pace_score))
    
    def _assess_pace(self, pace_score: float) -> str:
        """Assess pace based on score."""
        if pace_score >= 80:
            return "Excellent pace"
        elif pace_score >= 60:
            return "Good pace"
        elif pace_score >= 40:
            return "Moderate pace - some adjustments needed"
        else:
            return "Needs improvement - significant pacing issues"
    
    def _assess_language_clarity(self, filler_percentage: float) -> str:
        """Assess language clarity based on filler word percentage."""
        if filler_percentage < 2:
            return "Excellent clarity"
        elif filler_percentage < 5:
            return "Good clarity"
        elif filler_percentage < 10:
            return "Moderate clarity - reduce filler words"
        else:
            return "Needs improvement - too many filler words"
    
    def _assess_rapport(self, listening_score: float, empathy_score: float) -> str:
        """Assess rapport building based on listening and empathy scores."""
        combined_score = (listening_score + empathy_score) / 2
        
        if combined_score >= 60:
            return "Excellent rapport building"
        elif combined_score >= 40:
            return "Good rapport building"
        elif combined_score >= 20:
            return "Moderate rapport - increase active listening"
        else:
            return "Needs improvement - focus on empathy and listening"
    
    def _assess_professionalism(self, professionalism_score: float) -> str:
        """Assess professional communication level."""
        if professionalism_score >= 10:
            return "Highly professional communication"
        elif professionalism_score >= 5:
            return "Professional communication"
        elif professionalism_score >= 0:
            return "Mostly professional - minor improvements needed"
        else:
            return "Needs improvement - reduce casual language"
    
    def _analyze_turn_taking(self, segments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze turn-taking patterns in the conversation."""
        if len(segments) < 2:
            return {'interruptions': 0, 'natural_transitions': 0}
        
        interruptions = 0
        natural_transitions = 0
        
        for i in range(1, len(segments)):
            prev_speaker = segments[i-1].get('speaker')
            curr_speaker = segments[i].get('speaker')
            
            if prev_speaker == curr_speaker:
                interruptions += 1
            else:
                natural_transitions += 1
        
        return {
            'interruptions': interruptions,
            'natural_transitions': natural_transitions,
            'interruption_rate': (interruptions / max(len(segments) - 1, 1)) * 100
        }
    
    def _generate_overall_assessment(self, *analysis_components) -> Dict[str, Any]:
        """Generate overall assessment summary."""
        basic_metrics, communication_patterns, question_analysis, pace_analysis, language_quality, empathy_analysis, professional_analysis = analysis_components
        
        # Calculate overall scores
        scores = {
            'question_quality': question_analysis.get('question_quality_score', 0),
            'pace_quality': pace_analysis.get('pace_score', 0),
            'language_quality': language_quality.get('fluency_score', 0),
            'empathy_quality': (empathy_analysis.get('listening_score', 0) + empathy_analysis.get('empathy_score', 0)) / 2,
            'professional_quality': min(100, max(0, professional_analysis.get('professionalism_score', 0) * 10))
        }
        
        overall_score = sum(scores.values()) / len(scores)
        
        # Generate assessment level
        if overall_score >= 80:
            assessment_level = "Excellent"
        elif overall_score >= 65:
            assessment_level = "Good"
        elif overall_score >= 50:
            assessment_level = "Satisfactory"
        else:
            assessment_level = "Needs Improvement"
        
        return {
            'overall_score': overall_score,
            'assessment_level': assessment_level,
            'component_scores': scores,
            'key_strengths': self._identify_strengths(scores),
            'improvement_areas': self._identify_improvement_areas(scores)
        }
    
    def _identify_strengths(self, scores: Dict[str, float]) -> List[str]:
        """Identify key strengths based on scores."""
        strengths = []
        
        if scores.get('question_quality', 0) >= 70:
            strengths.append("Effective questioning techniques")
        if scores.get('pace_quality', 0) >= 70:
            strengths.append("Appropriate conversation pacing")
        if scores.get('language_quality', 0) >= 70:
            strengths.append("Clear and fluent communication")
        if scores.get('empathy_quality', 0) >= 70:
            strengths.append("Good empathy and active listening")
        if scores.get('professional_quality', 0) >= 70:
            strengths.append("Professional communication style")
        
        return strengths or ["Completing the audio assessment"]
    
    def _identify_improvement_areas(self, scores: Dict[str, float]) -> List[str]:
        """Identify areas needing improvement based on scores."""
        improvements = []
        
        if scores.get('question_quality', 0) < 50:
            improvements.append("Question formulation and variety")
        if scores.get('pace_quality', 0) < 50:
            improvements.append("Conversation pacing and timing")
        if scores.get('language_quality', 0) < 50:
            improvements.append("Speech fluency and clarity")
        if scores.get('empathy_quality', 0) < 50:
            improvements.append("Empathy and active listening skills")
        if scores.get('professional_quality', 0) < 50:
            improvements.append("Professional communication style")
        
        return improvements or ["Continue practicing audio communication"]

def create_conversation_analysis_report(analysis_data: Dict[str, Any]) -> str:
    """
    Create a formatted analysis report for supervisor feedback.
    
    Args:
        analysis_data: Complete analysis data from AudioConversationAnalyzer
        
    Returns:
        Formatted analysis report string
    """
    if not analysis_data or 'error' in analysis_data:
        return "Analysis data unavailable."
    
    basic = analysis_data.get('basic_metrics', {})
    patterns = analysis_data.get('communication_patterns', {})
    questions = analysis_data.get('question_analysis', {})
    pace = analysis_data.get('pace_analysis', {})
    language = analysis_data.get('language_quality', {})
    empathy = analysis_data.get('empathy_analysis', {})
    professional = analysis_data.get('professional_analysis', {})
    overall = analysis_data.get('overall_assessment', {})
    
    report = f"""
## Detailed Audio Conversation Analysis

### Overall Assessment: {overall.get('assessment_level', 'Unknown')} ({overall.get('overall_score', 0):.1f}/100)

### Key Metrics:
- **Total Exchanges**: {basic.get('total_exchanges', 0)}
- **Student Words**: {basic.get('student_words', 0)} ({basic.get('student_word_percentage', 0):.1f}% of conversation)
- **Questions Asked**: {questions.get('total_questions', 0)} ({questions.get('open_ended_questions', 0)} open-ended, {questions.get('closed_ended_questions', 0)} closed)
- **Conversation Balance**: {patterns.get('conversation_balance', 'Unknown')}

### Communication Quality Scores:
- **Question Quality**: {questions.get('question_quality_score', 0):.1f}/100
- **Pace & Timing**: {pace.get('pace_score', 0):.1f}/100 - {pace.get('pace_assessment', 'Unknown')}
- **Language Fluency**: {language.get('fluency_score', 0):.1f}/100 - {language.get('language_clarity', 'Unknown')}
- **Empathy & Rapport**: {empathy.get('listening_score', 0):.1f}/100 - {empathy.get('rapport_assessment', 'Unknown')}
- **Professionalism**: {professional.get('professionalism_score', 0):.1f}/100 - {professional.get('professional_communication_assessment', 'Unknown')}

### Key Strengths:
""" + "\n".join(f"• {strength}" for strength in overall.get('key_strengths', []))

    report += f"""

### Areas for Improvement:
""" + "\n".join(f"• {area}" for area in overall.get('improvement_areas', []))

    if pace.get('average_response_time'):
        report += f"""

### Timing Analysis:
- **Average Response Time**: {pace.get('average_response_time', 0):.1f} seconds
- **Pace Assessment**: {pace.get('pace_assessment', 'Unknown')}
"""

    if language.get('filler_percentage', 0) > 0:
        report += f"""
- **Filler Words**: {language.get('filler_word_count', 0)} instances ({language.get('filler_percentage', 0):.1f}% of speech)
"""

    return report