/**
 * Main Application Script
 * Handles portfolio management, API communication, and UI updates
 */

class TradingAssistant {
    constructor() {
        this.portfolio = [];
        this.analysisHistory = [];
        this.botRenderer = null;
        this.apiBaseUrl = '/api';
        this.webSocketUrl = 'ws://localhost:8080/ws';
        this.ws = null;
        
        this.initElements();
        this.setupEventListeners();
        this.initBot();
        this.loadPortfolio();
        this.connectWebSocket();
    }
    
    initElements() {
        this.elements = {
            canvas: document.getElementById('botCanvas'),
            portfolioInput: document.getElementById('portfolioInput'),
            addBtn: document.getElementById('addBtn'),
            portfolioList: document.getElementById('portfolioList'),
            totalValue: document.getElementById('totalValue'),
            totalGain: document.getElementById('totalGain'),
            analysisHistory: document.getElementById('analysisHistory'),
            analyzeBtn: document.getElementById('analyzeBtn'),
            connectionStatus: document.getElementById('connectionStatus'),
            speechBubble: document.getElementById('speechBubble'),
            speechText: document.getElementById('speechText')
        };
    }
    
    setupEventListeners() {
        this.elements.addBtn.addEventListener('click', () => this.addToPortfolio());
        this.elements.portfolioInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.addToPortfolio();
        });
        this.elements.analyzeBtn.addEventListener('click', () => this.analyzePortfolio());
    }
    
    initBot() {
        this.botRenderer = new BotRenderer(this.elements.canvas);
        this.botRenderer.setAnimationState('idle');
        this.sayBotMessage("Hello! I'm your 3D trading assistant. Add stocks to your portfolio to get started!");
    }
    
    connectWebSocket() {
        try {
            this.ws = new WebSocket(this.webSocketUrl);
            
            this.ws.onopen = () => {
                this.updateConnectionStatus(true);
                this.sayBotMessage("Connected to market data!");
            };
            
            this.ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handleMarketUpdate(data);
            };
            
            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.updateConnectionStatus(false);
            };
            
            this.ws.onclose = () => {
                this.updateConnectionStatus(false);
                setTimeout(() => this.connectWebSocket(), 3000);
            };
        } catch (error) {
            console.error('Failed to connect WebSocket:', error);
            this.updateConnectionStatus(false);
        }
    }
    
    updateConnectionStatus(connected) {
        if (connected) {
            this.elements.connectionStatus.textContent = '● Connected';
            this.elements.connectionStatus.classList.add('connected');
        } else {
            this.elements.connectionStatus.textContent = '● Disconnected';
            this.elements.connectionStatus.classList.remove('connected');
        }
    }
    
    async addToPortfolio() {
        const ticker = this.elements.portfolioInput.value.toUpperCase().trim();
        
        if (!ticker || ticker.length === 0) {
            this.sayBotMessage("Please enter a stock ticker symbol!");
            return;
        }
        
        if (this.portfolio.some(item => item.ticker === ticker)) {
            this.sayBotMessage(`${ticker} is already in your portfolio!`);
            return;
        }
        
        this.botRenderer.setAnimationState('thinking');
        this.sayBotMessage(`Fetching data for ${ticker}...`);
        
        try {
            const response = await fetch(`${this.apiBaseUrl}/stock/${ticker}`);
            if (!response.ok) throw new Error('Stock not found');
            
            const data = await response.json();
            
            const portfolioItem = {
                ticker,
                currentPrice: data.currentPrice,
                previousClose: data.previousClose,
                change: data.change,
                changePercent: data.changePercent,
                addedAt: new Date()
            };
            
            this.portfolio.push(portfolioItem);
            this.elements.portfolioInput.value = '';
            this.renderPortfolio();
            this.updateStats();
            
            this.botRenderer.setAnimationState('excited');
            this.sayBotMessage(`Great! Added ${ticker} to your portfolio. Current price: $${data.currentPrice.toFixed(2)}`);
            
            setTimeout(() => {
                this.botRenderer.setAnimationState('idle');
            }, 2000);
        } catch (error) {
            console.error('Error adding stock:', error);
            this.botRenderer.setAnimationState('worried');
            this.sayBotMessage(`Couldn't find ${ticker}. Please check the ticker symbol!`);
        }
    }
    
    removeFromPortfolio(ticker) {
        this.portfolio = this.portfolio.filter(item => item.ticker !== ticker);
        this.renderPortfolio();
        this.updateStats();
        this.sayBotMessage(`Removed ${ticker} from portfolio.`);
    }
    
    renderPortfolio() {
        this.elements.portfolioList.innerHTML = '';
        
        if (this.portfolio.length === 0) {
            this.elements.portfolioList.innerHTML = '<li style="text-align: center; opacity: 0.5;">No stocks added yet</li>';
            return;
        }
        
        this.portfolio.forEach(item => {
            const li = document.createElement('li');
            
            const changeColor = item.change >= 0 ? '#00ff96' : '#ff6464';
            const changeSymbol = item.change >= 0 ? '▲' : '▼';
            
            li.innerHTML = `
                <span class="ticker-symbol">${item.ticker}</span>
                <span style="color: ${changeColor}; font-size: 12px;">
                    ${changeSymbol} ${Math.abs(item.changePercent).toFixed(2)}%
                </span>
                <button class="remove-btn">Remove</button>
            `;
            
            li.querySelector('.remove-btn').addEventListener('click', () => {
                this.removeFromPortfolio(item.ticker);
            });
            
            this.elements.portfolioList.appendChild(li);
        });
    }
    
    updateStats() {
        const totalValue = this.portfolio.reduce((sum, item) => sum + item.currentPrice, 0);
        const totalGain = this.portfolio.reduce((sum, item) => sum + item.change, 0);
        
        this.elements.totalValue.textContent = `$${totalValue.toFixed(2)}`;
        this.elements.totalGain.textContent = `${totalGain >= 0 ? '+' : ''}${totalGain.toFixed(2)}`;
        this.elements.totalGain.style.color = totalGain >= 0 ? '#00ff96' : '#ff6464';
    }
    
    async analyzePortfolio() {
        if (this.portfolio.length === 0) {
            this.sayBotMessage("Add some stocks to your portfolio first!");
            return;
        }
        
        this.botRenderer.setAnimationState('thinking');
        this.sayBotMessage("Analyzing your portfolio...");
        
        try {
            const tickers = this.portfolio.map(item => item.ticker);
            const response = await fetch(`${this.apiBaseUrl}/analyze`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ tickers })
            });
            
            if (!response.ok) throw new Error('Analysis failed');
            
            const analysis = await response.json();
            this.displayAnalysis(analysis);
            
            this.botRenderer.setAnimationState('explaining');
            this.sayBotMessage(analysis.summary);
            
            setTimeout(() => {
                this.botRenderer.setAnimationState('idle');
            }, 3000);
        } catch (error) {
            console.error('Analysis error:', error);
            this.botRenderer.setAnimationState('worried');
            this.sayBotMessage("Sorry, I couldn't analyze your portfolio right now. Try again later!");
        }
    }
    
    displayAnalysis(analysis) {
        const entry = document.createElement('div');
        entry.className = `analysis-entry ${analysis.scenario}`;
        
        const timestamp = new Date().toLocaleTimeString();
        
        entry.innerHTML = `
            <div class="analysis-entry-header">
                <span class="ticker">${analysis.tickers.join(', ')}</span>
                <span class="scenario">${analysis.scenario.toUpperCase()}</span>
                <span class="time">${timestamp}</span>
            </div>
            <div class="analysis-entry-content">
                ${analysis.details}
            </div>
            <div class="analysis-entry-footer">
                <span class="price-change ${analysis.recommendation.includes('SELL') ? 'negative' : 'positive'}">
                    ${analysis.recommendation}
                </span>
                <span class="confidence">Confidence: ${(analysis.confidence * 100).toFixed(0)}%</span>
            </div>
        `;
        
        this.elements.analysisHistory.insertBefore(entry, this.elements.analysisHistory.firstChild);
        
        // Keep only last 10 entries
        while (this.elements.analysisHistory.children.length > 10) {
            this.elements.analysisHistory.removeChild(this.elements.analysisHistory.lastChild);
        }
    }
    
    handleMarketUpdate(data) {
        const portfolioItem = this.portfolio.find(item => item.ticker === data.ticker);
        
        if (portfolioItem) {
            portfolioItem.currentPrice = data.price;
            portfolioItem.change = data.price - portfolioItem.previousClose;
            portfolioItem.changePercent = (portfolioItem.change / portfolioItem.previousClose) * 100;
            
            this.renderPortfolio();
            this.updateStats();
            
            // Significant price movement
            if (Math.abs(portfolioItem.changePercent) > 2) {
                this.handleSignificantMovement(data);
            }
        }
    }
    
    handleSignificantMovement(data) {
        const isUp = data.price > data.previousPrice;
        
        if (isUp) {
            this.botRenderer.setAnimationState('excited');
            this.sayBotMessage(`${data.ticker} is pumping! Up ${Math.abs(data.changePercent).toFixed(2)}%!`);
        } else {
            this.botRenderer.setAnimationState('worried');
            this.sayBotMessage(`Watch out! ${data.ticker} dipped ${Math.abs(data.changePercent).toFixed(2)}%.`);
        }
        
        setTimeout(() => {
            this.botRenderer.setAnimationState('idle');
        }, 2000);
    }
    
    sayBotMessage(message) {
        this.elements.speechText.textContent = message;
        this.elements.speechBubble.style.display = 'block';
        
        setTimeout(() => {
            this.elements.speechBubble.style.display = 'none';
        }, 4000);
    }
    
    loadPortfolio() {
        const saved = localStorage.getItem('portfolio');
        if (saved) {
            this.portfolio = JSON.parse(saved);
            this.renderPortfolio();
            this.updateStats();
        }
    }
    
    savePortfolio() {
        localStorage.setItem('portfolio', JSON.stringify(this.portfolio));
    }
}

// Initialize the application when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.app = new TradingAssistant();
    
    // Save portfolio periodically
    setInterval(() => {
        window.app.savePortfolio();
    }, 5000);
});
