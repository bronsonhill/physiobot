/**
 * Simplified Streamlit Component Library
 * Provides basic communication between component and Streamlit
 */

(function() {
    let componentReadyCallbacks = [];
    let componentValueCallbacks = [];
    let frameHeight = 1000;
    
    // Main Streamlit object
    window.Streamlit = {
        /**
         * Tell Streamlit that this component is ready
         */
        setComponentReady: function() {
            console.log("Component ready");
            window.parent.postMessage({
                type: "streamlit:componentReady",
                height: frameHeight
            }, "*");
        },
        
        /**
         * Set the height of the component iframe
         */
        setFrameHeight: function(height) {
            frameHeight = height;
            window.parent.postMessage({
                type: "streamlit:setFrameHeight", 
                height: height
            }, "*");
        },
        
        /**
         * Send data back to Streamlit
         */
        setComponentValue: function(value) {
            console.log("Sending value to Streamlit:", value);
            window.parent.postMessage({
                type: "streamlit:setComponentValue",
                value: value
            }, "*");
        },
        
        /**
         * Register a callback for when component data is received
         */
        onDataReceived: function(callback) {
            componentValueCallbacks.push(callback);
        }
    };
    
    // Listen for messages from Streamlit
    window.addEventListener("message", function(event) {
        console.log("Component received message:", event.data);
        
        if (event.data.type === "streamlit:render") {
            // Handle data from Streamlit
            const detail = event.data.args;
            console.log("Render data:", detail);
            
            // Dispatch custom event
            const customEvent = new CustomEvent("streamlit:render", {
                detail: detail
            });
            document.dispatchEvent(customEvent);
        }
    });
    
    console.log("Streamlit component library loaded");
})();