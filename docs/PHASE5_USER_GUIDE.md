# PhysioBot Phase 5 User Guide

## Overview

Phase 5 of PhysioBot introduces significant UI/UX enhancements, comprehensive configuration tools, and advanced testing capabilities. This guide covers all new features and how to use them effectively.

## Table of Contents

1. [Enhanced User Interface](#enhanced-user-interface)
2. [Audio Preferences & Setup](#audio-preferences--setup)
3. [Admin Configuration Panel](#admin-configuration-panel)
4. [Testing & Diagnostics](#testing--diagnostics)
5. [Troubleshooting Guide](#troubleshooting-guide)
6. [Best Practices](#best-practices)

---

## Enhanced User Interface

### 🎨 Modern Audio Conversation Interface

The Phase 5 interface provides a streamlined, modern experience for audio conversations:

#### Key Features:
- **Real-time Status Indicators**: Clear visual feedback showing conversation state
- **Enhanced Audio Visualization**: Live volume meters and frequency displays
- **Improved Control Layout**: Intuitive button placement and sizing
- **Responsive Design**: Works seamlessly across different screen sizes

#### Navigation:
```
Home Page → Audio Preferences → Patient Conversation → Supervisor Conversation
```

#### Visual Indicators:
- 🔵 **Blue**: Ready/Idle state
- 🟡 **Yellow**: Processing/Connecting
- 🟢 **Green**: Active recording/responding
- 🔴 **Red**: Recording in progress
- ❌ **Red X**: Error state

### 📱 Accessibility Features

Phase 5 includes comprehensive accessibility improvements:

- **High Contrast Mode**: Enhanced visibility for users with visual impairments
- **Large Control Buttons**: Easier interaction for motor accessibility
- **Keyboard Shortcuts**: Full keyboard navigation support
- **Screen Reader Support**: Compatible with assistive technologies

---

## Audio Preferences & Setup

### 🎧 Accessing Audio Preferences

Navigate to the **Audio Preferences** page from the sidebar or main menu.

#### Required Before Use:
- Valid student identifier entered on Home page
- Working microphone and speakers/headphones
- Modern web browser with JavaScript enabled

### 🎵 Audio Settings Tab

#### Output Settings:
- **Output Volume**: Adjust AI response volume (0.0 - 2.0)
- **Preferred Speech Speed**: Control AI speaking rate (0.5 - 2.0x)
- **Voice Preference**: Choose from available voice styles

#### Input Settings:
- **Microphone Sensitivity**: Adjust for your recording environment
- **Auto-record**: Automatically start recording after AI responses
- **Push-to-talk**: Hold button to record instead of click to toggle

#### Connection Settings:
- **Connection Quality**: Auto, High Quality, Balanced, or Low Bandwidth
- **Audio Visualization**: Enable/disable real-time audio meters
- **Live Transcript**: Show/hide conversation text

#### Accessibility Options:
- **Large Control Buttons**: Increase button size for easier access
- **High Contrast Mode**: Improve visibility with high contrast colors
- **Keyboard Shortcuts**: Enable spacebar recording and Enter to send

### 🧪 Audio Test Tab

#### Pre-Conversation Testing:

1. **Microphone Test**:
   - Click "Start Microphone Test"
   - Speak clearly into your microphone
   - Check volume levels and quality feedback

2. **Speaker Test**:
   - Click "Test Speakers/Headphones"
   - Confirm you can hear the test audio clearly
   - Adjust volume if needed

3. **Connection Test**:
   - Click "Test Connection Quality"
   - Review latency, jitter, and bandwidth metrics
   - Ensure stable connection for best experience

4. **End-to-End Test**:
   - Click "Full Audio Pipeline Test"
   - Comprehensive test of all audio components
   - Verify complete system functionality

### 🔧 Troubleshooting Tab

Common issues and solutions are provided for:
- Microphone not working
- No audio output
- Poor audio quality
- Connection issues

### 📖 Help Guide Tab

Comprehensive guidance including:
- Quick start instructions
- Conversation tips
- Keyboard shortcuts
- FAQ section

---

## Admin Configuration Panel

### 🔐 Admin Access

Admin features require authentication:
1. Navigate to **Admin Configuration** page
2. Enter admin access key (provided by system administrator)
3. Access comprehensive system management tools

### 🎵 Audio Settings Management

#### Voice & Speech Configuration:
- **Voice Type**: Select from OpenAI voice options (alloy, echo, fable, onyx, nova, shimmer)
- **Speech Speed**: Global speed setting (0.25 - 4.0x)
- **Conversation Detection**: Silence threshold and volume trigger levels
- **Quality Settings**: Sample rate and audio format configuration

#### Testing Tools:
- **Voice Settings Test**: Validate voice configuration
- **Audio Quality Test**: Measure latency, jitter, and quality metrics

### 👥 Cohort Management

#### Creating Cohorts:
1. Enter unique Cohort ID (e.g., "PHYSIO2024_SEM1")
2. Provide descriptive cohort name
3. Set academic year and semester
4. Add instructor email addresses (one per line)
5. Click "Create Cohort"

#### Managing Existing Cohorts:
- **View Statistics**: Student counts, completion rates, average scores
- **Configure Settings**: Cohort-specific audio and conversation settings
- **Archive Cohorts**: Safely archive completed cohorts

### 🔧 System Settings

#### Conversation Configuration:
- **Max Duration**: Maximum conversation time (seconds)
- **Max Responses**: Limit on conversation exchanges
- **Auto-save Interval**: Frequency of automatic saves
- **Connection Timeout**: API timeout settings

#### UI Configuration:
- **Live Transcript**: Enable/disable real-time transcription
- **Audio Visualization**: System-wide visualization settings
- **Theme**: Light, dark, or auto theme selection

#### Environment Settings:
- **Debug Logging**: Enable detailed logging for troubleshooting
- **Log Level**: Set minimum log level (DEBUG, INFO, WARNING, ERROR)

### 📊 Analytics & Monitoring

#### Real-time Metrics:
- Active session count
- Total conversation statistics
- Average response times
- System uptime monitoring

#### Usage Analytics:
- Daily conversation trends
- User engagement metrics
- Performance graphs and charts

#### System Alerts:
- Real-time error notifications
- Performance warnings
- System status updates

### 🧪 Testing Tools

#### Browser Compatibility:
- Automated browser feature detection
- Compatibility matrix for major browsers
- Feature support verification

#### Audio Quality Testing:
- Microphone access verification
- Audio capture/playback testing
- WebRTC support validation
- Echo cancellation and noise suppression checks

#### Performance Testing:
- System resource monitoring
- API response time measurement
- Memory and CPU usage tracking

#### Load Testing:
- Concurrent user simulation
- Scalability testing
- Performance bottleneck identification

---

## Testing & Diagnostics

### 🔄 Automated Testing Suite

Phase 5 includes comprehensive automated testing:

#### Test Categories:
1. **Browser Compatibility**: Multi-browser feature support
2. **Audio Pipeline**: Complete audio processing chain
3. **Network Connectivity**: API and WebSocket connections
4. **Performance**: Resource usage and response times
5. **Error Handling**: Recovery and fallback mechanisms
6. **Load Testing**: Concurrent user scenarios

#### Running Tests:

```bash
# Command line execution
python tests/test_audio_compatibility.py

# Streamlit interface
# Navigate to Admin Configuration → Testing Tools
```

#### Test Reports:
- Detailed JSON reports with timestamps
- Pass/fail status for each test
- Performance metrics and recommendations
- Historical test result tracking

### 📊 Performance Monitoring

#### Key Metrics:
- **Latency**: Round-trip audio processing time
- **Jitter**: Variation in response times
- **Packet Loss**: Network reliability measure
- **Quality Score**: Overall audio experience rating

#### Monitoring Tools:
- Real-time dashboard in admin panel
- Automated alerting for issues
- Historical performance tracking
- Comparison across different configurations

---

## Troubleshooting Guide

### 🎤 Audio Issues

#### Microphone Problems:
1. **Check browser permissions**: Ensure microphone access is granted
2. **Test with other applications**: Verify microphone works elsewhere
3. **Try different browser**: Chrome recommended for best compatibility
4. **Check system settings**: Ensure correct microphone is selected

#### No Audio Output:
1. **Volume settings**: Check both browser and system volume
2. **Output device**: Verify correct speakers/headphones selected
3. **Browser tab**: Ensure audio isn't muted in browser
4. **Hardware**: Test with different audio output device

#### Poor Audio Quality:
1. **Internet connection**: Test bandwidth and stability
2. **Close other applications**: Free up network resources
3. **Adjust quality settings**: Lower quality for poor connections
4. **Environmental factors**: Reduce background noise

### 🌐 Connection Issues

#### WebSocket Problems:
1. **Refresh page**: Simple restart often resolves issues
2. **Check internet**: Verify stable connection
3. **Disable VPN**: May interfere with WebSocket connections
4. **Clear cache**: Browser cache clearing can help

#### API Connectivity:
1. **Check system status**: Verify OpenAI API availability
2. **Retry connection**: Wait and attempt reconnection
3. **Check credentials**: Ensure valid API keys
4. **Network restrictions**: Corporate firewalls may block connections

### 🔧 Browser Compatibility

#### Recommended Browsers:
- **Chrome 80+**: Full feature support, best performance
- **Firefox 75+**: Good compatibility, solid alternative
- **Edge 80+**: Microsoft's modern browser, good support
- **Safari 13+**: Limited features, desktop only

#### Unsupported:
- Internet Explorer (all versions)
- Mobile browsers (limited support)
- Very old browser versions

### 📱 Mobile Considerations

#### Limitations:
- Limited audio processing capabilities
- Reduced feature set
- Battery usage concerns
- Network stability issues

#### Recommendations:
- Use desktop/laptop when possible
- Ensure strong WiFi connection
- Close other apps during use
- Use headphones for better audio quality

---

## Best Practices

### 🎯 For Students

#### Before Starting:
1. **Test your setup**: Run audio tests in preferences
2. **Find quiet space**: Minimize background noise
3. **Use headphones**: Prevent audio feedback
4. **Check connection**: Ensure stable internet

#### During Conversation:
1. **Speak clearly**: Normal pace and volume
2. **Wait for responses**: Don't interrupt AI responses
3. **Use natural language**: Conversational, not robotic
4. **Take your time**: No rush, focus on quality

#### If Problems Occur:
1. **Stay calm**: Technical issues happen
2. **Try text backup**: Use text input if audio fails
3. **Refresh if needed**: Page refresh can resolve issues
4. **Contact support**: Instructors can provide assistance

### 👨‍🏫 For Instructors

#### Setup Phase:
1. **Review system requirements**: Ensure student computers meet specs
2. **Provide clear instructions**: Share user guide with students
3. **Test before class**: Verify system functionality
4. **Have backup plan**: Alternative activities if technical issues

#### During Class:
1. **Monitor dashboard**: Watch for system alerts
2. **Provide technical support**: Help students with basic issues
3. **Document problems**: Report persistent issues to administrators
4. **Encourage students**: Technical difficulties are learning opportunities

#### After Class:
1. **Review analytics**: Check participation and completion rates
2. **Gather feedback**: Student experience surveys
3. **Report issues**: Systematic problem reporting
4. **Plan improvements**: Continuous enhancement based on feedback

### 🔧 For Administrators

#### Regular Maintenance:
1. **Run automated tests**: Weekly compatibility checks
2. **Monitor performance**: Track key metrics
3. **Update configurations**: Adjust settings based on usage
4. **Backup data**: Regular system backups

#### Scaling Considerations:
1. **Monitor resource usage**: CPU, memory, bandwidth
2. **Plan for growth**: Anticipate increased usage
3. **Optimize settings**: Adjust for performance vs. quality balance
4. **Update documentation**: Keep guides current

#### Security Best Practices:
1. **Regular updates**: Keep all components current
2. **Access control**: Limit admin access appropriately
3. **Data privacy**: Ensure student data protection
4. **Audit logs**: Monitor system access and changes

---

## Support and Resources

### 📞 Getting Help

#### For Students:
- Contact your course instructor
- Check troubleshooting guide
- Use built-in help features
- Report technical issues through proper channels

#### For Instructors:
- System administrator contact
- Technical documentation
- User forums and community
- Direct support channels

#### For Administrators:
- Technical support team
- System documentation
- Configuration guides
- Update notifications

### 📚 Additional Resources

- **Technical Documentation**: Detailed system architecture
- **API References**: Developer documentation
- **Configuration Examples**: Sample setups and best practices
- **Training Materials**: Video tutorials and guides

### 🔄 Updates and Maintenance

#### Regular Updates:
- Feature enhancements
- Security patches
- Performance improvements
- Bug fixes

#### Maintenance Windows:
- Scheduled downtime notifications
- Update procedures
- Rollback plans
- Communication protocols

---

## Conclusion

Phase 5 represents a significant advancement in PhysioBot's capabilities, providing enhanced user experience, comprehensive configuration options, and robust testing tools. By following this guide and implementing the best practices outlined, users can maximize the benefits of the audio conversation system while ensuring reliable, high-quality educational experiences.

For additional support or questions not covered in this guide, please contact your system administrator or refer to the technical documentation.

---

*Last Updated: Phase 5 Implementation*
*Version: 1.0*
*Contact: PhysioBot Support Team*