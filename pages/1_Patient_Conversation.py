import streamlit as st
import json
import logging
from datetime import datetime, timezone
from openai import OpenAI

from Home import setup
from utils.mongodb_realtime import log_audio_transcript

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Patient Conversation - PhysioBot",
    page_icon="🗣️",
    layout="wide"
)

# Check user authentication
if not bool(st.session_state.get("user_identifier", "").strip()):
    st.error("Please enter your identifier on the Home page before starting the conversation.")
    st.stop()

# Check if patient conversation is already finished
if st.session_state.get("p_conversation_finished", False):
    st.success("✅ Patient conversation completed! You can now proceed to the Supervisor conversation.")
    st.stop()

# Setup OpenAI client
client = setup()

def get_patient_instructions():
    """Get patient instructions for the conversation"""
    try:
        with open("./prompts/audio_patient_prompt.txt", "r") as file:
            return file.read()
    except FileNotFoundError:
        # Fallback to regular prompt with audio adaptations
        patient_instructions = st.session_state.get("patient_prompt", "")
        return f"""{patient_instructions}

IMPORTANT AUDIO CONVERSATION GUIDELINES:
- You are having a spoken conversation, not a text chat
- Speak naturally and conversationally
- Keep responses concise and clear (2-3 sentences max)
- Use verbal acknowledgments like "mm-hmm", "I see", "okay"
- If you don't understand something, ask for clarification naturally
- Express emotions through your tone of voice appropriately
- Remember this is a learning experience for a physiotherapy student
- Be patient and encouraging while staying in character
- Stay focused on the physiotherapy consultation scenario
"""

def get_js_code():
    """Return the JavaScript code for WebRTC implementation"""
    instructions = get_patient_instructions()
    api_key = st.secrets["OPENAI_API_KEY"]
    
    return f"""
        document.addEventListener('DOMContentLoaded', function() {{
            console.log("Patient conversation script loaded");

            // Add debug logging for audio context
            navigator.mediaDevices.getUserMedia({{ audio: true }})
                .then(() => console.log("Microphone permission granted"))
                .catch(err => console.error("Microphone error:", err));

            const startButton = document.getElementById('startButton');
            const stopButton = document.getElementById('stopButton');
            const finishButton = document.getElementById('finishButton');
            const statusDiv = document.getElementById('status');
            const errorDiv = document.getElementById('error');
            const chatContainer = document.getElementById('chat-container');
            const chatContent = document.getElementById('chat-content');
            const emptyState = document.getElementById('empty-state');

            let peerConnection = null;
            let audioStream = null;
            let dataChannel = null;
            let conversationActive = false;
            let conversationSegments = [];
            let autoScrollEnabled = true;
            let scrollTimeout = null;

            const INITIAL_INSTRUCTIONS = {json.dumps(instructions)};
            const API_KEY = "{api_key}";

            // Add event listeners
            startButton.addEventListener('click', init);
            stopButton.addEventListener('click', stopRecording);
            finishButton.addEventListener('click', finishConversation);
            
            // Add scroll event listener for smart scrolling
            chatContainer.addEventListener('scroll', handleChatScroll);
            
            // Scroll handling functions
            function handleChatScroll() {{
                const container = chatContainer;
                const isScrolledToBottom = container.scrollHeight - container.scrollTop <= container.clientHeight + 50;
                
                // Enable auto-scroll when user scrolls to bottom, disable when scrolling up
                autoScrollEnabled = isScrolledToBottom;
                
                // Clear any pending scroll timeout
                if (scrollTimeout) {{
                    clearTimeout(scrollTimeout);
                }}
                
                // Show/hide scroll indicator after a delay
                scrollTimeout = setTimeout(() => {{
                    updateScrollIndicator();
                }}, 100);
            }}
            
            function smartScrollToBottom(force = false) {{
                if (autoScrollEnabled || force) {{
                    // Small delay to ensure DOM is updated
                    setTimeout(() => {{
                        chatContainer.scrollTo({{
                            top: chatContainer.scrollHeight,
                            behavior: autoScrollEnabled ? 'smooth' : 'auto'
                        }});
                    }}, 10);
                }}
            }}
            
            function updateScrollIndicator() {{
                const indicator = document.getElementById('scroll-indicator');
                if (indicator) {{
                    // Show indicator if user has scrolled up and there are messages
                    const hasMessages = chatContent.children.length > 1 || 
                                      (chatContent.children.length === 1 && emptyState && emptyState.style.display === 'none');
                    if (!autoScrollEnabled && hasMessages) {{
                        indicator.style.display = 'block';
                    }} else {{
                        indicator.style.display = 'none';
                    }}
                }}
            }}
            
            // Make smartScrollToBottom available globally for the button click
            window.smartScrollToBottom = smartScrollToBottom;
            
            // Initialize scroll behavior
            setTimeout(() => {{
                updateScrollIndicator();
            }}, 100);

            async function init() {{
                startButton.disabled = true;
                try {{
                    updateStatus('Initializing...');

                    // Connect directly to OpenAI's API
                    peerConnection = new RTCPeerConnection();
                    await setupAudio();
                    setupDataChannel();

                    const offer = await peerConnection.createOffer();
                    await peerConnection.setLocalDescription(offer);

                    const sdpResponse = await fetch(`https://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-10-01`, {{
                        method: "POST",
                        body: offer.sdp,
                        headers: {{
                            Authorization: `Bearer ${{API_KEY}}`,
                            "Content-Type": "application/sdp",
                            "OpenAI-Beta": "realtime=v1"
                        }},
                    }});

                    if (!sdpResponse.ok) {{
                        throw new Error(`OpenAI API error: ${{sdpResponse.status}}`);
                    }}

                    const answer = {{
                        type: "answer",
                        sdp: await sdpResponse.text(),
                    }};
                    await peerConnection.setRemoteDescription(answer);

                    conversationActive = true;
                    updateStatus('🟢 Connected - Ready to talk with your patient');
                    stopButton.disabled = false;
                    finishButton.disabled = false;
                    hideError();

                }} catch (error) {{
                    startButton.disabled = false;
                    stopButton.disabled = true;
                    finishButton.disabled = true;
                    showError('Error: ' + error.message);
                    console.error('Initialization error:', error);
                    updateStatus('❌ Failed to connect');
                }}
            }}

            async function setupAudio() {{
                try {{
                    const audioEl = document.createElement("audio");
                    audioEl.autoplay = true;
                    document.body.appendChild(audioEl);

                    audioStream = await navigator.mediaDevices.getUserMedia({{
                        audio: {{
                            echoCancellation: true,
                            noiseSuppression: true,
                            sampleRate: 48000,
                            channelCount: 1
                        }}
                    }});

                    peerConnection.ontrack = (event) => {{
                        console.log("Received audio track");
                        audioEl.srcObject = event.streams[0];
                    }};

                    audioStream.getTracks().forEach(track => {{
                        peerConnection.addTrack(track, audioStream);
                    }});

                    console.log("Audio setup completed");
                }} catch (error) {{
                    console.error("Error setting up audio:", error);
                    throw error;
                }}
            }}

            function setupDataChannel() {{
                dataChannel = peerConnection.createDataChannel("oai-events");
                dataChannel.onopen = onDataChannelOpen;
                dataChannel.onmessage = handleMessage;
                dataChannel.onerror = (error) => {{
                    console.error("DataChannel error:", error);
                    showError("DataChannel error: " + error.message);
                }};
                console.log("DataChannel setup completed");
            }}

            function handleMessage(event) {{
                try {{
                    const message = JSON.parse(event.data);
                    console.log('Received message:', message);

                    switch (message.type) {{
                        case "response.done":
                            handleTranscript(message);
                            break;
                        case "response.audio.delta":
                            handleAudioDelta(message);
                            break;
                        case "input_audio_buffer.speech_started":
                            console.log("Speech started");
                            updateStatus("🔴 Listening...");
                            createUserMessageContainer();
                            break;
                        case "input_audio_buffer.speech_ended":
                            console.log("Speech ended");
                            updateStatus("🟡 Processing...");
                            break;
                        case "conversation.item.input_audio_transcription.completed":
                            handleUserTranscript(message);
                            break;
                        case "response.audio.done":
                            updateStatus("🟢 Ready to talk with your patient");
                            break;
                        case "error":
                            console.error("Error from API:", message.error);
                            showError(message.error.message);
                            break;
                        default:
                            console.log('Message type:', message.type);
                    }}
                }} catch (error) {{
                    console.error('Error processing message:', error);
                    showError('Error processing message: ' + error.message);
                }}
            }}

            let currentUserMessage = null;

            function createUserMessageContainer() {{
                // Hide empty state if it's visible
                if (emptyState) {{
                    emptyState.style.display = 'none';
                }}
                
                currentUserMessage = document.createElement('div');
                currentUserMessage.className = 'message user-message';

                const label = document.createElement('div');
                label.className = 'message-label';
                label.textContent = '🧑‍⚕️ You';

                const content = document.createElement('div');
                content.className = 'message-content';
                content.textContent = 'Speaking...';

                currentUserMessage.appendChild(label);
                currentUserMessage.appendChild(content);
                chatContent.appendChild(currentUserMessage);
                smartScrollToBottom();
            }}

            function handleUserTranscript(message) {{
                if (currentUserMessage && message.transcript) {{
                    const content = currentUserMessage.querySelector('.message-content');
                    content.textContent = message.transcript;
                    
                    // Add to conversation segments
                    conversationSegments.push({{
                        timestamp: new Date().toISOString(),
                        speaker: 'user',
                        text: message.transcript
                    }});
                    
                    smartScrollToBottom();
                }}
            }}

            function handleAudioDelta(message) {{
                if (message.delta) {{
                    console.log("Received audio data");
                }}
            }}

            function handleTranscript(message) {{
                if (message.response?.output?.[0]?.content?.[0]?.transcript) {{
                    const transcript = message.response.output[0].content[0].transcript;

                    // Hide empty state if it's visible
                    if (emptyState) {{
                        emptyState.style.display = 'none';
                    }}

                    const botMessage = document.createElement('div');
                    botMessage.className = 'message bot-message';

                    const label = document.createElement('div');
                    label.className = 'message-label';
                    label.textContent = '🤒 Patient';

                    const content = document.createElement('div');
                    content.className = 'message-content';
                    content.textContent = transcript;

                    botMessage.appendChild(label);
                    botMessage.appendChild(content);
                    chatContent.appendChild(botMessage);
                    smartScrollToBottom();
                    
                    // Add to conversation segments
                    conversationSegments.push({{
                        timestamp: new Date().toISOString(),
                        speaker: 'assistant',
                        text: transcript
                    }});
                }}
            }}

            function sendSessionUpdate() {{
                const sessionUpdateEvent = {{
                    "type": "session.update",
                    "session": {{
                        "instructions": INITIAL_INSTRUCTIONS,
                        "modalities": ["text", "audio"],
                        "voice": "alloy",
                        "input_audio_format": "pcm16",
                        "output_audio_format": "pcm16",
                        "input_audio_transcription": {{
                            "model": "whisper-1",
                        }},
                        "turn_detection": {{
                            "type": "server_vad",
                            "threshold": 0.5,
                            "prefix_padding_ms": 300,
                            "silence_duration_ms": 800,
                        }}
                    }}
                }};
                sendMessage(sessionUpdateEvent);
            }}

            function sendMessage(message) {{
                if (dataChannel?.readyState === "open") {{
                    dataChannel.send(JSON.stringify(message));
                    console.log('Sent message:', message);
                }}
            }}

            function onDataChannelOpen() {{
                sendSessionUpdate();
                sendResponseCreate();
            }}

            function sendResponseCreate() {{
                sendMessage({{ "type": "response.create" }});
            }}

            function stopRecording() {{
                if (peerConnection) {{
                    peerConnection.close();
                    peerConnection = null;
                }}
                if (audioStream) {{
                    audioStream.getTracks().forEach(track => track.stop());
                    audioStream = null;
                }}
                if (dataChannel) {{
                    dataChannel.close();
                    dataChannel = null;
                }}
                conversationActive = false;
                startButton.disabled = false;
                stopButton.disabled = true;
                finishButton.disabled = true;
                updateStatus('Conversation ended');
            }}

            function finishConversation() {{
                console.log("=== FINISH CONVERSATION CALLED ===");
                
                // Stop the conversation
                stopRecording();
                console.log("Recording stopped");
                
                // Save conversation data
                if (conversationSegments.length > 0) {{
                    console.log(`Saving ${{conversationSegments.length}} conversation segments`);
                    
                    const transcriptData = {{
                        transcript_segments: conversationSegments,
                        session_summary: {{
                            duration_seconds: 0,
                            total_exchanges: conversationSegments.length
                        }},
                        conversation_metrics: {{
                            total_exchanges: conversationSegments.length,
                            user_segments: conversationSegments.filter(s => s.speaker === 'user').length,
                            assistant_segments: conversationSegments.filter(s => s.speaker === 'assistant').length
                        }}
                    }};
                    
                    console.log("Transcript data prepared:", transcriptData);
                    
                    // Send completion signal to Streamlit
                    console.log("Sending completion signal to parent window...");
                    window.parent.postMessage({{
                        type: 'conversation_complete',
                        data: transcriptData
                    }}, '*');
                    
                    console.log("Completion signal sent");
                    updateStatus('✅ Conversation completed and saved!');
                }} else {{
                    console.log("No conversation segments to save");
                    updateStatus('No conversation to save');
                }}
            }}

            function updateStatus(message) {{
                statusDiv.textContent = message;
            }}

            function showError(message) {{
                errorDiv.style.display = 'block';
                errorDiv.textContent = message;
            }}

            function hideError() {{
                errorDiv.style.display = 'none';
            }}
        }});
    """

def get_webrtc_html():
    """Generate the HTML for WebRTC interface"""
    js_code = get_js_code()

    return f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Patient Conversation</title>
        <style>
            .container {{
                max-width: 1000px;
                margin: 0 auto;
                padding: 20px;
                font-family: -apple-system, BlinkMacSystemFont, sans-serif;
            }}
            .controls {{
                text-align: center;
                margin: 20px 0;
                padding: 20px;
                background-color: #f8f9fa;
                border-radius: 10px;
            }}
            .chat-container {{
                margin: 20px 0;
                padding: 0;
                border: 2px solid #ddd;
                border-radius: 10px;
                height: 500px;
                overflow-y: auto;
                overflow-x: hidden;
                background-color: #ffffff;
                scroll-behavior: smooth;
                position: relative;
                box-sizing: border-box;
            }}
            .chat-content {{
                padding: 15px;
                min-height: 100%;
                display: flex;
                flex-direction: column;
            }}
            .message {{
                margin: 8px 0;
                padding: 12px 15px;
                border-radius: 10px;
                max-width: 85%;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                word-wrap: break-word;
                overflow-wrap: break-word;
            }}
            .user-message {{
                background-color: #e3f2fd;
                margin-left: auto;
                margin-right: 0;
                border-left: 4px solid #2196F3;
            }}
            .bot-message {{
                background-color: #f3e5f5;
                margin-left: 0;
                margin-right: auto;
                border-left: 4px solid #9C27B0;
            }}
            .message-label {{
                font-size: 0.85em;
                color: #666;
                margin-bottom: 6px;
                font-weight: bold;
            }}
            .message-content {{
                font-size: 1em;
                line-height: 1.4;
            }}
            .empty-state {{
                text-align: center;
                color: #666;
                font-style: italic;
                margin-top: 150px;
                flex-grow: 1;
                display: flex;
                align-items: center;
                justify-content: center;
            }}
            .status {{
                text-align: center;
                margin: 15px 0;
                padding: 10px;
                font-size: 1.1em;
                font-weight: bold;
                background-color: #f0f8ff;
                border-radius: 5px;
            }}
            .error {{
                color: #d32f2f;
                display: none;
                margin: 15px 0;
                padding: 10px;
                background-color: #ffebee;
                border-radius: 5px;
                border-left: 4px solid #d32f2f;
            }}
            button {{
                padding: 12px 24px;
                margin: 0 10px;
                border-radius: 8px;
                border: none;
                font-size: 1em;
                font-weight: bold;
                cursor: pointer;
                transition: all 0.3s ease;
            }}
            button:disabled {{
                background-color: #cccccc;
                cursor: not-allowed;
                opacity: 0.6;
            }}
            .start-btn {{
                background-color: #4CAF50;
                color: white;
            }}
            .start-btn:hover:not(:disabled) {{
                background-color: #45a049;
            }}
            .stop-btn {{
                background-color: #f44336;
                color: white;
            }}
            .stop-btn:hover:not(:disabled) {{
                background-color: #da190b;
            }}
            .finish-btn {{
                background-color: #ff9800;
                color: white;
            }}
            .finish-btn:hover:not(:disabled) {{
                background-color: #e68900;
            }}
            .instructions {{
                margin: 20px 0;
                padding: 15px;
                background-color: #fff3cd;
                border-radius: 5px;
                border-left: 4px solid #ffc107;
            }}
            .instructions h3 {{
                margin-top: 0;
                color: #856404;
            }}
            .instructions ul {{
                margin: 10px 0;
                padding-left: 20px;
            }}
            .instructions li {{
                margin: 5px 0;
            }}
            .scroll-indicator {{
                position: relative;
                text-align: center;
                margin: -10px 0 10px 0;
                display: none;
                z-index: 10;
            }}
            .scroll-to-bottom-btn {{
                background: linear-gradient(135deg, #4CAF50, #45a049);
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 20px;
                font-size: 0.9em;
                cursor: pointer;
                box-shadow: 0 2px 8px rgba(0,0,0,0.2);
                transition: all 0.3s ease;
                animation: bounce 2s infinite;
            }}
            .scroll-to-bottom-btn:hover {{
                background: linear-gradient(135deg, #45a049, #4CAF50);
                box-shadow: 0 4px 12px rgba(0,0,0,0.3);
                transform: translateY(-1px);
            }}
            @keyframes bounce {{
                0%, 20%, 50%, 80%, 100% {{
                    transform: translateY(0);
                }}
                40% {{
                    transform: translateY(-3px);
                }}
                60% {{
                    transform: translateY(-2px);
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container"> 
            <div class="instructions">
                <h3>📋 Instructions:</h3>
                <ul>
                    <li><strong>Start:</strong> Click "Start Conversation" and allow microphone access</li>
                    <li><strong>Talk:</strong> Speak naturally - and the patient will respond</li>
                    <li><strong>Finish:</strong> Click "Finish Conversation" when done to save your transcript</li>
                </ul>
            </div>
            
            <div class="controls">
                <button id="startButton" class="start-btn">🎙️ Start Conversation</button>
                <button id="stopButton" class="stop-btn" disabled>⏹️ Stop Conversation</button>
                <button id="finishButton" class="finish-btn" disabled>✅ Finish & Save</button>
            </div>
            
            <div id="status" class="status">Ready to start conversation with your patient</div>
            <div id="error" class="error"></div>
            
            <div id="chat-container" class="chat-container">
                <div class="chat-content" id="chat-content">
                    <div class="empty-state" id="empty-state">
                        Your conversation transcript will appear here...
                    </div>
                </div>
            </div>
            
            <div id="scroll-indicator" class="scroll-indicator">
                <button onclick="smartScrollToBottom(true)" class="scroll-to-bottom-btn">
                    ↓ New messages below ↓
                </button>
            </div>
        </div>
        
        <script>
            {js_code}
        </script>
    </body>
    </html>
    '''

# Page title and header
st.title("🗣️ Audio Conversation with your Patient")
st.markdown("---")

# Create the WebRTC interface
with st.container():
    # Create a placeholder for the conversation data
    conversation_data_placeholder = st.empty()
    
    # Add JavaScript listener for conversation completion
    completion_listener = """
    <script>
        console.log("Setting up conversation completion listener...");
        
        // Function to send data to Streamlit
        function sendToStreamlit(data) {
            console.log("Sending data to Streamlit:", data);
            
            // Create a custom event that Streamlit can listen to
            const event = new CustomEvent('conversationComplete', {
                detail: data
            });
            
            // Dispatch the event
            window.parent.document.dispatchEvent(event);
            
            // Also try to communicate via postMessage
            window.parent.postMessage({
                type: 'conversation_complete',
                data: data
            }, '*');
            
            console.log("Data sent to Streamlit via multiple methods");
        }
        
        window.addEventListener('message', function(event) {
            console.log("Received message:", event.data);
            
            if (event.data.type === 'conversation_complete') {
                console.log("=== CONVERSATION COMPLETION DETECTED ===");
                console.log("Transcript data:", event.data.data);
                
                // Store data in sessionStorage for backup
                const transcriptData = event.data.data;
                sessionStorage.setItem('conversation_data', JSON.stringify(transcriptData));
                console.log("Stored conversation data in sessionStorage");
                
                // Send to Streamlit
                sendToStreamlit(transcriptData);
            }
        });
    </script>
    """
    
    # Check if conversation was completed
    completion_check = """
    <script>
        console.log("Checking for stored conversation data...");
        const storedData = sessionStorage.getItem('conversation_data');
        if (storedData) {
            console.log("Found stored conversation data:", storedData);
            const data = JSON.parse(storedData);
            sessionStorage.removeItem('conversation_data');
            console.log("Removed conversation data from sessionStorage");
            
            // Send to Streamlit
            sendToStreamlit(data);
        } else {
            console.log("No stored conversation data found");
        }
    </script>
    """
    
    # Add a button to manually trigger conversation completion for testing
    if st.button("🔧 Test Conversation Completion"):
        test_data = {
            "transcript_segments": [
                {
                    "timestamp": "2025-06-30T08:00:00.000Z",
                    "speaker": "assistant",
                    "text": "Hi, I've been having some lower back pain."
                },
                {
                    "timestamp": "2025-06-30T08:01:00.000Z", 
                    "speaker": "user",
                    "text": "Tell me more about your symptoms."
                }
            ],
            "session_summary": {
                "duration_seconds": 60,
                "total_exchanges": 2
            },
            "conversation_metrics": {
                "total_exchanges": 2,
                "user_segments": 1,
                "assistant_segments": 1
            }
        }
        st.session_state["conversation_complete_data"] = test_data
        logger.info("=== TEST CONVERSATION DATA SET ===")
        st.success("✅ Test conversation data set! Check the logs below.")
    
    st.components.v1.html(
        get_webrtc_html() + completion_listener + completion_check,
        height=1000
    )

# Add JavaScript to listen for conversation completion events
st.markdown("""
<script>
    // Listen for conversation completion events
    document.addEventListener('conversationComplete', function(event) {
        console.log('Conversation completion event received:', event.detail);
        
        // Send the data to Streamlit via a form submission
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = window.location.href;
        
        const input = document.createElement('input');
        input.type = 'hidden';
        input.name = 'conversation_data';
        input.value = JSON.stringify(event.detail);
        
        form.appendChild(input);
        document.body.appendChild(form);
        form.submit();
    });
    
    // Also listen for postMessage events
    window.addEventListener('message', function(event) {
        if (event.data.type === 'conversation_complete') {
            console.log('Conversation completion message received:', event.data.data);
            
            // Send the data to Streamlit via a form submission
            const form = document.createElement('form');
            form.method = 'POST';
            form.action = window.location.href;
            
            const input = document.createElement('input');
            input.type = 'hidden';
            input.name = 'conversation_data';
            input.value = JSON.stringify(event.data.data);
            
            form.appendChild(input);
            document.body.appendChild(form);
            form.submit();
        }
    });
</script>
""", unsafe_allow_html=True)

# Check for form data in the request
try:
    # Try to access form data from the request
    import streamlit.runtime.scriptrunner as scriptrunner
    if hasattr(scriptrunner, 'get_script_run_ctx'):
        ctx = scriptrunner.get_script_run_ctx()
        if ctx and hasattr(ctx, 'form_data'):
            form_data = ctx.form_data
            if form_data and 'conversation_data' in form_data:
                logger.info("=== CONVERSATION DATA RECEIVED VIA FORM ===")
                conversation_data_str = form_data['conversation_data']
                try:
                    transcript_data = json.loads(conversation_data_str)
                    st.session_state["conversation_complete_data"] = transcript_data
                    logger.info("Successfully parsed and stored conversation data from form")
                    st.success("✅ Conversation data received via form!")
                except Exception as e:
                    logger.error(f"Error parsing conversation data from form: {e}")
                    st.error(f"Error parsing conversation data: {e}")
except Exception as e:
    logger.debug(f"Form data check failed: {e}")

# Check for URL parameter data (fallback)
query_params = st.query_params
if query_params.get("conversation_data"):
    logger.info("=== CONVERSATION DATA RECEIVED VIA URL PARAMS ===")
    conversation_data_str = query_params["conversation_data"]
    try:
        transcript_data = json.loads(conversation_data_str)
        st.session_state["conversation_complete_data"] = transcript_data
        logger.info("Successfully parsed and stored conversation data from URL params")
        
        # Show immediate feedback
        st.success("✅ Conversation data received via URL params!")
        
        # Clear the URL parameter to prevent reprocessing
        st.query_params.clear()
        
    except Exception as e:
        logger.error(f"Error parsing conversation data from URL params: {e}")
        logger.error(f"Raw data: {conversation_data_str[:200]}...")
        st.error(f"Error parsing conversation data: {e}")

# Add debug info to show current state
st.sidebar.markdown("### Debug Info")
st.sidebar.write(f"URL params: {dict(query_params)}")
st.sidebar.write(f"Session state keys: {list(st.session_state.keys())}")
if st.session_state.get("conversation_complete_data"):
    st.sidebar.write("✅ Conversation data found in session state")
else:
    st.sidebar.write("❌ No conversation data in session state")

# Handle conversation completion
if st.session_state.get("conversation_complete_data"):
    logger.info("=== CONVERSATION COMPLETION FLOW STARTED ===")
    transcript_data = st.session_state["conversation_complete_data"]
    
    logger.info(f"Received transcript data: {type(transcript_data)}")
    logger.info(f"Transcript data keys: {list(transcript_data.keys()) if isinstance(transcript_data, dict) else 'Not a dict'}")
    logger.info(f"Session state keys: {list(st.session_state.keys())}")
    logger.info(f"User identifier: {st.session_state.get('user_identifier', 'NOT_FOUND')}")
    logger.info(f"MongoDB URI available: {bool(st.session_state.get('mongodb_uri', None))}")
    
    # Log transcript to database
    try:
        logger.info("Attempting to log transcript to database...")
        session_id = log_audio_transcript(
            st.session_state["mongodb_uri"],
            "patient",
            transcript_data
        )
        
        logger.info(f"Database logging result - Session ID: {session_id}")
        
        if session_id:
            st.session_state["session_id"] = session_id
            st.session_state["p_conversation_finished"] = True
            st.session_state["part_1_done"] = True
            
            logger.info("Successfully updated session state")
            logger.info(f"Session ID stored: {st.session_state.get('session_id')}")
            logger.info(f"Conversation finished flag: {st.session_state.get('p_conversation_finished')}")
            
            # Clear the completion data
            del st.session_state["conversation_complete_data"]
            logger.info("Cleared conversation_complete_data from session state")
            
            st.success("✅ Conversation completed and saved successfully!")
            st.balloons()
            
            # Show next steps
            st.info("🎯 **Next Step:** Go to the 'Supervisor Conversation' page to get feedback on your conversation.")
            
        else:
            logger.error("Database logging returned None - no session ID created")
            st.error("❌ Failed to save conversation to database. Please try again.")
            
    except Exception as e:
        logger.error(f"=== DATABASE LOGGING ERROR ===")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Error message: {str(e)}")
        logger.error(f"Error details: {e}")
        
        # Log additional debugging info
        logger.error(f"MongoDB URI length: {len(st.session_state.get('mongodb_uri', '')) if st.session_state.get('mongodb_uri') else 'None'}")
        logger.error(f"Transcript data type: {type(transcript_data)}")
        logger.error(f"Transcript data sample: {str(transcript_data)[:200] if transcript_data else 'None'}")
        
        st.error(f"Error saving conversation: {str(e)}")
        logger.error(f"Error saving conversation: {e}")

# Add custom CSS for better styling
st.markdown("""
<style>
    .stButton > button {
        width: 100%;
        margin: 5px 0;
    }
    
    /* Hide the default Streamlit elements for cleaner look */
    .stDeployButton {
        display: none;
    }
    
    #MainMenu {
        visibility: hidden;
    }
    
    footer {
        visibility: hidden;
    }
</style>
""", unsafe_allow_html=True)