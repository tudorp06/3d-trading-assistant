import os
from dotenv import load_dotenv
from pydantic import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    # API Keys
    finnhub_api_key: str = os.getenv("FINNHUB_API_KEY", "")
    polygon_api_key: str = os.getenv("POLYGON_API_KEY", "")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    twitter_bearer_token: str = os.getenv("TWITTER_BEARER_TOKEN", "")
    
    # LLM Config
    llm_model: str = os.getenv("LLM_MODEL", "gpt-4o-mini")
    llm_provider: str = os.getenv("LLM_PROVIDER", "openai")
    
    # Volatility Thresholds
    volatility_threshold_percent: float = float(os.getenv("VOLATILITY_THRESHOLD_PERCENT", "2.5"))
    volatility_threshold_price: float = float(os.getenv("VOLATILITY_THRESHOLD_PRICE", "5.0"))
    
    # Timing
    monitor_interval_minutes: int = int(os.getenv("MONITOR_INTERVAL_MINUTES", "1"))
    cooldown_minutes: int = int(os.getenv("COOLDOWN_MINUTES", "15"))
    news_lookback_minutes: int = int(os.getenv("NEWS_LOOKBACK_MINUTES", "10"))
    
    # Database
    db_path: str = os.getenv("DB_PATH", "./data/cache.db")
    
    # Tickers
    monitor_tickers: list = os.getenv("MONITOR_TICKERS", "NVDA,AAPL,VOO,TSLA,MSFT").split(",")
    
    class Config:
        env_file = ".env"

settings = Settings()
