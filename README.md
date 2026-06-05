# 3D AI Trading Assistant - MVP Backend

Aplicație mobilă (web) de trading personalizată cu AI Assistant 3D animat care oferă analiză critică în timp real.

## Caracteristici

1. **Event-Driven Volatility Trigger** - Monitorizare prețuri prin Websocket
2. **Real-time News Scraping** - Integrare Reuters/Bloomberg + Twitter API
3. **Dynamic Prompt Generation** - LLM-powered analiză financiară
4. **Cooldown & Caching** - Optimizare costuri API
5. **3D Bot Animation** - Frontend cu bot 3D animat

## Arhitectură

```
├── backend/
│   ├── main.py                    # Entry point
│   ├── config.py                  # Configurare API keys
│   ├── volatility_trigger.py      # Event-driven trigger logic
│   ├── prompt_generator.py        # Dynamic prompt assembly
│   ├── llm_client.py              # LLM integration (OpenAI/Gemini)
│   ├── news_scraper.py            # News & Twitter scraping
│   ├── cache_manager.py           # SQLite cache + cooldown
│   └── utils/
│       └── websocket_simulator.py # Test Websocket simulator
├── frontend/
│   └── 3d-bot/                    # Three.js 3D bot (TBD)
├── requirements.txt
└── .env.example
```

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
# Completează API keys
python backend/main.py
```
