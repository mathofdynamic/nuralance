document.addEventListener('DOMContentLoaded', () => {
    const uploadArea = document.getElementById('upload-area');
    const chatArea = document.getElementById('chat-area');
    const uploadButton = document.getElementById('upload-button');
    const csvUploadInput = document.getElementById('csv-upload');
    const sendButton = document.getElementById('send-button');
    const messageInput = document.getElementById('message-input');
    const chatWindow = document.getElementById('chat-window');
    const statusArea = document.getElementById('status-area');

    // Configure marked.js for better rendering
    if (typeof marked !== 'undefined') {
        marked.setOptions({
            breaks: true, // Convert line breaks to <br>
            gfm: true,    // Use GitHub Flavored Markdown
        });
    }

    let sessionId = sessionStorage.getItem('nuralance_session_id');
    if (!sessionId) {
        sessionId = 'session_' + Date.now() + Math.random().toString(36).substring(2, 9);
        sessionStorage.setItem('nuralance_session_id', sessionId);
    }

    function addMessage(text, sender) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', `${sender}-message`);

        // Use marked.js for assistant messages for rich formatting
        if (sender === 'assistant' && typeof marked !== 'undefined') {
            messageElement.innerHTML = marked.parse(text);
        } else {
            messageElement.textContent = text;
        }

        chatWindow.appendChild(messageElement);
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }

    uploadButton.addEventListener('click', async () => {
        const file = csvUploadInput.files[0];
        if (!file) {
            statusArea.textContent = 'Please select a CSV file first.';
            return;
        }

        statusArea.textContent = 'Uploading and analyzing your data... This may take a moment.';
        const formData = new FormData();
        formData.append('csv_file', file);
        formData.append('session_id', sessionId);

        try {
            const response = await fetch('/upload-csv', {
                method: 'POST',
                body: formData,
            });
            const result = await response.json();

            if (!response.ok) throw new Error(result.detail || 'Upload failed');
            
            // Professional welcome message using markdown
            const welcomeMessage = `**Analysis Complete!**\n\nI've processed your file. Here's what I understand about your data:\n\n${result.db_description}\n\nHow can I help you analyze this information?`;
            addMessage(welcomeMessage, 'assistant');
            statusArea.textContent = 'Ready';
            
            uploadArea.style.display = 'none';
            chatArea.style.display = 'flex';
            messageInput.focus();

        } catch (error) {
            statusArea.textContent = `Error: ${error.message}`;
        }
    });

    async function sendMessage() {
        const messageText = messageInput.value.trim();
        if (messageText === '') return;

        addMessage(messageText, 'user');
        messageInput.value = '';
        statusArea.textContent = 'Nuralance is thinking...';

        try {
            const response = await fetch('/chatbot/message', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ session_id: sessionId, message: messageText }),
            });
            const result = await response.json();

            if (!response.ok) throw new Error(result.detail || 'Failed to get response');

            addMessage(result.response, 'assistant');
            statusArea.textContent = 'Ready';

        } catch (error) {
            addMessage(`Error: ${error.message}`, 'assistant');
            statusArea.textContent = 'Error';
        }
    }

    sendButton.addEventListener('click', sendMessage);
    messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });

    addMessage('**Welcome to Nuralance!**\n\nPlease upload your finance data as a CSV file to begin.', 'assistant');
});