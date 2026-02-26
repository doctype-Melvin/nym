window.addEventListener("message", (event) => {
    if (event.data.type === "streamlit:render") {
        // We only need the 'markdown' (which is now pre-rendered HTML)
        const { markdown } = event.data.args;
        const container = document.getElementById('overlayer');

        try {
            // Using marked.parse on the already 'marked-up' HTML 
            // will render the structural markdown (headers, lists) 
            // while preserving our custom <mark> tags.
            container.innerHTML = marked.parse(markdown);
            
            // Re-attach listeners to the new HTML elements
            attachPIIListeners();

        } catch (err) {
            console.error("Render error:", err);
        }
    }
});

function attachPIIListeners() {
    // Find all the <mark> tags we injected in Python
    const marks = document.querySelectorAll('mark');
    marks.forEach(mark => {
        mark.onclick = function() {
            // Send the pii_id back to Python to update the DB
            sendToStreamlit({ 
                action: "toggle",
                pii_id: this.getAttribute('data-id'),
                click_id: Date.now() 
            });
        };
    });
}

function sendToStreamlit(data) {
    window.parent.postMessage({
        isStreamlitMessage: true,
        type: "streamlit:setComponentValue",
        value: data
    }, "*");
}

// manual selection logic - very useful!
document.addEventListener('mouseup', () => {
    const selection = window.getSelection().toString().trim();
    if (selection && selection.length > 1 && selection.length < 100) {
        sendToStreamlit({ 
            action: "manual_mark",
            word: selection,
            click_id: Date.now()
        });
        window.getSelection().removeAllRanges()
    }
});

// Handshake
window.parent.postMessage({isStreamlitMessage: true, type: "streamlit:componentReady", apiVersion: 1}, "*");