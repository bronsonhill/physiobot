# PhysioBot Instructor & Administrator Guide
## Phase 5: Enhanced Audio Interface Management

### Version 1.0 - Administrative Controls & System Management
*Last Updated: January 2024*

---

## Table of Contents

1. [Overview](#overview)
2. [Admin Interface Access](#admin-interface-access)
3. [Audio Configuration](#audio-configuration)
4. [System Monitoring](#system-monitoring)
5. [Testing & Diagnostics](#testing--diagnostics)
6. [User Management](#user-management)
7. [Performance Optimization](#performance-optimization)
8. [Troubleshooting Guide](#troubleshooting-guide)
9. [Best Practices](#best-practices)
10. [Technical Reference](#technical-reference)

---

## Overview

The Phase 5 enhanced PhysioBot platform introduces comprehensive administrative controls for managing the audio-enabled conversation system. This guide covers all aspects of system administration, from basic configuration to advanced troubleshooting.

### Key Administrative Features

- **🎛️ Audio Configuration Management**: Control voice settings, quality parameters, and conversation limits
- **📊 Real-time System Monitoring**: Track usage, performance, and system health
- **🧪 Comprehensive Testing Suite**: Built-in diagnostic and validation tools
- **👥 User Session Management**: Monitor active users and manage sessions
- **📈 Performance Analytics**: Detailed reporting and usage statistics
- **🔧 Troubleshooting Tools**: Advanced diagnostic capabilities

### Access Levels

1. **System Administrator**: Full access to all configuration and monitoring features
2. **Course Instructor**: Access to student management and basic monitoring
3. **Technical Support**: Access to diagnostics and troubleshooting tools

---

## Admin Interface Access

### Authentication

1. **Access the Admin Panel**
   - Navigate to the "Admin Configuration" page
   - This page is available to authenticated administrators only

2. **Login Process**
   - Enter the administrator password when prompted
   - Default password: `admin123` (change immediately in production)
   - Authentication status persists during the session

3. **Security Notes**
   - Change default password immediately
   - Use strong passwords in production environments
   - Consider implementing role-based access control
   - Log access attempts for security auditing

### Interface Overview

The admin interface is organized into five main tabs:

- **🎵 Audio Settings**: Configure voice and audio parameters
- **📊 System Monitoring**: Real-time system performance and usage
- **🧪 Testing Tools**: Diagnostic and validation utilities
- **👥 User Management**: Active user monitoring and session control
- **📚 Documentation**: Training materials and system documentation

---

## Audio Configuration

### Voice Settings

#### Voice Type Selection
- **Available Voices**: alloy, echo, fable, onyx, nova, shimmer
- **Recommendations**:
  - `alloy`: Balanced, professional tone (recommended for clinical settings)
  - `echo`: Clear, authoritative (good for supervisor conversations)
  - `nova`: Warm, approachable (suitable for patient interactions)

#### Speech Parameters
- **Speech Speed**: 0.25 - 4.0 (1.0 = normal speed)
  - Recommended range: 0.8 - 1.2 for educational content
  - Slower speeds (0.8-0.9) may help non-native speakers
  - Faster speeds (1.1-1.2) can improve engagement

#### Audio Quality Settings
- **Sample Rate**: 16kHz, 24kHz, or 48kHz
  - 24kHz recommended for balance of quality and bandwidth
  - 48kHz for premium audio quality (higher bandwidth requirement)
  - 16kHz for limited bandwidth environments

- **Format**: PCM16 (default and recommended)

### Conversation Detection

#### Silence Threshold
- **Range**: 0.5 - 5.0 seconds
- **Default**: 2.0 seconds
- **Guidance**:
  - Lower values (1.0-1.5s): More responsive, may cut off speakers
  - Higher values (2.5-3.0s): More tolerance for pauses, slower response

#### Volume Threshold
- **Range**: 0.01 - 1.0
- **Default**: 0.1
- **Purpose**: Minimum volume level to trigger speech detection
- **Adjustment**: Increase if background noise causes false triggers

### Conversation Limits

#### Duration Controls
- **Max Duration**: 300 - 3600 seconds (5-60 minutes)
- **Default**: 1800 seconds (30 minutes)
- **Considerations**:
  - Longer sessions may impact server resources
  - Consider student attention spans
  - Balance educational goals with technical constraints

#### Response Limits
- **Max Responses**: 10 - 200 exchanges
- **Default**: 50 responses
- **Guidance**: Adjust based on assessment complexity and course requirements

#### Auto-save Settings
- **Auto-save Interval**: 60 - 1800 seconds
- **Default**: 300 seconds (5 minutes)
- **Benefit**: Prevents data loss during long conversations

### Saving Configuration Changes

1. **Apply Changes**
   - Review all settings before saving
   - Click "💾 Save Audio Configuration"
   - System will validate settings before applying

2. **Configuration Validation**
   - Invalid settings will be rejected with specific error messages
   - All changes are validated against acceptable ranges
   - Backup of previous configuration is automatically created

3. **Reset Options**
   - "🔄 Reset to Defaults" restores factory settings
   - Confirmation dialog prevents accidental resets
   - Previous configuration can be restored from backup

---

## System Monitoring

### Dashboard Overview

The monitoring dashboard provides real-time insights into system performance and usage patterns.

#### Key Metrics

1. **Total Sessions**: Cumulative number of conversations started
2. **Active Users**: Students currently using the system (24-hour window)
3. **Average Session Duration**: Mean conversation length in minutes
4. **Success Rate**: Percentage of successfully completed conversations

#### Recent Sessions Table

- **Real-time Updates**: Automatically refreshes every 30 seconds (optional)
- **Session Details**: Timestamp, student ID, duration, exchange count, status
- **Status Indicators**:
  - "Started": Session initiated but not completed
  - "In Progress": Active conversation ongoing
  - "Completed": Successfully finished both patient and supervisor conversations

#### System Health Indicators

Monitor critical system components:

- **OpenAI API**: Connection status and response times
- **Database**: Connection health and query performance
- **Audio Service**: WebRTC functionality and audio processing status

### Performance Monitoring

#### Usage Patterns
- Track peak usage times
- Identify resource bottlenecks
- Monitor concurrent user limits
- Analyze session completion rates

#### Quality Metrics
- Audio quality scores (1-5 scale)
- Connection stability measurements
- Error rates and failure types
- User satisfaction indicators

### Alerts and Notifications

#### Automatic Monitoring
- System will alert on critical issues
- Performance degradation warnings
- Resource utilization thresholds
- Connectivity problems

#### Manual Refresh
- Use "🔄 Refresh Data" for immediate updates
- Toggle "Auto-refresh (30s)" for continuous monitoring
- Export data for detailed analysis

---

## Testing & Diagnostics

### Audio Test Suite

#### Microphone Testing
- **Function**: Verify microphone access and functionality
- **Process**: 
  1. Click "🎤 Test Microphone Access"
  2. System checks browser permissions
  3. Tests audio input device availability
  4. Reports sample rate and device information

#### Audio Playback Testing
- **Function**: Validate audio output capabilities
- **Process**:
  1. Click "🔊 Test Audio Playback"
  2. System tests speaker/headphone output
  3. Measures volume levels and latency
  4. Confirms audio context availability

#### OpenAI Connection Testing
- **Function**: Verify Realtime API connectivity
- **Process**:
  1. Click "🌐 Test OpenAI Connection"
  2. Establishes WebSocket connection
  3. Tests API response times
  4. Validates authentication and rate limits

#### Full System Test
- **Function**: Comprehensive system validation
- **Process**:
  1. Click "📊 Run Full System Test"
  2. Progress bar shows testing stages
  3. Tests all major components sequentially
  4. Provides detailed results summary

### Diagnostic Tools

#### Browser Compatibility Check
- **Detected Information**: Browser type and version
- **Compatibility Status**: WebRTC, Microphone API, WebSocket support
- **Recommendations**: Browser-specific optimization suggestions

#### Performance Metrics
- **Response Times**: Average system response measurements
- **Connection Quality**: Network stability assessments
- **Audio Quality Score**: Overall audio experience rating
- **Success Rate**: System reliability percentage

#### Log Monitoring
- **Real-time Logs**: Recent system events and activities
- **Error Tracking**: Color-coded log entries (green=info, yellow=warning, red=error)
- **Log Levels**: Information, warnings, and error messages
- **Historical Data**: Scrollable log viewer with timestamps

### Troubleshooting Workflows

#### Connection Issues
1. Run OpenAI Connection Test
2. Check system health indicators
3. Verify API key and rate limits
4. Monitor network connectivity

#### Audio Problems
1. Test microphone and playback
2. Check browser compatibility
3. Verify permissions and settings
4. Assess audio quality metrics

#### Performance Issues
1. Monitor system resource usage
2. Check concurrent user counts
3. Analyze response time trends
4. Review error logs for patterns

---

## User Management

### Active User Monitoring

#### Current Sessions
- **Real-time Tracking**: See who's currently using the system
- **Session Status**: In Patient Chat, In Supervisor Chat, or Idle
- **Duration Tracking**: How long each user has been active
- **Quick Actions**: View details or force disconnect if necessary

#### Usage Statistics
- **Daily Metrics**: Today's session count and unique users
- **Weekly Trends**: Seven-day usage patterns
- **User Engagement**: Average session times and completion rates
- **Peak Usage**: Identification of high-traffic periods

### Session Management

#### Individual User Controls
- **Session Details**: Deep dive into specific user's conversation data
- **Force Disconnect**: Emergency option to terminate problematic sessions
- **Progress Monitoring**: Track completion of conversation phases

#### Bulk Operations
Available bulk actions for user management:

1. **Export All Sessions**: Generate comprehensive usage reports
2. **Clear Old Sessions**: Remove outdated session data
3. **Generate Usage Report**: Create formatted analytics reports
4. **Reset User Progress**: Clear completion status for specific users

### User Support Tools

#### Session Recovery
- Help users reconnect after technical issues
- Restore interrupted conversations
- Provide fallback options for audio problems

#### Progress Tracking
- Monitor individual student progress
- Identify students who may need additional support
- Track completion rates across cohorts

---

## Performance Optimization

### System Configuration

#### Resource Management
- **Concurrent User Limits**: Adjust based on server capacity
- **Session Timeouts**: Optimize for user experience and resource conservation
- **Bandwidth Optimization**: Configure audio quality vs. bandwidth trade-offs

#### Database Optimization
- **Connection Pooling**: Manage database connections efficiently
- **Query Optimization**: Monitor and optimize database performance
- **Data Archiving**: Implement strategies for managing historical data

### Audio Quality Optimization

#### Bandwidth Considerations
- **High Bandwidth**: Use 48kHz sample rate for premium quality
- **Medium Bandwidth**: 24kHz provides good balance
- **Low Bandwidth**: 16kHz for restricted connections

#### Latency Reduction
- **Server Location**: Consider geographic proximity to users
- **CDN Usage**: Implement content delivery networks for static assets
- **Connection Optimization**: Use WebSocket keep-alives

### Monitoring and Alerting

#### Performance Thresholds
- Set alerts for response time degradation
- Monitor error rates and failure patterns
- Track resource utilization trends

#### Capacity Planning
- Analyze usage growth patterns
- Plan for peak usage periods
- Scale resources proactively

---

## Troubleshooting Guide

### Common Issues and Solutions

#### Audio Not Working
**Symptoms**: Students report no audio input/output
**Diagnosis**:
1. Check browser compatibility matrix
2. Verify microphone permissions
3. Test with admin diagnostic tools

**Solutions**:
- Guide users through permission setup
- Recommend compatible browsers
- Provide text input fallback

#### Poor Audio Quality
**Symptoms**: Distorted, unclear, or choppy audio
**Diagnosis**:
1. Check connection quality metrics
2. Review audio quality settings
3. Assess network bandwidth

**Solutions**:
- Adjust sample rate settings
- Recommend audio equipment upgrades
- Optimize network configuration

#### Connection Timeouts
**Symptoms**: Frequent disconnections, failed connections
**Diagnosis**:
1. Run OpenAI connection tests
2. Check API rate limits
3. Monitor network stability

**Solutions**:
- Increase timeout values
- Implement retry logic
- Verify API key validity

#### High Resource Usage
**Symptoms**: Slow performance, server overload
**Diagnosis**:
1. Monitor concurrent user counts
2. Check database performance
3. Analyze memory and CPU usage

**Solutions**:
- Implement user limits
- Optimize database queries
- Scale server resources

### Emergency Procedures

#### System Outage Response
1. **Immediate Assessment**
   - Check system health dashboard
   - Identify affected components
   - Estimate impact scope

2. **User Communication**
   - Notify active users of issues
   - Provide status updates
   - Offer alternative access methods

3. **Resolution Process**
   - Follow escalation procedures
   - Document issue details
   - Implement fixes systematically

#### Data Recovery
- **Backup Verification**: Ensure backup systems are operational
- **Recovery Procedures**: Follow documented recovery protocols
- **Data Integrity**: Validate recovered data completeness

---

## Best Practices

### Configuration Management

#### Change Control
- **Documentation**: Record all configuration changes
- **Testing**: Validate changes in non-production environment first
- **Rollback Plans**: Maintain ability to revert changes quickly
- **Approval Process**: Implement change approval workflows

#### Security Practices
- **Password Management**: Use strong, unique passwords
- **Access Control**: Implement least-privilege access principles
- **Audit Logging**: Track administrative actions
- **Regular Updates**: Keep systems and dependencies current

### Monitoring and Maintenance

#### Regular Monitoring
- **Daily Checks**: Review system health and performance metrics
- **Weekly Analysis**: Analyze usage trends and identify issues
- **Monthly Reviews**: Comprehensive system performance evaluation
- **Quarterly Planning**: Capacity planning and system optimization

#### Preventive Maintenance
- **Database Maintenance**: Regular cleanup and optimization
- **Log Rotation**: Manage log file sizes and retention
- **Performance Tuning**: Ongoing optimization based on usage patterns
- **Security Updates**: Apply patches and updates promptly

### User Support

#### Proactive Support
- **User Training**: Provide comprehensive user guides and training
- **System Status**: Maintain transparent system status communication
- **Feedback Collection**: Actively gather user feedback for improvements

#### Reactive Support
- **Issue Tracking**: Implement ticket system for user issues
- **Response Times**: Establish and maintain response time standards
- **Escalation Procedures**: Clear escalation paths for complex issues

---

## Technical Reference

### Configuration File Structure

The system uses `config.yaml` for configuration management:

```yaml
audio_settings:
  voice_type: "alloy"
  speech_speed: 1.0
  conversation_detection:
    silence_threshold: 2.0
    volume_threshold: 0.1
  quality_settings:
    sample_rate: 24000
    format: "pcm16"

conversation_settings:
  max_duration: 1800
  max_responses: 50
  auto_save_interval: 300
  connection_timeout: 30

ui_settings:
  show_live_transcript: true
  enable_audio_visualization: true

database_settings:
  database_name: "physiobot-realtime"
  collections:
    cohorts: "cohorts"
    valid_identifiers: "valid_identifiers"
    audio_transcripts: "audio_transcripts"
    instructors: "instructors"
```

### API Endpoints

#### Configuration Management
- `GET /api/config` - Retrieve current configuration
- `POST /api/config` - Update configuration settings
- `POST /api/config/reset` - Reset to default configuration
- `GET /api/config/validate` - Validate configuration

#### Monitoring
- `GET /api/stats` - System statistics
- `GET /api/health` - System health check
- `GET /api/sessions` - Recent session data
- `GET /api/users/active` - Active user list

#### Testing
- `POST /api/test/audio` - Run audio tests
- `POST /api/test/connection` - Test OpenAI connection
- `POST /api/test/system` - Full system test

### Database Schema

#### Audio Transcripts Collection
```javascript
{
  _id: ObjectId,
  timestamp: DateTime,
  identifier: String,
  cohort_id: String,
  session_metadata: {
    duration_seconds: Number,
    audio_quality_score: Number,
    connection_stability: Number
  },
  patient_conversation: {
    transcript_segments: Array,
    conversation_metrics: Object
  },
  supervisor_conversation: {
    transcript_segments: Array,
    conversation_metrics: Object
  }
}
```

### Environment Variables

#### Required Settings
- `OPENAI_API_KEY`: OpenAI API authentication key
- `MONGODB_URI`: MongoDB connection string
- `ADMIN_PASSWORD`: Administrator interface password

#### Optional Settings
- `LOG_LEVEL`: Logging verbosity (DEBUG, INFO, WARNING, ERROR)
- `MAX_CONCURRENT_USERS`: Maximum simultaneous users
- `SESSION_TIMEOUT`: Session timeout in seconds

### Error Codes and Messages

#### Common Error Codes
- `AUDIO_001`: Microphone permission denied
- `AUDIO_002`: Audio device not available
- `CONN_001`: OpenAI API connection failed
- `CONN_002`: Database connection timeout
- `AUTH_001`: Invalid admin credentials
- `CONFIG_001`: Invalid configuration parameters

---

## Appendix

### Keyboard Shortcuts (Admin Interface)
- `Ctrl+R`: Refresh current tab data
- `Ctrl+T`: Run audio test
- `Ctrl+S`: Save configuration
- `Esc`: Close modal dialogs

### Supported Browsers
- Chrome 90+ (Recommended)
- Firefox 88+
- Safari 14+
- Edge 90+

### Resource Requirements

#### Minimum Server Specifications
- CPU: 2 cores, 2.4GHz
- RAM: 4GB
- Storage: 20GB SSD
- Bandwidth: 10Mbps

#### Recommended Server Specifications
- CPU: 4 cores, 3.0GHz
- RAM: 8GB
- Storage: 50GB SSD
- Bandwidth: 100Mbps

### Contact Information

#### Technical Support
- Email: support@physiobot.edu
- Phone: +1-555-PHYSIO
- Hours: 8 AM - 6 PM EST, Monday-Friday

#### Emergency Support
- 24/7 Emergency Line: +1-555-URGENT
- Slack Channel: #physiobot-support
- Email: emergency@physiobot.edu

---

*This guide is regularly updated to reflect system enhancements and best practices. For the latest version, check the system documentation portal.*

**PhysioBot Instructor & Administrator Guide v1.0**  
*Phase 5 Implementation - January 2024*