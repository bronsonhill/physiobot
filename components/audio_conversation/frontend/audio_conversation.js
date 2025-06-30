/**
 * Audio Conversation Component for PhysioBot
 * Handles realtime audio communication with OpenAI GPT-4 Audio
 */

class AudioConversationComponent {
    constructor() {
        // Initialize Streamlit communication
        this.streamlit = window.Streamlit;
        
        // Component state
        this.isInitialized = false;
        this.conversationData = null;
        this.conversationSegments = [];
        
        // Audio connection state
        this.peerConnection = null;
        this.audioStream = null;
        this.dataChannel = null;
        this.conversationActive = false;
        
        // UI elements
        this.startButton = null;
        this.stopButton = null;
        this.finishButton = null;
        this.statusDiv = null;
        this.errorDiv = null;
        this.chatContainer = null;
        this.chatContent = null;
        this.emptyState = null;
        
        // Configuration
        this.config = {
            instructions: "",
            api_key: "",
            conversation_id: "",
            user_identifier: ""
        };
        
        // Smart scrolling
        this.autoScrollEnabled = true;
        this.scrollTimeout = null;
        this.currentUserMessage = null;
        
        console.log("AudioConversationComponent initialized");
    }
    
    /**
     * Initialize the component with Streamlit data
     */
    initialize(componentData) {
        console.log("Initializing component with data:", componentData);
        
        // Store configuration
        this.config = {
            instructions: componentData.instructions || "",
            api_key: componentData.api_key || "",
            conversation_id: componentData.conversation_id || "",
            user_identifier: componentData.user_identifier || ""
        };
        
        // Get UI elements
        this.initializeUIElements();
        
        // Set up event listeners
        this.setupEventListeners();
        
        // Set up Streamlit communication
        this.setupStreamlitCommunication();
        
        this.isInitialized = true;
        console.log("Component initialization complete");
    }
    
    /**
     * Initialize UI element references
     */
    initializeUIElements() {
        this.startButton = document.getElementById('startButton');
        this.stopButton = document.getElementById('stopButton');
        this.finishButton = document.getElementById('finishButton');
        this.statusDiv = document.getElementById('status');
        this.errorDiv = document.getElementById('error');
        this.chatContainer = document.getElementById('chat-container');
        this.chatContent = document.getElementById('chat-content');
        this.emptyState = document.getElementById('empty-state');
    }
    
    /**
     * Set up event listeners for UI elements
     */
    setupEventListeners() {
        if (this.startButton) {
            this.startButton.addEventListener('click', () => this.startConversation());
        }
        
        if (this.stopButton) {
            this.stopButton.addEventListener('click', () => this.stopConversation());
        }
        
        if (this.finishButton) {
            this.finishButton.addEventListener('click', () => this.finishConversation());
        }
        
        if (this.chatContainer) {
            this.chatContainer.addEventListener('scroll', () => this.handleChatScroll());
        }
        
        console.log("Event listeners set up");
    }
    
    /**
     * Set up Streamlit communication
     */
    setupStreamlitCommunication() {
        if (this.streamlit) {
            // Tell Streamlit we're ready
            this.streamlit.setComponentReady();
            
            // Set initial height
            this.streamlit.setFrameHeight(1000);
            
            console.log("Streamlit communication established");
        } else {
            console.error("Streamlit object not available");
        }
    }
    
    /**
     * Start the conversation
     */
    async startConversation() {
        if (!this.config.api_key) {
            this.showError("API key is required");
            return;
        }
        
        console.log("Starting conversation...");
        this.startButton.disabled = true;
        
        try {
            this.updateStatus('Initializing...');
            
            // Setup WebRTC connection
            await this.setupWebRTCConnection();
            
            this.conversationActive = true;
            this.updateStatus('🟢 Connected - Ready to talk with your patient');
            this.stopButton.disabled = false;
            this.finishButton.disabled = false;
            this.hideError();
            
        } catch (error) {
            console.error('Error starting conversation:', error);
            this.showError('Error: ' + error.message);
            this.startButton.disabled = false;
            this.stopButton.disabled = true;
            this.finishButton.disabled = true;
            this.updateStatus('❌ Failed to connect');
        }
    }
    
    /**
     * Set up WebRTC connection to OpenAI
     */
    async setupWebRTCConnection() {
        // Create peer connection
        this.peerConnection = new RTCPeerConnection();
        
        // Setup audio
        await this.setupAudio();
        
        // Setup data channel
        this.setupDataChannel();
        
        // Create offer
        const offer = await this.peerConnection.createOffer();
        await this.peerConnection.setLocalDescription(offer);
        
        // Send to OpenAI
        const response = await fetch(`https://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-10-01`, {
            method: "POST",
            body: offer.sdp,
            headers: {
                Authorization: `Bearer ${this.config.api_key}`,
                "Content-Type": "application/sdp",
                "OpenAI-Beta": "realtime=v1"
            }
        });
        
        if (!response.ok) {
            throw new Error(`OpenAI API error: ${response.status}`);
        }
        
        // Set remote description
        const answer = {
            type: "answer",
            sdp: await response.text()
        };
        await this.peerConnection.setRemoteDescription(answer);
        
        console.log("WebRTC connection established");
    }
    
    /**
     * Setup audio stream
     */
    async setupAudio() {
        // Create audio element for playback
        const audioEl = document.createElement("audio");
        audioEl.autoplay = true;
        document.body.appendChild(audioEl);
        
        // Get user media
        this.audioStream = await navigator.mediaDevices.getUserMedia({
            audio: {
                echoCancellation: true,
                noiseSuppression: true,
                sampleRate: 48000,
                channelCount: 1
            }
        });
        
        // Handle incoming audio
        this.peerConnection.ontrack = (event) => {
            console.log("Received audio track");
            audioEl.srcObject = event.streams[0];
        };
        
        // Add outgoing audio
        this.audioStream.getTracks().forEach(track => {
            this.peerConnection.addTrack(track, this.audioStream);
        });
        
        console.log("Audio setup complete");
    }
    
    /**
     * Setup data channel for message communication
     */
    setupDataChannel() {
        this.dataChannel = this.peerConnection.createDataChannel("oai-events");
        this.dataChannel.onopen = () => this.onDataChannelOpen();
        this.dataChannel.onmessage = (event) => this.handleMessage(event);
        this.dataChannel.onerror = (error) => {
            console.error("DataChannel error:", error);
            this.showError("DataChannel error: " + error.message);
        };
        
        console.log("DataChannel setup complete");
    }
    
    /**
     * Handle data channel open
     */
    onDataChannelOpen() {
        console.log("DataChannel opened");
        
        // Send session configuration
        this.sendMessage({
            "type": "session.update",
            "session": {
                "instructions": this.config.instructions,
                "modalities": ["text", "audio"],
                "voice": "alloy",
                "input_audio_format": "pcm16",
                "output_audio_format": "pcm16",
                "input_audio_transcription": {
                    "model": "whisper-1"
                },
                "turn_detection": {
                    "type": "server_vad",
                    "threshold": 0.5,
                    "prefix_padding_ms": 300,
                    "silence_duration_ms": 800
                }
            }
        });
        
        // Start the conversation
        this.sendMessage({"type": "response.create"});
    }
    
    /**
     * Send message through data channel
     */
    sendMessage(message) {
        if (this.dataChannel?.readyState === "open") {
            this.dataChannel.send(JSON.stringify(message));
            console.log('Sent message:', message);
        }
    }
    
    /**
     * Handle incoming messages
     */
    handleMessage(event) {
        try {
            const message = JSON.parse(event.data);
            console.log('Received message:', message);
            
            switch (message.type) {
                case "response.done":
                    this.handleTranscript(message);
                    break;
                case "input_audio_buffer.speech_started":
                    console.log("Speech started");
                    this.updateStatus("🔴 Listening...");
                    this.createUserMessageContainer();
                    break;
                case "input_audio_buffer.speech_ended":
                    console.log("Speech ended");
                    this.updateStatus("🟡 Processing...");
                    break;
                case "conversation.item.input_audio_transcription.completed":
                    this.handleUserTranscript(message);
                    break;
                case "response.audio.done":
                    this.updateStatus("🟢 Ready to talk with your patient");
                    break;
                case "error":
                    console.error("Error from API:", message.error);
                    this.showError(message.error.message);
                    break;
                default:
                    console.log('Message type:', message.type);
            }
        } catch (error) {
            console.error('Error processing message:', error);
            this.showError('Error processing message: ' + error.message);
        }
    }
    
    /**
     * Create container for user message
     */
    createUserMessageContainer() {
        // Hide empty state
        if (this.emptyState) {
            this.emptyState.style.display = 'none';
        }
        
        this.currentUserMessage = document.createElement('div');
        this.currentUserMessage.className = 'message user-message';
        
        const label = document.createElement('div');
        label.className = 'message-label';
        label.textContent = '🧑‍⚕️ You';
        
        const content = document.createElement('div');
        content.className = 'message-content';
        content.textContent = 'Speaking...';
        
        this.currentUserMessage.appendChild(label);
        this.currentUserMessage.appendChild(content);
        this.chatContent.appendChild(this.currentUserMessage);
        this.smartScrollToBottom();
    }
    
    /**
     * Handle user transcript
     */
    handleUserTranscript(message) {
        if (this.currentUserMessage && message.transcript) {
            const content = this.currentUserMessage.querySelector('.message-content');
            content.textContent = message.transcript;
            
            // Add to conversation segments
            this.conversationSegments.push({
                timestamp: new Date().toISOString(),
                speaker: 'user',
                text: message.transcript
            });
            
            this.smartScrollToBottom();
        }
    }
    
    /**
     * Handle assistant transcript
     */
    handleTranscript(message) {
        if (message.response?.output?.[0]?.content?.[0]?.transcript) {
            const transcript = message.response.output[0].content[0].transcript;
            
            // Hide empty state
            if (this.emptyState) {
                this.emptyState.style.display = 'none';
            }
            
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
            this.chatContent.appendChild(botMessage);
            this.smartScrollToBottom();
            
            // Add to conversation segments
            this.conversationSegments.push({
                timestamp: new Date().toISOString(),
                speaker: 'assistant',
                text: transcript
            });
        }
    }
    
    /**
     * Stop the conversation
     */
    stopConversation() {
        console.log("Stopping conversation...");
        
        if (this.peerConnection) {
            this.peerConnection.close();
            this.peerConnection = null;
        }
        
        if (this.audioStream) {
            this.audioStream.getTracks().forEach(track => track.stop());
            this.audioStream = null;
        }
        
        if (this.dataChannel) {
            this.dataChannel.close();
            this.dataChannel = null;
        }
        
        this.conversationActive = false;
        this.startButton.disabled = false;
        this.stopButton.disabled = true;
        this.finishButton.disabled = true;
        this.updateStatus('Conversation ended');
    }
    
    /**
     * Finish and save the conversation
     */
    finishConversation() {
        console.log("=== FINISHING CONVERSATION ===");
        
        // Stop the conversation first
        this.stopConversation();
        
        if (this.conversationSegments.length > 0) {
            console.log(`Finalizing ${this.conversationSegments.length} conversation segments`);
            
            // Prepare conversation data
            const conversationData = {
                transcript_segments: this.conversationSegments,
                session_summary: {
                    duration_seconds: 0,
                    total_exchanges: this.conversationSegments.length
                },
                conversation_metrics: {
                    total_exchanges: this.conversationSegments.length,
                    user_segments: this.conversationSegments.filter(s => s.speaker === 'user').length,
                    assistant_segments: this.conversationSegments.filter(s => s.speaker === 'assistant').length
                }
            };
            
            console.log("Sending conversation data to Streamlit:", conversationData);
            
            // Send to Streamlit
            if (this.streamlit) {
                this.streamlit.setComponentValue(conversationData);
                console.log("Conversation data sent to Streamlit successfully");
            } else {
                console.error("Streamlit object not available");
            }
            
            this.updateStatus('✅ Conversation completed and saved!');
        } else {
            console.log("No conversation segments to save");
            this.updateStatus('No conversation to save');
        }
    }
    
    /**
     * Handle chat scroll for smart scrolling
     */
    handleChatScroll() {
        const container = this.chatContainer;
        const isScrolledToBottom = container.scrollHeight - container.scrollTop <= container.clientHeight + 50;
        
        this.autoScrollEnabled = isScrolledToBottom;
        
        if (this.scrollTimeout) {
            clearTimeout(this.scrollTimeout);
        }
        
        this.scrollTimeout = setTimeout(() => {
            this.updateScrollIndicator();
        }, 100);
    }
    
    /**
     * Smart scroll to bottom
     */
    smartScrollToBottom(force = false) {
        if (this.autoScrollEnabled || force) {
            setTimeout(() => {
                this.chatContainer.scrollTo({
                    top: this.chatContainer.scrollHeight,
                    behavior: this.autoScrollEnabled ? 'smooth' : 'auto'
                });
            }, 10);
        }
    }
    
    /**
     * Update scroll indicator
     */
    updateScrollIndicator() {
        const indicator = document.getElementById('scroll-indicator');
        if (indicator) {
            const hasMessages = this.chatContent.children.length > 1 || 
                              (this.chatContent.children.length === 1 && this.emptyState && this.emptyState.style.display === 'none');
            if (!this.autoScrollEnabled && hasMessages) {
                indicator.style.display = 'block';
            } else {
                indicator.style.display = 'none';
            }
        }
    }
    
    /**
     * Update status message
     */
    updateStatus(message) {
        if (this.statusDiv) {
            this.statusDiv.textContent = message;
        }
    }
    
    /**
     * Show error message
     */
    showError(message) {
        if (this.errorDiv) {
            this.errorDiv.style.display = 'block';
            this.errorDiv.textContent = message;
        }
    }
    
    /**
     * Hide error message
     */
    hideError() {
        if (this.errorDiv) {
            this.errorDiv.style.display = 'none';
        }
    }
}

// Global scroll function for the button
function smartScrollToBottom(force = false) {
    if (window.audioConversationComponent) {
        window.audioConversationComponent.smartScrollToBottom(force);
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM loaded, waiting for Streamlit...");
    
    // Wait for Streamlit to be available
    function initializeWhenReady() {
        if (window.Streamlit) {
            console.log("Streamlit available, initializing component");
            
            // Create component instance
            window.audioConversationComponent = new AudioConversationComponent();
            
            // Listen for data from Streamlit
            window.Streamlit.setComponentReady();
            window.Streamlit.setFrameHeight(1000);
            
            // Handle incoming data from Streamlit
            function onDataReceived(event) {
                if (event.detail && window.audioConversationComponent) {
                    console.log("Received data from Streamlit:", event.detail);
                    window.audioConversationComponent.initialize(event.detail);
                }
            }
            
            // Listen for data
            document.addEventListener("streamlit:render", onDataReceived);
            
        } else {
            console.log("Streamlit not ready, retrying...");
            setTimeout(initializeWhenReady, 100);
        }
    }
    
    initializeWhenReady();
});