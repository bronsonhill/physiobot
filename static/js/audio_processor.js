/**
 * AudioProcessor - AudioWorkletProcessor for real-time audio capture
 * Handles audio data capture, volume detection, and buffering
 */

class AudioProcessor extends AudioWorkletProcessor {
    constructor(options) {
        super();
        
        // Configuration from options
        this.sampleRate = options.processorOptions?.sampleRate || 24000;
        this.bufferSize = options.processorOptions?.bufferSize || 4096;
        
        // Processing state
        this.isRecording = false;
        this.buffer = new Float32Array(this.bufferSize);
        this.bufferIndex = 0;
        
        // Volume detection
        this.volumeAccumulator = 0;
        this.volumeSampleCount = 0;
        this.volumeReportInterval = Math.floor(this.sampleRate / 10); // Report 10 times per second
        
        // Listen for messages from main thread
        this.port.onmessage = (event) => {
            this.handleMessage(event.data);
        };
        
        console.log('AudioProcessor initialized with sampleRate:', this.sampleRate, 'bufferSize:', this.bufferSize);
    }

    /**
     * Process audio data
     */
    process(inputs, outputs, parameters) {
        const input = inputs[0];
        
        // Only process if we have input and are recording
        if (!input || !input[0] || !this.isRecording) {
            return true;
        }
        
        const inputChannel = input[0]; // First channel (mono)
        
        // Process each sample
        for (let i = 0; i < inputChannel.length; i++) {
            const sample = inputChannel[i];
            
            // Add to buffer
            this.buffer[this.bufferIndex] = sample;
            this.bufferIndex++;
            
            // Accumulate volume data
            this.volumeAccumulator += Math.abs(sample);
            this.volumeSampleCount++;
            
            // Send buffer when full
            if (this.bufferIndex >= this.bufferSize) {
                this.sendAudioData();
                this.bufferIndex = 0;
            }
            
            // Report volume periodically
            if (this.volumeSampleCount >= this.volumeReportInterval) {
                this.reportVolume();
            }
        }
        
        return true; // Keep processor alive
    }

    /**
     * Handle messages from main thread
     */
    handleMessage(data) {
        switch (data.command) {
            case 'start':
                this.startRecording();
                break;
                
            case 'stop':
                this.stopRecording();
                break;
                
            case 'configure':
                this.configure(data.config);
                break;
                
            default:
                console.log('Unknown command:', data.command);
        }
    }

    /**
     * Start recording audio
     */
    startRecording() {
        this.isRecording = true;
        this.bufferIndex = 0;
        this.volumeAccumulator = 0;
        this.volumeSampleCount = 0;
        
        console.log('AudioProcessor: Recording started');
    }

    /**
     * Stop recording audio
     */
    stopRecording() {
        this.isRecording = false;
        
        // Send any remaining buffered data
        if (this.bufferIndex > 0) {
            this.sendAudioData();
            this.bufferIndex = 0;
        }
        
        console.log('AudioProcessor: Recording stopped');
    }

    /**
     * Configure processor parameters
     */
    configure(config) {
        if (config.bufferSize) {
            this.bufferSize = config.bufferSize;
            this.buffer = new Float32Array(this.bufferSize);
            this.bufferIndex = 0;
        }
        
        if (config.volumeReportInterval) {
            this.volumeReportInterval = config.volumeReportInterval;
        }
        
        console.log('AudioProcessor: Configuration updated', config);
    }

    /**
     * Send buffered audio data to main thread
     */
    sendAudioData() {
        // Create a copy of the current buffer content
        const audioData = new Float32Array(this.bufferIndex);
        audioData.set(this.buffer.subarray(0, this.bufferIndex));
        
        // Send to main thread
        this.port.postMessage({
            type: 'audioData',
            audioData: audioData,
            timestamp: currentTime,
            bufferSize: this.bufferIndex
        });
    }

    /**
     * Report current volume level
     */
    reportVolume() {
        if (this.volumeSampleCount === 0) return;
        
        // Calculate RMS volume
        const rmsVolume = Math.sqrt(this.volumeAccumulator / this.volumeSampleCount);
        
        // Send volume data to main thread
        this.port.postMessage({
            type: 'volume',
            volume: rmsVolume,
            timestamp: currentTime
        });
        
        // Reset volume accumulator
        this.volumeAccumulator = 0;
        this.volumeSampleCount = 0;
    }

    /**
     * Calculate audio statistics
     */
    calculateAudioStats(buffer, length) {
        let sum = 0;
        let sumSquares = 0;
        let max = 0;
        
        for (let i = 0; i < length; i++) {
            const sample = Math.abs(buffer[i]);
            sum += sample;
            sumSquares += sample * sample;
            max = Math.max(max, sample);
        }
        
        const mean = sum / length;
        const rms = Math.sqrt(sumSquares / length);
        
        return {
            mean,
            rms,
            max,
            samples: length
        };
    }

    /**
     * Apply simple audio processing (optional)
     */
    processAudioBuffer(buffer, length) {
        // This can be extended to apply filters, noise reduction, etc.
        // For now, just return the buffer as-is
        return buffer;
    }
}

// Register the processor
registerProcessor('audio-processor', AudioProcessor);