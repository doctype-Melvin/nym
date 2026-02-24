let sessionState = {
    originalHashes: [],
    revokedHashes: [],
    manualMarks: [],
    history: [],
};

function sendToStreamlit(type, data) {
    window.parent.postMessage({
        isStreamlitMessage: true,
        type: type,
        ...data
    }, "*");
}

window.addEventListener("message", (event) => {
    if (event.data.type === "streamlit:render") {
        const { markdown, pii_map, user_exclusions } = event.data.args;
        sessionState.revokedHashes = user_exclusions;

        const container = document.getElementById('overlayer');

        try {
            const renderer = new marked.Renderer();

            renderer.link = (href, title, text) => text
            renderer.mailto = (href, title, text) => text

            renderer.text = (token) => {
                let content = (typeof token === 'object') ? token.text : token;
                if (typeof content !== 'string') return content;

                return content.split(/(\b\w+\b)/g).map(part => {
                    const category = pii_map ? pii_map[part] : null;
                    if (category) {
                        const isRevoked = sessionState.revokedHashes.includes(part); 
                        const styleClass = isRevoked ? 'pii-revoked' : `pii-${category.toLowerCase()}`;
                        return `<span class="pii-tag ${styleClass}" onclick="togglePII('${part}')">${part}</span>`;
                    }
                    return part;
                }).join('');
            };

            marked.setOptions({
                gfm: false,
                breaks: true
            })

            container.innerHTML = marked.parse(markdown, { renderer });
            
            
        } catch (err) {
            console.error("Render error:", err);
        }
    }
});

function togglePII(word) {
    sendToStreamlit("streamlit:setComponentValue", { 
        value: { action: "toggle", word: word } 
    });
}

// Handshake
sendToStreamlit("streamlit:componentReady", { apiVersion: 1 });