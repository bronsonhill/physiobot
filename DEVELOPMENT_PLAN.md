# PhysioBot Realtime Audio Development Plan

## Executive Summary

This development plan outlines the transition of the physiobot platform from a text-based chat interface to a realtime audio conversation system using OpenAI's Realtime Audio API. The project maintains the core educational framework while introducing voice interaction capabilities for a more realistic patient-practitioner simulation experience.

**Updated Scope**: The platform is designed to support multiple cohorts simultaneously with proper data isolation and administrative controls.

## Current Architecture Analysis

### Existing Components
- **Frontend**: Streamlit-based web application with Home.py and two conversation pages
- **Backend**: OpenAI GPT-4o-mini for text completions
- **Database**: MongoDB with `physiobot` database containing:
  - `valid_identifiers` collection for student authentication
  - `transcripts` collection for conversation logs
- **Educational Framework**: WOCCSNOR-based patient assessment with structured feedback
- **Authentication**: Student identifier validation system

### Key Features to Preserve
- Two-phase conversation flow (Patient → Supervisor)
- Student identifier validation
- Conversation transcript logging
- Educational assessment framework
- Response limiting and conversation finishing mechanisms

## Project Scope & Objectives

### Primary Goals
1. Replace text chat with realtime audio conversation
2. Implement OpenAI Realtime Audio API integration
3. Create configurable audio settings system
4. Migrate to new `physiobot-realtime` database
5. Maintain educational effectiveness while improving realism

### MVP Constraints
- Target: Small class trial (20-50 students)
- Focus on core functionality over advanced features
- Maintain existing educational assessment criteria
- Ensure stable audio experience across common browsers

## Multi-Phase Development Plan

### Phase 1: Foundation & Infrastructure (Weeks 1-2)

#### Dependencies: None (Can start immediately)

#### Deliverables:
1. **Project Structure Setup**
   - Create new `physiobot-realtime` project structure
   - Set up virtual environment with realtime audio dependencies
   - Configure development environment

2. **Database Migration**
   - Create new `physiobot-realtime` MongoDB database
   - Migrate schema for `valid_identifiers` collection
   - Design new `audio_transcripts` collection schema with audio-specific fields:
     ```json
     {
       "_id": ObjectId,
       "timestamp": DateTime,
       "identifier": String,
       "session_duration": Number,
       "patient_conversation": {
         "audio_duration": Number,
         "transcript": Array,
         "audio_quality_metrics": Object
       },
       "supervisor_conversation": {
         "audio_duration": Number,
         "transcript": Array,
         "audio_quality_metrics": Object
       }
     }
     ```

3. **Configuration System**
   - Create `config.yaml` for audio settings:
     ```yaml
     audio_settings:
       voice_type: "alloy"  # OpenAI voice options: alloy, echo, fable, onyx, nova, shimmer
       speech_speed: 1.0    # Range: 0.25 - 4.0
       conversation_detection:
         silence_threshold: 2.0  # seconds
         volume_threshold: 0.1
       quality_settings:
         sample_rate: 24000
         format: "pcm16"
     
     conversation_settings:
       max_duration: 1800    # 30 minutes
       auto_save_interval: 300  # 5 minutes
       connection_timeout: 30
     
     ui_settings:
       show_live_transcript: true
       enable_audio_visualization: true
     ```

4. **Requirements & Dependencies**
   - Update requirements.txt with realtime audio dependencies
   - Set up environment variables for OpenAI Realtime API

#### Acceptance Criteria:
- [ ] New project structure created
- [ ] Database schema designed and tested
- [ ] Configuration system implemented
- [ ] Development environment fully configured

---

### Phase 2: Core Audio Infrastructure (Weeks 2-3)

#### Dependencies: Phase 1 completion

#### Deliverables:
1. **OpenAI Realtime Audio Integration**
   - Implement WebSocket connection handler for OpenAI Realtime API
   - Create audio capture and playback utilities
   - Build conversation state management system

2. **Audio Components**
   - `utils/audio_manager.py`: Handle audio input/output
   - `utils/realtime_client.py`: OpenAI Realtime API client
   - `utils/conversation_handler.py`: Manage conversation flow

3. **Browser Audio Interface**
   - JavaScript components for audio capture
   - Real-time audio streaming to backend
   - Audio playback controls and visualization

4. **Testing Framework**
   - Unit tests for audio components
   - Integration tests for OpenAI API connectivity
   - Audio quality testing utilities

#### Acceptance Criteria:
- [ ] Stable WebSocket connection to OpenAI Realtime API
- [ ] Audio capture working in browser
- [ ] Audio playback functioning correctly
- [ ] Basic conversation flow established

---

### Phase 3: Patient Conversation Implementation (Weeks 3-4)

#### Dependencies: Phase 2 completion

#### Deliverables:
1. **Patient Conversation Page**
   - Replace `pages/1_Patient_Conversation.py` with audio-enabled version
   - Implement realtime conversation with patient persona
   - Add audio controls (mute, volume, start/stop recording)

2. **Prompt Integration**
   - Adapt existing patient prompt for audio conversation
   - Implement conversation instructions for audio format
   - Add audio-specific behavioral guidelines

3. **Real-time Transcript Display**
   - Live transcript generation during conversation
   - Conversation history display
   - Audio playback controls for review

4. **Conversation Management**
   - Implement conversation timing controls
   - Add pause/resume functionality
   - Create conversation finishing mechanism

#### Acceptance Criteria:
- [ ] Patient conversation fully functional in audio
- [ ] Live transcript generation working
- [ ] Conversation controls responsive
- [ ] Audio quality meets minimum standards

---

### Phase 4: Supervisor Conversation Implementation (Weeks 4-5)

#### Dependencies: Phase 3 completion

#### Deliverables:
1. **Supervisor Conversation Page**
   - Replace `pages/2_Supervisor_Conversation.py` with audio version
   - Implement conversation review and feedback system
   - Integrate patient conversation context

2. **Feedback Integration**
   - Audio-aware feedback prompts
   - Assessment of verbal communication skills
   - Evaluation of audio-specific factors (tone, pace, clarity)

3. **Audio Analysis Features**
   - Conversation pace analysis
   - Speaking time ratios (student vs. patient)
   - Audio quality metrics for feedback

#### Acceptance Criteria:
- [ ] Supervisor conversation functional
- [ ] Feedback system adapted for audio format
- [ ] Audio analysis metrics implemented
- [ ] Conversation context properly maintained

---

### Phase 5: UI/UX Enhancement & Testing (Weeks 5-6)

#### Dependencies: Phase 4 completion

#### Deliverables:
1. **Enhanced User Interface**
   - Modern audio conversation interface
   - Visual indicators for audio activity
   - Improved navigation and controls

2. **Configuration Interface**
   - Admin panel for audio settings adjustment
   - Student-facing audio preferences
   - Troubleshooting and diagnostics tools

3. **Comprehensive Testing**
   - Cross-browser compatibility testing
   - Audio quality validation across devices
   - Performance testing under load
   - User acceptance testing with pilot group

4. **Documentation & Training Materials**
   - Updated user documentation
   - Technical documentation for maintenance
   - Student orientation materials

#### Acceptance Criteria:
- [ ] UI/UX meets modern standards
- [ ] Configuration system user-friendly
- [ ] Cross-browser compatibility verified
- [ ] Documentation complete

---

### Phase 6: Deployment & Pilot Testing (Weeks 6-7)

#### Dependencies: Phase 5 completion

#### Deliverables:
1. **Production Deployment**
   - Configure production environment
   - Set up monitoring and logging
   - Implement backup and recovery procedures

2. **Pilot Program Launch**
   - Deploy to limited user group (5-10 students)
   - Monitor system performance and user feedback
   - Collect audio quality metrics

3. **Feedback Collection & Iteration**
   - Implement feedback collection system
   - Analyze user experience data
   - Make necessary adjustments based on pilot results

4. **Full Deployment Preparation**
   - Scale infrastructure for full class
   - Finalize configuration settings
   - Prepare support documentation

#### Acceptance Criteria:
- [ ] Production environment stable
- [ ] Pilot testing completed successfully
- [ ] User feedback incorporated
- [ ] System ready for full deployment

---

## Technical Implementation Details

### Architecture Changes

#### New Technology Stack
- **Frontend**: Streamlit + JavaScript audio components
- **Backend**: Python with WebSocket support
- **Audio API**: OpenAI Realtime Audio API
- **Database**: MongoDB (physiobot-realtime)
- **Audio Processing**: Browser-native WebRTC APIs

#### Key Components

1. **Audio Manager (`utils/audio_manager.py`)**
   ```python
   class AudioManager:
       def __init__(self, config):
           self.config = config
           self.is_recording = False
           self.is_playing = False
       
       async def start_recording(self):
           # Implement audio capture
       
       async def stop_recording(self):
           # Stop capture and process audio
       
       async def play_audio(self, audio_data):
           # Play received audio
   ```

2. **Realtime Client (`utils/realtime_client.py`)**
   ```python
   class RealtimeClient:
       def __init__(self, api_key, config):
           self.api_key = api_key
           self.config = config
           self.websocket = None
       
       async def connect(self):
           # Establish WebSocket connection
       
       async def send_audio(self, audio_data):
           # Send audio to OpenAI
       
       async def receive_audio(self):
           # Receive and process audio response
   ```

3. **Configuration Manager (`utils/config_manager.py`)**
   ```python
   class ConfigManager:
       def __init__(self, config_path="config.yaml"):
           self.config = self.load_config(config_path)
       
       def get_audio_settings(self):
           return self.config['audio_settings']
       
       def update_setting(self, key, value):
           # Update configuration dynamically
   ```

### Database Schema Updates

#### Audio Transcripts Collection
```json
{
  "_id": ObjectId,
  "timestamp": DateTime,
  "identifier": String,
  "session_metadata": {
    "duration_seconds": Number,
    "audio_quality_score": Number,
    "connection_stability": Number,
    "browser_info": String,
    "device_info": String
  },
  "patient_conversation": {
    "audio_duration": Number,
    "transcript_segments": [
      {
        "timestamp": Number,
        "speaker": String, // "student" or "patient"
        "text": String,
        "confidence": Number,
        "audio_quality": Number
      }
    ],
    "conversation_metrics": {
      "student_speaking_time": Number,
      "patient_speaking_time": Number,
      "average_response_time": Number,
      "interruptions_count": Number
    }
  },
  "supervisor_conversation": {
    // Similar structure to patient_conversation
  },
  "assessment_data": {
    "communication_scores": Object,
    "audio_quality_feedback": String,
    "technical_issues": Array
  }
}
```

### Configuration System

#### Admin Configuration Interface
Create a new admin page for configuration management:

```python
# pages/Admin_Configuration.py
import streamlit as st
import yaml
from utils.config_manager import ConfigManager

def admin_config_page():
    st.title("Audio Configuration")
    
    config_manager = ConfigManager()
    
    # Audio Settings
    st.subheader("Audio Settings")
    voice_type = st.selectbox("Voice Type", 
                             ["alloy", "echo", "fable", "onyx", "nova", "shimmer"])
    speech_speed = st.slider("Speech Speed", 0.25, 4.0, 1.0)
    
    # Conversation Settings
    st.subheader("Conversation Settings")
    max_duration = st.number_input("Max Duration (seconds)", value=1800)
    
    if st.button("Save Configuration"):
        # Save configuration changes
        config_manager.update_settings({
            'audio_settings': {
                'voice_type': voice_type,
                'speech_speed': speech_speed
            },
            'conversation_settings': {
                'max_duration': max_duration
            }
        })
        st.success("Configuration updated successfully!")
```

## Risk Management

### Technical Risks

1. **Audio Quality Issues**
   - **Risk**: Poor audio quality affecting user experience
   - **Mitigation**: Implement quality monitoring, provide troubleshooting guides
   - **Contingency**: Fallback to text mode if audio fails

2. **Browser Compatibility**
   - **Risk**: Audio features not working across all browsers
   - **Mitigation**: Test extensively on Chrome, Firefox, Safari, Edge
   - **Contingency**: Provide browser-specific instructions

3. **OpenAI API Limitations**
   - **Risk**: API rate limits or downtime
   - **Mitigation**: Implement retry logic, rate limiting
   - **Contingency**: Queue system for high-demand periods

4. **Network Connectivity**
   - **Risk**: Poor internet affecting audio streaming
   - **Mitigation**: Implement connection quality detection
   - **Contingency**: Offline mode with local recording

### Educational Risks

1. **Learning Effectiveness**
   - **Risk**: Audio format may not be as effective as text
   - **Mitigation**: Conduct comparison studies, collect feedback
   - **Contingency**: Hybrid mode with both audio and text options

2. **Assessment Accuracy**
   - **Risk**: Difficulty assessing audio-based communication
   - **Mitigation**: Develop audio-specific assessment criteria
   - **Contingency**: Manual review process for critical assessments

## Success Metrics

### Technical Metrics
- Audio quality score > 4.0/5.0
- Connection stability > 95%
- Average response time < 2 seconds
- Cross-browser compatibility > 90%

### Educational Metrics
- Student satisfaction score > 4.0/5.0
- Completion rate > 85%
- Assessment accuracy maintained within 5% of text version
- Time to complete conversations < 120% of text version

### Operational Metrics
- System uptime > 99%
- Support ticket volume < 10% of user base
- Configuration change success rate > 95%

## Resource Requirements

### Development Team
- 1 Senior Full-Stack Developer
- 1 Audio/WebRTC Specialist
- 1 UI/UX Designer
- 1 QA Engineer
- 1 DevOps Engineer

### Infrastructure
- MongoDB Atlas cluster (M10 tier minimum)
- OpenAI Realtime API quota
- CDN for audio file delivery
- Monitoring and logging infrastructure

### Timeline Summary
- **Total Duration**: 7 weeks
- **Critical Path**: Phases 1→2→3→4→5→6
- **Parallel Opportunities**: UI/UX design can run parallel to backend development
- **Buffer Time**: 1-2 weeks for unexpected issues

## Conclusion

This development plan provides a structured approach to transitioning the physiobot platform to realtime audio conversation while maintaining educational effectiveness and system reliability. The phased approach allows for incremental testing and validation, reducing risk and ensuring successful deployment for the target MVP use case.

The plan emphasizes maintaining the existing educational framework while enhancing the user experience through more realistic audio-based patient interactions. The configuration system ensures flexibility for different use cases and technical environments.

Regular milestone reviews and stakeholder feedback sessions should be scheduled throughout the development process to ensure alignment with educational objectives and technical requirements.

## Multi-Cohort Support Architecture

### Overview
The platform will support multiple cohorts simultaneously, each with:
- Isolated student data and transcripts
- Configurable audio and conversation settings per cohort
- Separate instructor/administrator access controls
- Academic year and semester management
- Bulk student management tools

### Enhanced Database Schema

#### Cohorts Collection
```json
{
  "_id": ObjectId,
  "cohort_id": String,        // e.g., "PHYSIO2024_SEM1"
  "cohort_name": String,      // e.g., "First Year Physiotherapy 2024"
  "academic_year": String,    // e.g., "2024"
  "semester": String,         // e.g., "Semester 1"
  "instructor_emails": Array, // ["instructor1@uni.edu", "instructor2@uni.edu"]
  "created_at": DateTime,
  "is_active": Boolean,
  "settings": {
    "audio_settings": {
      "voice_type": String,
      "speech_speed": Number,
      "conversation_detection": Object
    },
    "conversation_settings": {
      "max_duration": Number,
      "max_responses": Number
    },
    "assignment_settings": {
      "patient_prompt_override": String,     // Optional custom prompt
      "supervisor_prompt_override": String,  // Optional custom prompt
      "due_date": DateTime,
      "instructions": String
    }
  }
}
```

#### Updated Valid Identifiers Collection
```json
{
  "_id": ObjectId,
  "identifier": String,
  "cohort_id": String,        // Links to cohorts collection
  "student_metadata": {
    "student_id": String,     // University student ID (hashed)
    "year_level": String,     // "Year 1", "Year 2", etc.
    "program": String         // "Physiotherapy", "Occupational Therapy"
  },
  "created_at": DateTime,
  "is_active": Boolean,
  "assignment_attempts": Number,
  "last_access": DateTime
}
```

#### Updated Audio Transcripts Collection
```json
{
  "_id": ObjectId,
  "timestamp": DateTime,
  "identifier": String,
  "cohort_id": String,        // For data isolation
  "assignment_id": String,    // For multiple assignments per cohort
  "session_metadata": {
    "duration_seconds": Number,
    "audio_quality_score": Number,
    "connection_stability": Number,
    "browser_info": String,
    "device_info": String
  },
  "patient_conversation": {
    // ... existing structure
  },
  "supervisor_conversation": {
    // ... existing structure
  },
  "assessment_data": {
    // ... existing structure
  }
}
```

#### Instructors Collection (New)
```json
{
  "_id": ObjectId,
  "email": String,
  "name": String,
  "role": String,             // "instructor", "admin", "coordinator"
  "cohort_access": Array,     // ["PHYSIO2024_SEM1", "PHYSIO2024_SEM2"]
  "permissions": {
    "view_transcripts": Boolean,
    "export_data": Boolean,
    "manage_students": Boolean,
    "configure_audio": Boolean
  },
  "created_at": DateTime,
  "last_login": DateTime
}
```

### Multi-Cohort Implementation Plan

#### Phase 1 Enhancement: Multi-Cohort Foundation
**Additional Deliverables:**

1. **Cohort Management System**
   - `utils/cohort_manager.py`: Cohort creation and management
   - `utils/instructor_auth.py`: Instructor authentication and permissions
   - Database migration scripts for existing data

2. **Enhanced Configuration System**
   ```python
   # utils/cohort_config_manager.py
   class CohortConfigManager:
       def __init__(self):
           self.mongodb_client = get_mongo_client()
       
       def get_cohort_config(self, cohort_id):
           """Get configuration for specific cohort"""
           cohort = self.mongodb_client.physiobot_realtime.cohorts.find_one(
               {"cohort_id": cohort_id}
           )
           return cohort.get('settings', {}) if cohort else {}
       
       def update_cohort_config(self, cohort_id, settings):
           """Update configuration for specific cohort"""
           return self.mongodb_client.physiobot_realtime.cohorts.update_one(
               {"cohort_id": cohort_id},
               {"$set": {"settings": settings}}
           )
   ```

3. **Student Management Enhancement**
   ```python
   # scripts/bulk_student_management.py
   class BulkStudentManager:
       def load_cohort_students(self, csv_path, cohort_id):
           """Load students for specific cohort"""
           df = pd.read_csv(csv_path)
           df['cohort_id'] = cohort_id
           # Generate identifiers with cohort prefix
           df['identifier'] = df.apply(
               lambda row: f"{cohort_id}_{generate_identifier(row)}", 
               axis=1
           )
           return df
       
       def transfer_students(self, from_cohort, to_cohort):
           """Transfer students between cohorts"""
           # Implementation for cohort transitions
   ```

#### Phase 2 Enhancement: Multi-Cohort Authentication
**Additional Deliverables:**

1. **Enhanced Authentication System**
   - Cohort-based login validation
   - Session management with cohort context
   - Instructor dashboard for cohort selection

2. **Updated Home.py**
   ```python
   def enhanced_setup():
       # ... existing setup code ...
       
       if "cohort_id" not in st.session_state:
           st.session_state["cohort_id"] = None
       
       if "instructor_mode" not in st.session_state:
           st.session_state["instructor_mode"] = False
   
   def cohort_identifier_validation():
       identifier = st.session_state.get("user_identifier", "").strip()
       if not identifier:
           return False, None
       
       # Check if instructor login
       if "@" in identifier:
           return validate_instructor_login(identifier)
       
       # Regular student validation with cohort detection
       return validate_student_identifier(identifier)
   ```

#### Phase 3-4 Enhancement: Cohort-Aware Conversations
**Additional Deliverables:**

1. **Cohort-Specific Prompts**
   - Dynamic prompt loading based on cohort settings
   - Assignment-specific instructions
   - Customizable patient scenarios per cohort

2. **Data Isolation**
   - All database queries filtered by cohort_id
   - Session-based cohort context enforcement
   - Audit logging for cross-cohort access attempts

#### Phase 5 Enhancement: Multi-Cohort Management Interface
**Additional Deliverables:**

1. **Instructor Dashboard**
   ```python
   # pages/Instructor_Dashboard.py
   def instructor_dashboard():
       st.title("Instructor Dashboard")
       
       # Cohort selection
       cohorts = get_instructor_cohorts(st.session_state.get("instructor_email"))
       selected_cohort = st.selectbox("Select Cohort", cohorts)
       
       if selected_cohort:
           # Cohort statistics
           stats = get_cohort_statistics(selected_cohort)
           
           col1, col2, col3, col4 = st.columns(4)
           with col1:
               st.metric("Total Students", stats['total_students'])
           with col2:
               st.metric("Completed Assignments", stats['completed'])
           with col3:
               st.metric("Average Score", f"{stats['avg_score']:.1f}")
           with col4:
               st.metric("Avg Duration", f"{stats['avg_duration']:.0f}min")
           
           # Student progress table
           st.subheader("Student Progress")
           progress_df = get_student_progress(selected_cohort)
           st.dataframe(progress_df)
           
           # Export functionality
           if st.button("Export Cohort Data"):
               export_cohort_data(selected_cohort)
   ```

2. **Admin Configuration Interface**
   ```python
   # pages/Admin_Multi_Cohort.py
   def admin_multi_cohort_page():
       st.title("Multi-Cohort Administration")
       
       tab1, tab2, tab3 = st.tabs(["Cohort Management", "Student Management", "System Settings"])
       
       with tab1:
           # Create new cohort
           st.subheader("Create New Cohort")
           cohort_form()
           
           # Manage existing cohorts
           st.subheader("Existing Cohorts")
           cohorts_table()
       
       with tab2:
           # Bulk student operations
           st.subheader("Bulk Student Management")
           bulk_student_interface()
       
       with tab3:
           # System-wide settings
           st.subheader("System Configuration")
           system_settings_interface()
   ```

### Scalability Considerations

#### Database Optimization
1. **Indexing Strategy**
   ```javascript
   // MongoDB indexes for multi-cohort performance
   db.audio_transcripts.createIndex({"cohort_id": 1, "timestamp": -1})
   db.audio_transcripts.createIndex({"identifier": 1, "cohort_id": 1})
   db.valid_identifiers.createIndex({"cohort_id": 1, "is_active": 1})
   db.cohorts.createIndex({"cohort_id": 1, "is_active": 1})
   ```

2. **Data Archiving**
   - Automatic archiving of old cohort data
   - Configurable retention policies
   - Compressed storage for historical data

#### Performance Optimization
1. **Caching Strategy**
   - Redis caching for cohort configurations
   - Session-based caching for student data
   - CDN for static assets per cohort

2. **Load Balancing**
   - Cohort-based load distribution
   - Regional deployment for multi-campus support
   - Auto-scaling based on cohort activity

### Cost Considerations

#### OpenAI API Usage
- **Estimated Cost per Student**: $2-5 per complete assignment
- **Monthly Cost for 200 students**: $400-1000
- **Annual Cost for 4 cohorts (800 students)**: $1,600-4,000

#### Infrastructure Scaling
- **Database**: M10 cluster → M30 cluster for 500+ concurrent users
- **Storage**: 10GB → 100GB for audio transcripts across multiple cohorts
- **Monitoring**: Enhanced monitoring for multi-cohort performance

### Implementation Recommendations

#### Immediate (Phase 1)
1. **Start with Cohort-Aware Schema**: Implement cohort_id fields from the beginning
2. **Simple Cohort Management**: Basic cohort creation and student assignment
3. **Data Isolation**: Ensure all queries include cohort_id filtering

#### Short-term (Phase 2-3)
1. **Instructor Dashboard**: Basic progress tracking and data export
2. **Bulk Student Management**: CSV import/export with cohort assignment
3. **Configuration per Cohort**: Allow different audio settings per cohort

#### Long-term (Phase 4-6)
1. **Advanced Analytics**: Cross-cohort performance comparison
2. **Automated Archiving**: Semester-based data lifecycle management
3. **Multi-Campus Support**: Institution-level hierarchy above cohorts

### Migration Strategy for Existing Data

#### Phase 1: Preparation
1. **Backup Current Data**: Full MongoDB backup
2. **Create Default Cohort**: Migrate existing data to "DEFAULT_COHORT"
3. **Update Identifiers**: Add cohort_id to existing valid_identifiers

#### Phase 2: Schema Migration
```python
# scripts/migrate_to_multi_cohort.py
def migrate_existing_data():
    """Migrate existing physiobot data to multi-cohort structure"""
    
    # Create default cohort
    default_cohort = {
        "cohort_id": "PHYSIO_LEGACY",
        "cohort_name": "Legacy Cohort",
        "academic_year": "2024",
        "semester": "Migration",
        "is_active": True,
        "created_at": datetime.utcnow()
    }
    
    # Migrate transcripts
    db.audio_transcripts.update_many(
        {"cohort_id": {"$exists": False}},
        {"$set": {"cohort_id": "PHYSIO_LEGACY"}}
    )
    
    # Migrate identifiers
    db.valid_identifiers.update_many(
        {"cohort_id": {"$exists": False}},
        {"$set": {"cohort_id": "PHYSIO_LEGACY"}}
    )
```

This enhanced multi-cohort architecture ensures the platform can scale to support multiple classes, semesters, and even different physiotherapy programs simultaneously while maintaining proper data isolation and administrative control.