import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Optional
from enum import Enum

logger = logging.getLogger(__name__)

class TriggerType(str, Enum):
    DIP = "DIP"  # Scădere
    PUMP = "PUMP"  # Creștere
    HALTED = "HALTED"  # Circuit breaker

@dataclass
class PricePoint:
    """Reprezentare punct de preț în timp real"""
    ticker: str
    price: float
    timestamp: datetime
    volume: int
    previous_price: Optional[float] = None
    
class VolatilityTrigger:
    """Monitorizare volatilitate și declanșare de evenimente"""
    
    def __init__(
        self, 
        volatility_threshold_percent: float = 2.5,
        volatility_threshold_price: float = 5.0,
        monitor_interval: int = 60  # secunde
    ):
        self.volatility_threshold_percent = volatility_threshold_percent
        self.volatility_threshold_price = volatility_threshold_price
        self.monitor_interval = monitor_interval
        
        # Stare pentru fiecare ticker
        self.price_history = {}  # ticker -> [PricePoint]
        self.last_triggered = {}  # ticker -> datetime (pentru cooldown)
        self.callbacks = []  # funcții callback pentru trigger
        
    def register_callback(self, callback: Callable):
        """Registrează o funcție callback pentru când se declanșează un trigger"""
        self.callbacks.append(callback)
        
    async def on_price_update(self, price_point: PricePoint):
        """Primește o actualizare de preț și verifică dacă trebuie să declanșeze evento"""
        ticker = price_point.ticker
        
        # Inițializează istoric dacă nu există
        if ticker not in self.price_history:
            self.price_history[ticker] = []
        
        # Adaugă punctul de preț la istoric (păstrează doar ultimele 200 puncte)
        self.price_history[ticker].append(price_point)
        if len(self.price_history[ticker]) > 200:
            self.price_history[ticker].pop(0)
        
        # Analizează volatilitatea
        trigger_info = self._analyze_volatility(ticker)
        
        if trigger_info:
            logger.info(f"🚨 TRIGGER DECLANȘAT: {ticker} - {trigger_info['type']}")
            await self._fire_callbacks(trigger_info)
    
    def _analyze_volatility(self, ticker: str) -> Optional[dict]:
        """Analizează volatilitatea și returnează info trigger dacă e necesar"""
        if ticker not in self.price_history or len(self.price_history[ticker]) < 2:
            return None
        
        history = self.price_history[ticker]
        current = history[-1]
        previous = history[-2]
        
        price_change = current.price - previous.price
        percent_change = (price_change / previous.price) * 100
        
        # Verifică dacă depășește threshold
        if abs(price_change) >= self.volatility_threshold_price or abs(percent_change) >= self.volatility_threshold_percent:
            trigger_type = TriggerType.DIP if price_change < 0 else TriggerType.PUMP
            
            return {
                "ticker": ticker,
                "type": trigger_type,
                "current_price": current.price,
                "previous_price": previous.price,
                "price_change": price_change,
                "percent_change": percent_change,
                "volume": current.volume,
                "timestamp": current.timestamp,
                "price_history": history[-10:],  # Ultimele 10 puncte
            }
        
        return None
    
    async def _fire_callbacks(self, trigger_info: dict):
        """Apelează toți callback-urile registrate"""
        tasks = [callback(trigger_info) for callback in self.callbacks]
        await asyncio.gather(*tasks, return_exceptions=True)
    
    def get_price_momentum(self, ticker: str, window: int = 5) -> Optional[float]:
        """Calculează momentum-ul prețului pentru ultimele N puncte"""
        if ticker not in self.price_history or len(self.price_history[ticker]) < window:
            return None
        
        history = self.price_history[ticker]
        prices = [p.price for p in history[-window:]]
        
        if len(prices) < 2:
            return None
        
        # Momentum = (Preț actual - Preț cu N puncte în spate) / Preț cu N puncte în spate
        momentum = ((prices[-1] - prices[0]) / prices[0]) * 100
        return momentum
