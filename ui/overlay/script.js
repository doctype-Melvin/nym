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
                if (typeof content !== 'string' || !pii_map) return content;

                const sortedPII = Object.keys(pii_map).sort((a,b) => b.length - a.length)

                if (sortedPII.length === 0) return content

                const escapedPII = sortedPII.map(str => str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'))
                const regex = new RegExp(`(${escapedPII.join('|')})`, 'g')

            return content.replace(regex, (match) => {
                const category = pii_map[match];
                
                // Check if this word/phrase is in the exclusions list sent by Python
                const isExcluded = user_exclusions && user_exclusions.includes(match);
                
                const styleClass = isExcluded ? 'pii-excluded' : `pii-${category.toLowerCase()}`;
                
                return `<span class="pii-tag ${styleClass}" onclick="togglePII('${match}')">${match}</span>`;
                });
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
        value: { action: "toggle", word: word, click_id: Date.now() } 
    });
}

document.addEventListener('mouseup', () => {
    const selection = window.getSelection().toString().trim()

    if (selection && selection.length > 0 && selection.length < 100) {
        sendToStreamlit("streamlit:setComponentValue", {
            value: {
                action: "manual_mark",
                word: selection,
                click_id: Date.now()
            }
        })
    }
    window.getSelection().removeAllRanges()
})

// Handshake
sendToStreamlit("streamlit:componentReady", { apiVersion: 1 });