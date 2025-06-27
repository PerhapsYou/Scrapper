class SLUChatbot {
    constructor() {
        this.defaultBackendPort = 8000;
        this.protocol = window.location.protocol;
        this.hostname = window.location.hostname;
        this.actionsURL = `${this.protocol}//${this.hostname}:${this.defaultBackendPort}`;

        this.chatMessages = document.getElementById('chatMessages');
        this.chatInput = document.getElementById('chatInput');
        this.sendBtn = document.getElementById('sendBtn');
        this.stopBtn = document.getElementById('stopBtn');
        this.typingIndicator = document.getElementById('typingIndicator');
        this.menuOptions = document.getElementById('menuOptions');

        this.isTyping = false;
        this.abortController = null;
    }

    async init() {
        await this.loadMenuData();
        this.menuOptions.style.display = 'none';
        this.initializeEventListeners();
        this.displayCurrentTime();
        this.initializeWelcomeMessage();
    }

    async initializeWelcomeMessage() {
        const staticWelcome = document.querySelector('#chatMessages .message.bot-message');
        if (staticWelcome) {
            staticWelcome.style.display = 'none';
        }

        this.menuOptions.style.display = 'none';
        await this.showTypingIndicator();

        const messageDiv = document.createElement('div');
        messageDiv.className = 'message bot-message';
        messageDiv.innerHTML = `
            <div class="message-content">
                <p>Hello! Welcome to the SLU Enrollment Assistant.</p>
                <p>How can I assist you today?</p>
            </div>
            <div class="message-time">${this.getCurrentTime()}</div>
        `;

        this.chatMessages.appendChild(messageDiv);
        this.hideTypingIndicator();
        this.scrollToBottom();
    }

    initializeEventListeners() {
        this.sendBtn.addEventListener('click', () => this.handleSend());
        this.stopBtn.addEventListener('click', () => this.handleStop());

        this.chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.handleSend();
            }
        });

        document.addEventListener('click', (e) => {
            if (e.target.closest('.menu-btn')) {
                const option = e.target.closest('.menu-btn').dataset.option;
                this.handleMenuSelection(option);
            }

            if (e.target.closest('.quick-btn')) {
                const action = e.target.closest('.quick-btn').dataset.quick;
                this.handleQuickAction(action);
            }
        });

        this.chatInput.addEventListener('input', () => {
            this.chatInput.style.height = 'auto';
            this.chatInput.style.height = Math.min(this.chatInput.scrollHeight, 100) + 'px';
        });
    }

    handleStop() {
        if (this.abortController) {
            this.abortController.abort();
            this.abortController = null;
        }
    }

    toggleButtons(isBotGenerating) {
        this.sendBtn.style.display = isBotGenerating ? "none" : "inline-block";
        this.stopBtn.style.display = isBotGenerating ? "inline-block" : "none";
    }

    displayCurrentTime() {
        const now = new Date();
        const timeString = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        const initialTimeElement = document.getElementById('initialTime');
        if (initialTimeElement) {
            initialTimeElement.textContent = timeString;
        }
    }

    async handleSend() {
    const message = this.chatInput.value.trim();
    if (!message || this.isTyping) return;

    this.addUserMessage(message);
    this.chatInput.value = '';
    this.chatInput.style.height = 'auto';

    this.toggleButtons(true); // Show stop button immediately
    this.streamBotResponse(message); // Don't await, let streaming handle itself
}


    addUserMessage(message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message user-message';
        messageDiv.innerHTML = `
            <div class="message-content">${this.escapeHtml(message)}</div>
            <div class="message-time">${this.getCurrentTime()}</div>
        `;

        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }

    async streamBotText(targetDiv, text, delay = 25) {
        for (let i = 0; i < text.length; i++) {
            targetDiv.innerHTML += this.escapeHtml(text[i]);
            this.scrollToBottom();
            await new Promise(resolve => setTimeout(resolve, delay));
        }
    }

    async streamBotResponse(query) {
        await this.showTypingIndicator();
        this.toggleButtons(true);

        const messageDiv = document.createElement("div");
        messageDiv.className = "message bot-message";
        messageDiv.innerHTML = `
            <div class="message-content"></div>
            <div class="message-time">${this.getCurrentTime()}</div>
        `;
        const contentDiv = messageDiv.querySelector(".message-content");
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();

        try {
            const response = await fetch("http://localhost:5005/webhooks/rest/webhook", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ sender: "user", message: query })
            });

            const data = await response.json();

            if (data.length === 0) {
                await this.streamBotText(contentDiv, "Sorry, I didn’t understand that.");
                this.hideTypingIndicator();
                this.toggleButtons(false);
                return;
            }

            for (const item of data) {
                if (item.custom && item.custom.stream_from_rag) {
                    const ragSource = new EventSource(`${this.actionsURL}/chat/stream?query=${encodeURIComponent(query)}`);
                    let fullRag = "";

                    ragSource.onmessage = (event) => {
                        if (event.data === "[DONE]") {
                            ragSource.close();
                            this.hideTypingIndicator();
                            this.toggleButtons(false);
                            return;
                        }
                        fullRag += event.data;
                        contentDiv.innerHTML += this.escapeHtml(event.data);
                        this.scrollToBottom();
                    };

                    ragSource.onerror = (err) => {
                        console.error("SSE stream error from RAG:", err);
                        ragSource.close();
                        this.hideTypingIndicator();
                        this.toggleButtons(false);
                    };

                    this.abortController = {
                        abort: () => {
                            fetch(`${this.actionsURL}/stop`, { method: "POST" })
                                .then(() => {
                                    ragSource.close();
                                    this.hideTypingIndicator();
                                    this.toggleButtons(false);
                                    this.isTyping = false;
                                })
                                .catch(err => console.error("Stop failed", err));
                        }
                    };
                } else if (item.text) {
                    await this.streamBotText(contentDiv, item.text);
                }
            }

        } catch (err) {
            console.error("Rasa communication failed:", err);
            await this.streamBotText(contentDiv, "Sorry, something went wrong.");
        }

        this.hideTypingIndicator();
        this.toggleButtons(false);
        this.isTyping = false;
    }

    async streamFromRAG(query) {
        await this.showTypingIndicator();
        this.toggleButtons(true);

        const messageDiv = document.createElement("div");
        messageDiv.className = "message bot-message";
        messageDiv.innerHTML = `
            <div class="message-content"></div>
            <div class="message-time">${this.getCurrentTime()}</div>
        `;
        const contentDiv = messageDiv.querySelector(".message-content");
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();

        const encodedQuery = encodeURIComponent(query);
        const source = new EventSource(`${this.actionsURL}/chat/stream?query=${encodedQuery}`);

        let fullResponse = "";

        source.onmessage = (event) => {
            const token = event.data;
            fullResponse += token;
            contentDiv.innerHTML += this.escapeHtml(token);
            this.scrollToBottom();
        };

        source.onerror = (err) => {
            console.error("SSE stream error:", err);
            source.close();
            this.hideTypingIndicator();
            this.toggleButtons(false);
            this.isTyping = false;
        };

        this.abortController = {
            abort: () => {
                fetch(`${this.actionsURL}/stop`, { method: "POST" })
                    .then(() => {
                        source.close();
                        this.hideTypingIndicator();
                        this.toggleButtons(false);
                        this.isTyping = false;
                    })
                    .catch(err => console.error("Stop failed", err));
            }
        };
    }

    async processMessage(message) {
        try {
            this.abortController = new AbortController();
            const signal = this.abortController.signal;

            const response = await fetch("http://localhost:5005/webhooks/rest/webhook", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ sender: "user", message }),
                signal
            });

            const data = await response.json();

            for (const item of data) {
                if (item.text) {
                    await this.streamBotText(this.createBotMessageContainer(), item.text);
                } else if (item.json_message && item.json_message.stream_from_rag) {
                    const ragQuery = item.json_message.query;
                    await this.streamFromRAG(ragQuery);
                }
            }

            this.toggleButtons(false);
            this.isTyping = false;
        } catch (error) {
            console.error("Error processing message:", error);
            await this.streamBotText(this.createBotMessageContainer(), "Sorry, something went wrong.");
            this.toggleButtons(false);
            this.isTyping = false;
        }
    }

    createBotMessageContainer() {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message bot-message';
        messageDiv.innerHTML = `
            <div class="message-content"></div>
            <div class="message-time">${this.getCurrentTime()}</div>
        `;
        this.chatMessages.appendChild(messageDiv);
        const contentDiv = messageDiv.querySelector(".message-content");
        this.scrollToBottom();
        return contentDiv;
    }

    isMenuRequest(message) {
        const menuKeywords = ['menu', 'options', 'help', 'start', 'begin', 'show menu'];
        return menuKeywords.some(keyword => message.includes(keyword));
    }

    async handleMenuSelection(optionId) {
        const selected = this.menuData.menu.find(item => item.id == optionId);
        if (selected) {
            this.addUserMessage(selected.title);
            const contentDiv = this.createBotMessageContainer();
            await this.streamBotText(contentDiv, selected.content);
            this.hideMenuOptions();
        }
    }

    async handleQuickAction(action) {
        switch (action) {
            case 'menu':
                this.addUserMessage("Show Menu");
                try {
                    const response = await fetch("http://localhost:5005/webhooks/rest/webhook", {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json"
                        },
                        body: JSON.stringify({ message: "menu" })
                    });
                    const data = await response.json();
                    for (const message of data) {
                        if (message.text) {
                            const contentDiv = this.createBotMessageContainer();
                            await this.streamBotText(contentDiv, message.text);
                        }
                    }
                    await this.showMenuOptions();

                } catch (err) {
                    console.error("Error fetching dynamic menu:", err);
                    const contentDiv = this.createBotMessageContainer();
                    await this.streamBotText(contentDiv, "Sorry, I couldn’t load the menu.");
                }
                break;
            case 'help':
                this.addUserMessage("Help");
                const contentDiv = this.createBotMessageContainer();
                await this.streamBotText(contentDiv,
                    `I'm here to help with your SLU enrollment questions! You can:
<br>• Click on the menu buttons when available
<br>• Type keywords like "admission", "programs", "fees", etc.
<br>• Ask specific questions about enrollment
<br>• Type "menu" anytime to see all options<br>
<br>What would you like to know about?`
                );
                break;
        }
    }

    showMenuOptions() {
        const menuGrid = this.menuOptions.querySelector('.menu-grid');
        menuGrid.innerHTML = '';

        this.menuData.menu.forEach(item => {
            const button = document.createElement('button');
            button.className = 'menu-btn';
            button.dataset.optionId = item.id;
            button.dataset.content = item.content;
            button.innerHTML = `
                <span class="menu-emoji">${item.emoji}</span>
                <span class="menu-text">${item.title}</span>
            `;
            menuGrid.appendChild(button);
        });

        const lastBotMessage = [...this.chatMessages.querySelectorAll('.bot-message')].pop();
        if (lastBotMessage) {
            lastBotMessage.appendChild(this.menuOptions);
        }

        this.menuOptions.style.display = 'block';
        this.scrollToBottom();
    }

    hideMenuOptions() {
        this.menuOptions.style.display = 'none';
    }

    async showTypingIndicator() {
        this.isTyping = true;
        this.typingIndicator.classList.add('active');
        this.scrollToBottom();

        await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 1000));
    }

    async loadMenuData() {
        try {
            const res = await fetch(`${this.actionsURL}/menu`);
            const data = await res.json();

            this.menuData = data;

            console.log("Menu data loaded:", this.menuData);

            if (this.menuOptions.style.display !== 'none') {
                this.showMenuOptions();
            }
        } catch (error) {
            console.error(">< Failed to load menu data from server:", error);
            this.menuData = { menu: [] };
        }
    }

    hideTypingIndicator() {
        this.isTyping = false;
        this.typingIndicator.classList.remove('active');
    }

    scrollToBottom() {
        setTimeout(() => {
            this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
        }, 100);
    }

    getCurrentTime() {
        return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    async refreshMenuData() {
        await this.loadMenuData();
        if (this.menuOptions.style.display !== 'none') {
            this.showMenuOptions();
        }
    }
}

document.addEventListener('DOMContentLoaded', async () => {
    window.sluChatbot = new SLUChatbot();
    await window.sluChatbot.init();

    window.addEventListener('storage', async (e) => {
        if (e.key === 'slu_chatbot_menu') {
            await window.sluChatbot.refreshMenuData();
        }
    });
});

