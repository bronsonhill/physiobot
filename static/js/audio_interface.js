/**
 * AudioInterface - Browser-side audio capture and playback for realtime conversation
 * Handles microphone access, audio recording, and playback controls
 */

class AudioInterface {
    constructor(config = {}) {
        // Configuration
        this.config = {
            sampleRate: config.sampleRate || 24000,
            bufferSize: config.bufferSize || 4096,
            channels: config.channels || 1,
            enableEchoCancellation: config.enableEchoCancellation !== false,
            enableNoiseSuppression: config.enableNoiseSuppression !== false,
            enableAutoGainControl: config.enableAutoGainControl !== false,
            visualizationEnabled: config.visualizationEnabled !== false,
            ...config
        };

        // Audio context and nodes
        this.audioContext = null;
        this.mediaStream = null;
        this.microphone = null;
        this.processor = null;
        this.analyser = null;
        this.gainNode = null;

        // Recording state
        this.isRecording = false;
        this.isPlaying = false;
        this.audioChunks = [];

        // Visualization
        this.visualizationData = new Float32Array(256);
        this.animationFrame = null;

        // Callbacks
        this.onAudioData = null;
        this.onVolumeLevel = null;
        this.onError = null;
        this.onStateChange = null;

        // Audio elements for playback
        this.audioElement = null;

        console.log('AudioInterface initialized with config:', this.config);
    }

    /**
     * Initialize audio context and request microphone permissions
     */
    async initialize() {
        try {
            // Request microphone permissions
            await this.requestMicrophonePermission();

            // Initialize audio context
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)({
                sampleRate: this.config.sampleRate,
                latencyHint: 'interactive'
            });

            // Resume audio context if suspended
            if (this.audioContext.state === 'suspended') {
                await this.audioContext.resume();
            }

            // Setup audio nodes
            await this.setupAudioNodes();

            console.log('AudioInterface initialized successfully');
            this.triggerStateChange('initialized');
            return true;

        } catch (error) {
            console.error('Failed to initialize AudioInterface:', error);
            this.triggerError(error.message);
            return false;
        }
    }

    /**
     * Request microphone permission
     */
    async requestMicrophonePermission() {
        const constraints = {
            audio: {
                sampleRate: this.config.sampleRate,
                channelCount: this.config.channels,
                echoCancellation: this.config.enableEchoCancellation,
                noiseSuppression: this.config.enableNoiseSuppression,
                autoGainControl: this.config.enableAutoGainControl
            }
        };

        this.mediaStream = await navigator.mediaDevices.getUserMedia(constraints);
        console.log('Microphone permission granted');
    }

    /**
     * Setup audio processing nodes
     */
    async setupAudioNodes() {
        if (!this.mediaStream || !this.audioContext) {
            throw new Error('Audio context or media stream not available');
        }

        // Create microphone input
        this.microphone = this.audioContext.createMediaStreamSource(this.mediaStream);

        // Create gain node for volume control
        this.gainNode = this.audioContext.createGain();
        this.gainNode.gain.value = 1.0;

        // Create analyser for visualization and volume detection
        this.analyser = this.audioContext.createAnalyser();
        this.analyser.fftSize = 512;
        this.analyser.smoothingTimeConstant = 0.8;

        // Create processor for audio data capture
        try {
            await this.audioContext.audioWorklet.addModule('./static/js/audio_processor.js');
            this.processor = new AudioWorkletNode(this.audioContext, 'audio-processor', {
                processorOptions: {
                    sampleRate: this.config.sampleRate,
                    bufferSize: this.config.bufferSize
                }
            });
        } catch (error) {
            console.warn('Failed to load audio processor worklet:', error);
            // Fallback: we can still work without the processor for basic functionality
            this.processor = null;
        }

        // Setup processor message handling
        if (this.processor) {
            this.processor.port.onmessage = (event) => {
                this.handleProcessorMessage(event.data);
            };
        }

        // Connect audio nodes
        this.microphone.connect(this.gainNode);
        this.gainNode.connect(this.analyser);
        if (this.processor) {
            this.gainNode.connect(this.processor);
        }

        console.log('Audio nodes setup completed');
    }

    /**
     * Start recording audio
     */
    async startRecording() {
        if (this.isRecording) {
            console.warn('Recording already in progress');
            return false;
        }

        if (!this.audioContext) {
            console.error('Audio context not initialized');
            return false;
        }

        try {
            // Clear previous audio chunks
            this.audioChunks = [];

            // Start recording
            this.isRecording = true;
            if (this.processor) {
                this.processor.port.postMessage({ command: 'start' });
            }

            // Start visualization if enabled
            if (this.config.visualizationEnabled) {
                this.startVisualization();
            }

            console.log('Audio recording started');
            this.triggerStateChange('recording');
            return true;

        } catch (error) {
            console.error('Failed to start recording:', error);
            this.isRecording = false;
            this.triggerError(error.message);
            return false;
        }
    }

    /**
     * Stop recording audio
     */
    async stopRecording() {
        if (!this.isRecording) {
            console.warn('No recording in progress');
            return null;
        }

        try {
            this.isRecording = false;
            if (this.processor) {
                this.processor.port.postMessage({ command: 'stop' });
            }

            // Stop visualization
            if (this.animationFrame) {
                cancelAnimationFrame(this.animationFrame);
                this.animationFrame = null;
            }

            // Return recorded audio data
            const audioData = this.audioChunks.length > 0 ? 
                this.concatenateAudioBuffers(this.audioChunks) : null;

            console.log('Audio recording stopped, captured', audioData ? audioData.length : 0, 'samples');
            this.triggerStateChange('stopped');

            return audioData;

        } catch (error) {
            console.error('Failed to stop recording:', error);
            this.triggerError(error.message);
            return null;
        }
    }

    /**
     * Play audio data
     */
    async playAudio(audioData) {
        if (!audioData || audioData.length === 0) {
            console.warn('No audio data provided for playback');
            return false;
        }

        try {
            this.isPlaying = true;
            this.triggerStateChange('playing');

            // Create audio buffer
            const audioBuffer = this.audioContext.createBuffer(
                1, // mono
                audioData.length,
                this.config.sampleRate
            );

            // Copy audio data to buffer
            const channelData = audioBuffer.getChannelData(0);
            if (audioData instanceof Int16Array) {
                // Convert Int16 to Float32
                for (let i = 0; i < audioData.length; i++) {
                    channelData[i] = audioData[i] / 32768.0;
                }
            } else {
                channelData.set(audioData);
            }

            // Create buffer source and play
            const source = this.audioContext.createBufferSource();
            source.buffer = audioBuffer;
            source.connect(this.audioContext.destination);

            source.onended = () => {
                this.isPlaying = false;
                this.triggerStateChange('playback_ended');
            };

            source.start();

            console.log('Audio playback started, duration:', audioBuffer.duration.toFixed(2), 'seconds');
            return true;

        } catch (error) {
            console.error('Failed to play audio:', error);
            this.isPlaying = false;
            this.triggerError(error.message);
            return false;
        }
    }

    /**
     * Handle messages from audio processor
     */
    handleProcessorMessage(data) {
        switch (data.type) {
            case 'audioData':
                if (this.isRecording) {
                    this.audioChunks.push(new Float32Array(data.audioData));
                    
                    // Trigger callback with audio data
                    if (this.onAudioData) {
                        this.onAudioData(data.audioData);
                    }
                }
                break;

            case 'volume':
                if (this.onVolumeLevel) {
                    this.onVolumeLevel(data.volume);
                }
                break;

            default:
                console.log('Unknown processor message:', data);
        }
    }

    /**
     * Start audio visualization
     */
    startVisualization() {
        if (!this.analyser) return;

        const animate = () => {
            if (!this.isRecording) return;

            this.analyser.getFloatFrequencyData(this.visualizationData);
            
            // Calculate average volume for simple visualization
            let sum = 0;
            for (let i = 0; i < this.visualizationData.length; i++) {
                sum += this.visualizationData[i];
            }
            const averageVolume = sum / this.visualizationData.length;

            // Update visualization elements (this can be customized)
            this.updateVisualizationElements(averageVolume, this.visualizationData);

            this.animationFrame = requestAnimationFrame(animate);
        };

        animate();
    }

    /**
     * Update visualization elements in the DOM
     */
    updateVisualizationElements(averageVolume, frequencyData) {
        // Update volume indicator
        const volumeIndicator = document.getElementById('volume-indicator');
        if (volumeIndicator) {
            const volumeLevel = Math.max(0, (averageVolume + 100) / 100); // Normalize to 0-1
            volumeIndicator.style.width = `${volumeLevel * 100}%`;
            volumeIndicator.style.backgroundColor = volumeLevel > 0.7 ? '#ff4444' : 
                                                   volumeLevel > 0.4 ? '#ffaa00' : '#44ff44';
        }

        // Update frequency bars
        const frequencyBars = document.querySelectorAll('.frequency-bar');
        if (frequencyBars.length > 0) {
            const step = Math.floor(frequencyData.length / frequencyBars.length);
            frequencyBars.forEach((bar, index) => {
                const value = Math.max(0, (frequencyData[index * step] + 100) / 100);
                bar.style.height = `${value * 100}%`;
            });
        }
    }

    /**
     * Concatenate audio buffers
     */
    concatenateAudioBuffers(buffers) {
        if (buffers.length === 0) return new Float32Array(0);

        const totalLength = buffers.reduce((sum, buffer) => sum + buffer.length, 0);
        const result = new Float32Array(totalLength);

        let offset = 0;
        for (const buffer of buffers) {
            result.set(buffer, offset);
            offset += buffer.length;
        }

        return result;
    }

    /**
     * Convert Float32Array to Int16Array for API transmission
     */
    float32ToInt16(float32Array) {
        const int16Array = new Int16Array(float32Array.length);
        for (let i = 0; i < float32Array.length; i++) {
            int16Array[i] = Math.max(-32768, Math.min(32767, float32Array[i] * 32768));
        }
        return int16Array;
    }

    /**
     * Convert Int16Array to Float32Array
     */
    int16ToFloat32(int16Array) {
        const float32Array = new Float32Array(int16Array.length);
        for (let i = 0; i < int16Array.length; i++) {
            float32Array[i] = int16Array[i] / 32768.0;
        }
        return float32Array;
    }

    /**
     * Set volume level
     */
    setVolume(level) {
        if (this.gainNode) {
            this.gainNode.gain.value = Math.max(0, Math.min(2, level));
        }
    }

    /**
     * Get current audio context state
     */
    getAudioContextState() {
        return {
            state: this.audioContext ? this.audioContext.state : 'not-initialized',
            sampleRate: this.audioContext ? this.audioContext.sampleRate : null,
            isRecording: this.isRecording,
            isPlaying: this.isPlaying
        };
    }

    /**
     * Check if browser supports required audio features
     */
    static checkBrowserSupport() {
        const support = {
            audioContext: !!(window.AudioContext || window.webkitAudioContext),
            mediaDevices: !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia),
            audioWorklet: !!(window.AudioWorkletNode),
            webAudio: !!(window.OfflineAudioContext)
        };

        const isSupported = Object.values(support).every(Boolean);
        return { isSupported, details: support };
    }

    /**
     * Cleanup resources
     */
    cleanup() {
        // Stop recording if active
        if (this.isRecording) {
            this.stopRecording();
        }

        // Stop visualization
        if (this.animationFrame) {
            cancelAnimationFrame(this.animationFrame);
        }

        // Close audio context
        if (this.audioContext) {
            this.audioContext.close();
        }

        // Stop media stream
        if (this.mediaStream) {
            this.mediaStream.getTracks().forEach(track => track.stop());
        }

        console.log('AudioInterface cleanup completed');
    }

    /**
     * Set callback functions
     */
    setCallbacks({ onAudioData, onVolumeLevel, onError, onStateChange } = {}) {
        this.onAudioData = onAudioData;
        this.onVolumeLevel = onVolumeLevel;
        this.onError = onError;
        this.onStateChange = onStateChange;
    }

    /**
     * Trigger state change callback
     */
    triggerStateChange(state) {
        if (this.onStateChange) {
            this.onStateChange(state);
        }
    }

    /**
     * Trigger error callback
     */
    triggerError(message) {
        if (this.onError) {
            this.onError(message);
        }
    }
}

// Export for use in modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AudioInterface;
} else {
    window.AudioInterface = AudioInterface;
}