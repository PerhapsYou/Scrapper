class SLUChatbot {
    constructor() {
        //uginx proxy
        this.defaultBackendPort = 8000;
        this.protocol = window.location.protocol;
        this.hostname = window.location.hostname;
        this.ragServer = `${this.protocol}//${this.hostname}:${this.defaultBackendPort}`;


        this.chatMessages = document.getElementById('chatMessages');
        this.chatInput = document.getElementById('chatInput');
        this.sendBtn = document.getElementById('sendBtn');
        this.stopBtn = document.getElementById('stopBtn');
        this.typingIndicator = document.getElementById('typingIndicator');
        this.menuOptions = document.getElementById('menuOptions');
        
        this.isTyping = false;
        
        this.initializeEventListeners();
        this.displayCurrentTime();
        this.initializeWelcomeMessage();

        this.abortController = null;
    }

    async init() {
        // Load menu data from server
        this.menuData = await this.loadMenuData();
        this.initializeEventListeners();
        this.displayCurrentTime();
        this.initializeWelcomeMessage();
    }
    
    async loadMenuData() {
    try {
        const res = await fetch(`${this.ragServer}/menu`);
        const data = await res.json();
        const menu = {};
        data.menu.forEach((item, index) => {
            menu[item.id] = {
                title: item.title,
                emoji: item.emoji,
                content: item.content
            };
        });
        return menu;
    } catch (e) {
        console.error("Failed to load menu data from server:", e);
        return {};
    }
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
        // Send button click/ stop button click
        this.sendBtn.addEventListener('click', () => this.handleSend());
        this.stopBtn.addEventListener('click', () => this.handleStop());

        
        // Enter key press
        this.chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.handleSend();
            }
        });
        
        // Menu button clicks
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
        
        // Chat input box
        this.chatInput.addEventListener('input', () => {
            this.chatInput.style.height = 'auto';
            this.chatInput.style.height = Math.min(this.chatInput.scrollHeight, 100) + 'px';
        });
    }

    handleStop() {
        if (this.abortController) {
            this.abortController.abort();  // Immediately cancel any ongoing fetch
            this.abortController = null;   // Reset
        }
        fetch(`${this.ragServer}/stop`, {
            method: "POST"
        })
        .then(res => res.json())
        .then(data => {
            console.log("Stop requested:", data);
            this.hideTypingIndicator();
            this.toggleButtons(false);
        })
        .catch(err => {
            console.error("Stop request failed:", err);
        });
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
    
    // Handles User input or messages
    async handleSend() {
        const message = this.chatInput.value.trim();
        if (!message || this.isTyping) return;
        
        this.addUserMessage(message);
        this.chatInput.value = '';
        this.chatInput.style.height = 'auto';
        this.toggleButtons(true); // Show stop button

        
        await this.processMessage(message);
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
    
    async addBotMessage(content, showMenu = false) {
        await this.showTypingIndicator();
        
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message bot-message';
        messageDiv.innerHTML = `
            <div class="message-content">${content}</div>
            <div class="message-time">${this.getCurrentTime()}</div>
        `;
        
        this.chatMessages.appendChild(messageDiv);
        
        if (showMenu) {
            this.showMenuOptions();
        }
        
        this.hideTypingIndicator();
        this.scrollToBottom();
    }
    
    async processMessage(message) {
        const lowerMessage = message.toLowerCase();

        // Keyword or Menu matching
        if (this.isMenuRequest(lowerMessage)) {
            await this.addBotMessage("Here are the available options. Please select one:", true);
            return;
        }

        const response = this.getKeywordResponse(lowerMessage);
        if (response) {
            await this.addBotMessage(response);
            return;
        }

        try {
            console.log("Sending message to RAG server:", message);

            // Setup AbortController for cancel support
            this.abortController = new AbortController();
            const signal = this.abortController.signal;

            // Fetch streaming response from FastAPI
            const response = await fetch(`${this.ragServer}/chat/stream`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ query: message }),
            signal: signal
            });

            if (!response.ok || !response.body) {
            throw new Error("RAG stream failed.");
            }

            this.isTyping = true;
            this.toggleButtons(true); // Show Stop button
            this.typingIndicator.classList.add("active");

            const reader = response.body.getReader();
            const decoder = new TextDecoder("utf-8");
            let fullText = "";
            let botMessageDiv = document.createElement('div');
            botMessageDiv.className = 'message bot-message';
            botMessageDiv.innerHTML = `
            <div class="message-content" id="live-stream-content"></div>
            <div class="message-time">${this.getCurrentTime()}</div>
            `;
            this.chatMessages.appendChild(botMessageDiv);
            const contentDiv = document.getElementById("live-stream-content");

            while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value);
            const clean = chunk.replace(/^data:\s*/gm, '').trim();

            if (clean && clean !== "[DONE]") {
                fullText += clean;
                contentDiv.innerHTML = `<span class="blink-cursor">${this.escapeHtml(fullText)}</span>`;
                this.scrollToBottom();
            }
            }

            //post-stream
            this.typingIndicator.classList.remove("active");
            this.toggleButtons(false); // Restore Send button
            this.abortController = null;
            this.isTyping = false;

            // Remove blink-cursor so message stays static
            if (contentDiv) {
            contentDiv.innerHTML = this.escapeHtml(fullText);  // rewrite without blinking span
            }

        } catch (error) {
            console.error("Error while processing:", error);
            this.typingIndicator.classList.remove("active");
            this.toggleButtons(false);
            this.abortController = null;
            this.isTyping = false;
            await this.addBotMessage(`Sorry, something went wrong. Please try again.`);
        }
    }

    
    // Menu keywords
    isMenuRequest(message) {
        const menuKeywords = ['menu', 'options', 'help', 'start', 'begin', 'show menu'];
        return menuKeywords.some(keyword => message.includes(keyword));
    }
    
    getKeywordResponse(message) {
        // Admission keywords
        if (message.includes('admission') || message.includes('requirement') || message.includes('apply') || message.includes('eligible')) {
            return this.menuData["1"].content;
        }
        
        // Program keywords
        if (message.includes('program') || message.includes('course') || message.includes('degree') || message.includes('major')) {
            return this.menuData["2"].content;
        }
        
        // Fee keywords
        if (message.includes('fee') || message.includes('cost') || message.includes('tuition') || message.includes('price')) {
            return this.menuData["3"].content;
        }
        
        // Scholarship keywords
        if (message.includes('scholarship') || message.includes('financial aid') || message.includes('discount')) {
            return this.menuData["4"].content;
        }
        
        // Enrollment keywords
        if (message.includes('enroll') || message.includes('registration') || message.includes('process')) {
            return this.menuData["5"].content;
        }
        
        // Contact keywords
        if (message.includes('contact') || message.includes('mobile') || message.includes('phone') || message.includes('email') || message.includes('reach')) {
            return this.menuData["6"].content;
        }
        
        return null;
    }
    
    async handleMenuSelection(option) {
        const menuItem = this.menuData[option];
        if (menuItem) {
            this.addUserMessage(menuItem.title);
            await this.addBotMessage(menuItem.content);
            
            this.hideMenuOptions();
        }
    }
    
    async handleQuickAction(action) {
        switch (action) {
            case 'menu':
                this.addUserMessage("Show Menu");
                await this.addBotMessage(
                    "Here are the available options. Please select one:",
                    true
                );
                break;
            case 'help':
                this.addUserMessage("Help");
                await this.addBotMessage(
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
        
        Object.entries(this.menuData).forEach(([key, item]) => {
            const button = document.createElement('button');
            button.className = 'menu-btn';
            button.dataset.option = key;
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
    
    refreshMenuData() {
        this.menuData = this.loadMenuData();
        if (this.menuOptions.style.display !== 'none') {
            this.showMenuOptions();
        }
    }
}

document.addEventListener('DOMContentLoaded', async () => {
    window.sluChatbot = new SLUChatbot();
    await window.sluChatbot.init();
    
    window.addEventListener('storage', (e) => {
        if (e.key === 'slu_chatbot_menu') {
            window.sluChatbot.refreshMenuData();
        }
    });
});

