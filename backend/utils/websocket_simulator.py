import asyncio
import random
from datetime import datetime
from typing import Callable

class WebSocketSimulator:
    """
    Simulator WebSocket pentru testing fără conexiune reală la Finnhub/Polygon
    Generează update-uri de preț realiste cu volatilitate și volume variabile
    """
    
    def __init__(
        self,
        tickers: list = ["NVDA", "AAPL", "TSLA", "VOO"],
        update_interval_seconds: float = 0.5,
    ):
        self.tickers = tickers
        self.update_interval = update_interval_seconds
        self.prices = {ticker: random.uniform(100, 250) for ticker in tickers}
        self.callbacks = []
        self.running = False
    
    def register_callback(self, callback: Callable):
        """Registrează o funcție callback pentru primire de update-uri de preț"""
        self.callbacks.append(callback)
    
    async def start_stream(self):
        """Pornește stream-ul de preț simulat"""
        self.running = True
        print(f"🌐 WebSocket Simulator started for {self.tickers}")
        
        while self.running:
            for ticker in self.tickers:
                # Random walk pentru preț (±1-3%)
                change_percent = random.uniform(-0.03, 0.03)
                new_price = self.prices[ticker] * (1 + change_percent)
                self.prices[ticker] = new_price
                
                # Volume aleatoriu
                volume = random.randint(500000, 5000000)
                
                # Apelează callback-urile
                price_data = {
                    "ticker": ticker,
                    "price": round(new_price, 2),
                    "timestamp": datetime.now().isoformat(),
                    "volume": volume,
                }
                
                for callback in self.callbacks:
                    await callback(price_data)
            
            await asyncio.sleep(self.update_interval)
    
    def stop_stream(self):
        """Oprește stream-ul"""
        self.running = False
        print("❌ WebSocket Simulator stopped")
    
    async def simulate_spike(self, ticker: str, percent_change: float, duration_seconds: float = 2):
        """
        Simulează o mișcare bruscă de preț (util pentru testing trigger-urilor)
        
        Args:
            ticker: Simbolul acțiunii
            percent_change: Procentul de schimbare (ex: -2.5 pentru -2.5%)
            duration_seconds: Durata spike-ului
        """
        start_price = self.prices[ticker]
        target_price = start_price * (1 + percent_change / 100)
        steps = int(duration_seconds / self.update_interval)
        
        print(f"\n📈 Simulating spike for {ticker}: {percent_change:+.2f}%")
        
        for step in range(steps):
            progress = (step + 1) / steps
            current_price = start_price + (target_price - start_price) * progress
            self.prices[ticker] = current_price
            
            volume = random.randint(8000000, 15000000)  # Volume mare pe spike
            
            price_data = {
                "ticker": ticker,
                "price": round(current_price, 2),
                "timestamp": datetime.now().isoformat(),
                "volume": volume,
            }
            
            for callback in self.callbacks:
                await callback(price_data)
            
            await asyncio.sleep(self.update_interval)


# Example de utilizare
async def example_usage():
    simulator = WebSocketSimulator()
    
    # Callback simplu
    async def on_price_update(data):
        print(f"Price update: {data['ticker']} - {data['price']}$")
    
    simulator.register_callback(on_price_update)
    
    # Porneștestream în background
    stream_task = asyncio.create_task(simulator.start_stream())
    
    # După 5 secunde, simulează o scădere
    await asyncio.sleep(5)
    await simulator.simulate_spike("NVDA", -2.5, duration_seconds=2)
    
    # Continuă streamul
    await asyncio.sleep(10)
    simulator.stop_stream()
    await stream_task

if __name__ == "__main__":
    asyncio.run(example_usage())
