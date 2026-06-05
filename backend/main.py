import asyncio
import logging
from datetime import datetime
from volatility_trigger import VolatilityTrigger, PricePoint, TriggerType
from prompt_generator import PromptGenerator, PromptContext, ScenarioType
from llm_client import LLMClient
from cache_manager import CacheManager
from config import settings

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TradingAssistant:
    """Orchestrator principal pentru Trading Assistant"""
    
    def __init__(self):
        self.volatility_trigger = VolatilityTrigger(
            volatility_threshold_percent=settings.volatility_threshold_percent,
            volatility_threshold_price=settings.volatility_threshold_price,
        )
        self.prompt_generator = PromptGenerator()
        self.llm_client = LLMClient()
        self.cache_manager = CacheManager()
        
        # Registrează callback-ul pentru trigger-uri
        self.volatility_trigger.register_callback(self.on_volatility_trigger)
    
    async def on_volatility_trigger(self, trigger_info: dict):
        """Callback declanșat când volatilitatea depășește threshold"""
        ticker = trigger_info["ticker"]
        trigger_type = trigger_info["type"]
        
        logger.info(f"🎯 Processing trigger for {ticker} ({trigger_type})")
        
        # Verifică dacă e în cooldown
        if self.cache_manager.is_in_cooldown(ticker):
            logger.warning(f"⏳ {ticker} în cooldown, skip")
            return
        
        # Mapează TriggerType la ScenarioType
        scenario = ScenarioType.DIP if trigger_type == TriggerType.DIP else ScenarioType.PUMP
        
        # Verifică dacă avem deja o analiză cached
        cached = self.cache_manager.get_cached_analysis(ticker, scenario.value)
        if cached:
            logger.info(f"📖 Using cached analysis for {ticker}")
            await self.display_analysis(cached, trigger_info)
            return
        
        # Generează prompt dinamic
        momentum = self.volatility_trigger.get_price_momentum(ticker, window=5)
        
        context = PromptContext(
            ticker=ticker,
            scenario=scenario,
            current_price=trigger_info["current_price"],
            previous_price=trigger_info["previous_price"],
            percent_change=trigger_info["percent_change"],
            volume=trigger_info["volume"],
            news_headlines=[],  # TODO: Fetch from scraper
            twitter_mentions=[],  # TODO: Fetch from scraper
            momentum=momentum,
        )
        
        prompt_data = self.prompt_generator.generate_prompt(context)
        
        logger.info(f"📝 Generated prompt for {ticker}")
        logger.debug(f"Scenario: {prompt_data['scenario']}")
        logger.debug(f"User Prompt (truncated): {prompt_data['user_prompt'][:200]}...")
        
        # Query LLM
        analysis = await self.llm_client.generate_analysis(
            prompt_data["system_prompt"],
            prompt_data["user_prompt"]
        )
        
        if analysis:
            # Salvează în cache
            self.cache_manager.save_analysis(ticker, scenario.value, analysis)
            
            # Set cooldown
            self.cache_manager.set_cooldown(ticker, scenario.value)
            
            # Display analysis
            await self.display_analysis(analysis, trigger_info)
        else:
            logger.error(f"❌ LLM failed to generate analysis for {ticker}")
    
    async def display_analysis(self, analysis: dict, trigger_info: dict):
        """Afișează analiza în format ready for 3D bot"""
        print("\n" + "="*60)
        print(f"🤖 ANÁLYSIS FOR {trigger_info['ticker']}")
        print("="*60)
        print(f"Price Move: {trigger_info['percent_change']:+.2f}% "
              f"({trigger_info['previous_price']}$ → {trigger_info['current_price']}$)")
        print(f"Volume: {trigger_info['volume']:,} shares")
        print(f"From Cache: {analysis.get('from_cache', False)}")
        print("\n📢 BOT RESPONSE (Max 3 sentences):")
        print("-" * 60)
        print(analysis.get("analysis", "No analysis available"))
        print("-" * 60)
        if analysis.get("key_factors"):
            print(f"\n🔑 Key Factors: {', '.join(analysis['key_factors'])}")
        print(f"Confidence: {analysis.get('confidence', 0) * 100:.0f}%")
        print("\n")
    
    async def simulate_price_update(self, ticker: str, price: float, volume: int):
        """Simulează o actualizare de preț (pentru testing)"""
        price_point = PricePoint(
            ticker=ticker,
            price=price,
            timestamp=datetime.now(),
            volume=volume,
        )
        await self.volatility_trigger.on_price_update(price_point)


async def main():
    """Main entry point - Demo cu simulare de preț"""
    logger.info("🚀 Starting 3D AI Trading Assistant MVP")
    
    assistant = TradingAssistant()
    
    # DEMO: Simulare NVDA dip de la 220 la 215 (-2.27%)
    print("\n📊 DEMO SCENARIO: NVDA Dip")
    print("Simulating: NVDA 220$ → 215$ (-2.27%)\n")
    
    await assistant.simulate_price_update("NVDA", 220.0, 5000000)
    await asyncio.sleep(0.1)  # Mic delay
    await assistant.simulate_price_update("NVDA", 215.0, 8000000)
    
    # DEMO: AAPL Pump
    print("\n📊 DEMO SCENARIO: AAPL Pump")
    print("Simulating: AAPL 180$ → 185$ (+2.78%)\n")
    
    await assistant.simulate_price_update("AAPL", 180.0, 3000000)
    await asyncio.sleep(0.1)
    await assistant.simulate_price_update("AAPL", 185.0, 5000000)
    
    # Await pentru a-și termina callbacks
    await asyncio.sleep(2)
    logger.info("✅ Demo completed")

if __name__ == "__main__":
    asyncio.run(main())
