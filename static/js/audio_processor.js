/**
 * AudioProcessor - Web Audio API AudioWorklet processor for real-time audio capture
 * This processor handles audio data capture from the microphone and volume level detection
 */

class AudioProcessor extends AudioWorkletProcessor {
    constructor(options) {
        super();
        
        // Configuration from options
        this.sampleRate = options.processorOptions?.sampleRate || 24000;
        this.bufferSize = options.processorOptions?.bufferSize || 4096;
        
        // State
        this.isRecording = false;
        this.audioBuffer = [];
        this.volumeSmoothing = 0.95;
        this.currentVolume = 0;
        
        // Volume detection parameters
        this.volumeThreshold = 0.01;
        this.silenceFrames = 0;
        this.maxSilenceFrames = Math.floor(this.sampleRate / 128 * 0.5); // 0.5 seconds of silence
        
        // Listen for messages from main thread
        this.port.onmessage = (event) => {
            this.handleMessage(event.data);
        };
        
        console.log('AudioProcessor initialized with sampleRate:', this.sampleRate);
    }
    
    handleMessage(data) {
        switch (data.command) {
            case 'start':
                this.startRecording();
                break;
            case 'stop':
                this.stopRecording();
                break;
            default:
                console.log('Unknown command:', data.command);
        }
    }
    
    startRecording() {
        this.isRecording = true;
        this.audioBuffer = [];
        this.currentVolume = 0;
        this.silenceFrames = 0;
        console.log('AudioProcessor started recording');
    }
    
    stopRecording() {
        this.isRecording = false;
        console.log('AudioProcessor stopped recording');
    }
    
    process(inputs, outputs, parameters) {
        const input = inputs[0];
        
        if (!input || input.length === 0) {
            return true;
        }
        
        const inputChannel = input[0];
        const frameCount = inputChannel.length;
        
        if (frameCount === 0) {
            return true;
        }
        
        // Calculate volume level (RMS)
        let sum = 0;
        for (let i = 0; i < frameCount; i++) {
            sum += inputChannel[i] * inputChannel[i];
        }
        const rms = Math.sqrt(sum / frameCount);
        
        // Smooth volume level
        this.currentVolume = this.currentVolume * this.volumeSmoothing + rms * (1 - this.volumeSmoothing);
        
        // Send volume level to main thread
        this.port.postMessage({
            type: 'volume',
            volume: this.currentVolume
        });
        
        // If recording, capture audio data
        if (this.isRecording) {
            // Copy audio data to avoid issues with transferable objects
            const audioData = new Float32Array(frameCount);
            audioData.set(inputChannel);
            
            // Add to buffer
            this.audioBuffer.push(audioData);
            
            // Send audio data to main thread
            this.port.postMessage({
                type: 'audioData',
                audioData: Array.from(audioData) // Convert to regular array for transfer
            });
            
            // Detect silence for automatic stopping (optional feature)
            if (this.currentVolume < this.volumeThreshold) {
                this.silenceFrames++;
            } else {
                this.silenceFrames = 0;
            }
            
            // Auto-stop on extended silence (optional)
            if (this.silenceFrames > this.maxSilenceFrames) {
                this.port.postMessage({
                    type: 'silenceDetected'
                });
                this.silenceFrames = 0; // Reset to avoid repeated messages
            }
        }
        
        return true;
    }
}

// Register the processor
registerProcessor('audio-processor', AudioProcessor);