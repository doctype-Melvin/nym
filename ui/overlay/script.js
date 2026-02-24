let sessionState = {
    originalHashes: [],
    revokedHashes: [],
    manualMarks: [],
    history: [],
}

window.addEventListener("message", (event) => {
    if (event.data.type === "streamlit:render") {
        const { markdown, pii_map, revoked_hashes } = event.data.args;
        
        // Use the marked custom renderer
        const renderer = new marked.Renderer();
        
        renderer.text = (text) => {
            // Split text into words and punctuation
            return text.split(/(\b\w+\b)/g).map(part => {
                const category = pii_map[part];
                if (category) {
                    const isRevoked = revoked_hashes.includes(part); // Simplified for test
                    const styleClass = isRevoked ? 'pii-revoked' : `pii-${category.toLowerCase()}`;
                    
                    // Return the word wrapped in a span with metadata
                    return `<span class="pii-tag ${styleClass}" 
                                  data-word="${part}" 
                                  data-category="${category}"
                                  onclick="togglePII('${part}')">${part}</span>`;
                }
                return part;
            }).join('');
        };

        const container = document.getElementById('glass-box-container');
        container.innerHTML = marked.parse(markdown, { renderer });
        
        // ... height logic ...
    }
});

function togglePII(word) {
    // Send the toggled word back to Python
    window.parent.postMessage({
        isStreamlitMessage: true,
        type: "streamlit:setComponentValue",
        value: { action: "toggle", word: word }
    }, "*");
}

/*
function sendToStreamlit(type, data) {
            window.parent.postMessage({
                isStreamlitMessage: true,
                type: type,
                ...data
            }, "*");
        }

window.addEventListener("message", (event) => {
    if (event.data.type === "streamlit:render") {
        const { markdown } = event.data.args;
        
        try {
            if (typeof marked !== 'undefined') {
                document.getElementById('overlayer').innerHTML = marked.parse(markdown)
            } else {
                document.getElementById('overlayer').innerText = "Marked missing"
            }
        } catch (e) {
            document.getElementById('overlayer').innerText = "Error parsing: " + e.message
        }
        sendToStreamlit("streamlit:setComponentValue", { value: "Marked is working!" });
sendToStreamlit("streamlit:setFrameHeight", { value: document.body.scrollHeight });
    }
});

// Tell Streamlit we are ready
sendToStreamlit("streamlit:componentReady", { apiVersion: 1 });
*/