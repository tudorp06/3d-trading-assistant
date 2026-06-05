from enum import Enum
from dataclasses import dataclass
from typing import Optional
import json

class ScenarioType(str, Enum):
    DIP = "DIP"              # Scădere
    PUMP = "PUMP"            # Creștere
    HALTED = "HALTED"        # Circuit breaker

@dataclass
class PromptContext:
    """Context pentru generarea dinamică a prompt-ului"""
    ticker: str
    scenario: ScenarioType
    current_price: float
    previous_price: float
    percent_change: float
    volume: int
    news_headlines: list  # Lista de știri relevante
    twitter_mentions: list  # Lista de mentions pe Twitter
    momentum: Optional[float] = None
    circuit_breaker_reason: Optional[str] = None

class PromptGenerator:
    """Generator de prompt-uri dinamice pentru LLM"""
    
    # SYSTEM PROMPT - Instrucțiuni stricte pentru LLM
    SYSTEM_PROMPT = """
Tu ești un jurnalist financiar critic și un profesor de economie cu 20 de ani de experiență.
Rolul tău este să oferi ANALIZĂ CRITICĂ și explicații în timp real despre volatilitatea pieței.

REGULI STRICTE:
1. NU oferi TRADING ADVICE (fără "cumpără", "vinde", "hold", "investește")
2. Limbajul trebuie să fie RETROSPECTIV sau IPOTETIC ("Prețul scade probabil din cauză că...")
3. Răspunsul trebuie să fie SCURT: MAXIMUM 3 PROPOZIȚII
4. Limbaj tehnic dar accesibil pentru investitori pasivi
5. Dacă nu ai suficiente informații, spune-o clar: "Mișcare tehnică de algoritm sau lichidare de poziții"
6. Corelează cu știrile și contextul pieței DOAR dacă avem date concrete
7. EVITĂ speculațiile generice - fii specific și bazat pe date

Formatează răspunsul ca JSON cu câmpuri: "analysis", "confidence", "key_factors"
"""
    
    # Șablonul pentru scenariu DIP (Scădere)
    DIP_TEMPLATE = """
Contextul volatilității pentru {ticker}:
- Preț: {current_price}$ (Era: {previous_price}$)
- Scădere: {percent_change:.2f}% ({volume:,} acțiuni tranzacționate)
- Momentum ultimei 5 minute: {momentum:.2f}%

Ştiri recente ({lookback} minute):
{news_section}

Semnale din Twitter/X cashtag ${ticker}:
{twitter_section}

Vreți analiza critică: De ce SCADE {ticker}? E din cauza unei știri specifice, ori e o mișcare tehnică de algoritm (stop-loss hunt, lichidare)?
"""
    
    # Șablonul pentru scenariu PUMP (Creștere)
    PUMP_TEMPLATE = """
Contextul volatilității pentru {ticker}:
- Preț: {current_price}$ (Era: {previous_price}$)
- Creștere: {percent_change:.2f}% ({volume:,} acțiuni tranzacționate)
- Momentum ultimei 5 minute: {momentum:.2f}%

Ştiri recente ({lookback} minute):
{news_section}

Semnale din Twitter/X cashtag ${ticker}:
{twitter_section}

Vreți analiza critică: De ce CREȘTE {ticker}? E FOMO (Fear Of Missing Out), earnings peste așteptări, sau o pompă speculativă?
"""
    
    # Șablonul pentru scenariu HALTED (Circuit Breaker)
    HALTED_TEMPLATE = """
ALERTA: {ticker} a fost OPRIT din tranzacționare!

Motiv posibil: {circuit_breaker_reason}
Volume extreme: {volume:,} acțiuni
Mișcare: {percent_change:.2f}%

Contextul pieței:
{news_section}

Analizați: Ce panică sau extaz a provocat această oprire și ce implicații are aceasta?
"""
    
    def generate_prompt(self, context: PromptContext) -> dict:
        """
        Generează prompt-ul dinamic în funcție de scenario
        Returnează dict cu 'system_prompt' și 'user_prompt'
        """
        
        # Selectează template-ul în funcție de scenariul volatilității
        if context.scenario == ScenarioType.DIP:
            user_prompt = self._build_dip_prompt(context)
        elif context.scenario == ScenarioType.PUMP:
            user_prompt = self._build_pump_prompt(context)
        elif context.scenario == ScenarioType.HALTED:
            user_prompt = self._build_halted_prompt(context)
        else:
            user_prompt = "Context necunoscut"
        
        return {
            "system_prompt": self.SYSTEM_PROMPT,
            "user_prompt": user_prompt,
            "scenario": context.scenario.value,
            "ticker": context.ticker,
        }
    
    def _build_dip_prompt(self, context: PromptContext) -> str:
        """Asamblează prompt pentru scenariu DIP"""
        news_text = self._format_news(context.news_headlines)
        twitter_text = self._format_twitter(context.twitter_mentions)
        
        return self.DIP_TEMPLATE.format(
            ticker=context.ticker,
            current_price=context.current_price,
            previous_price=context.previous_price,
            percent_change=context.percent_change,
            volume=context.volume,
            momentum=context.momentum or 0,
            lookback=10,
            news_section=news_text if news_text else "[Fără știri relevante - verifică mai jos]",
            twitter_section=twitter_text if twitter_text else "[Fără mentions pe Twitter]",
        )
    
    def _build_pump_prompt(self, context: PromptContext) -> str:
        """Asamblează prompt pentru scenariu PUMP"""
        news_text = self._format_news(context.news_headlines)
        twitter_text = self._format_twitter(context.twitter_mentions)
        
        return self.PUMP_TEMPLATE.format(
            ticker=context.ticker,
            current_price=context.current_price,
            previous_price=context.previous_price,
            percent_change=context.percent_change,
            volume=context.volume,
            momentum=context.momentum or 0,
            lookback=10,
            news_section=news_text if news_text else "[Fără știri relevante]",
            twitter_section=twitter_text if twitter_text else "[Fără mentions pe Twitter]",
        )
    
    def _build_halted_prompt(self, context: PromptContext) -> str:
        """Asamblează prompt pentru scenariu HALTED (Circuit Breaker)"""
        news_text = self._format_news(context.news_headlines)
        
        return self.HALTED_TEMPLATE.format(
            ticker=context.ticker,
            circuit_breaker_reason=context.circuit_breaker_reason or "Volatilitate extremă",
            volume=context.volume,
            percent_change=context.percent_change,
            news_section=news_text if news_text else "[Context neclar]",
        )
    
    @staticmethod
    def _format_news(headlines: list) -> str:
        """Formatează lista de știri pentru prompt"""
        if not headlines:
            return ""
        
        formatted = ""
        for i, headline in enumerate(headlines[:5], 1):  # Max 5 știri
            if isinstance(headline, dict):
                formatted += f"{i}. {headline.get('title', 'N/A')}\n"
            else:
                formatted += f"{i}. {headline}\n"
        
        return formatted
    
    @staticmethod
    def _format_twitter(mentions: list) -> str:
        """Formatează mentions de pe Twitter/X pentru prompt"""
        if not mentions:
            return ""
        
        formatted = ""
        for i, mention in enumerate(mentions[:5], 1):  # Max 5 mentions
            if isinstance(mention, dict):
                formatted += f"{i}. @{mention.get('author', 'unknown')}: {mention.get('text', 'N/A')}\n"
            else:
                formatted += f"{i}. {mention}\n"
        
        return formatted
