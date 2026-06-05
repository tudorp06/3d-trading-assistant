import json
import logging
from typing import Optional, Dict, Any
from config import settings

logger = logging.getLogger(__name__)

class LLMClient:
    """Client pentru comunicarea cu LLM-uri (OpenAI / Google Gemini)"""
    
    def __init__(self):
        self.provider = settings.llm_provider
        self.model = settings.llm_model
        
        if self.provider == "openai":
            from openai import AsyncOpenAI
            self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        elif self.provider == "gemini":
            import google.generativeai as genai
            genai.configure(api_key=settings.gemini_api_key)
            self.client = genai  # Gemini use async differently
        else:
            raise ValueError(f"Unknown LLM provider: {self.provider}")
    
    async def generate_analysis(self, system_prompt: str, user_prompt: str) -> Optional[Dict[str, Any]]:
        """
        Trimite prompt-ul la LLM și primește analiza
        
        Args:
            system_prompt: Instrucțiuni de sistem
            user_prompt: Prompt-ul utilizatorului cu context
        
        Returns:
            Dict cu response parsificat sau None dacă eroare
        """
        try:
            if self.provider == "openai":
                return await self._query_openai(system_prompt, user_prompt)
            elif self.provider == "gemini":
                return await self._query_gemini(system_prompt, user_prompt)
        except Exception as e:
            logger.error(f"Eroare la LLM query: {e}")
            return None
    
    async def _query_openai(self, system_prompt: str, user_prompt: str) -> Optional[Dict[str, Any]]:
        """Query către OpenAI GPT-4o-mini"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.7,
                max_tokens=150,  # Max 3 propoziții
                response_format={"type": "json_object"}  # Forțează JSON response
            )
            
            content = response.choices[0].message.content
            parsed = json.loads(content)
            
            logger.info(f"✅ OpenAI Response: {parsed}")
            return parsed
        
        except json.JSONDecodeError:
            logger.warning("Response nu e valid JSON, returnez raw text")
            return {
                "analysis": response.choices[0].message.content,
                "confidence": 0.8,
                "key_factors": []
            }
    
    async def _query_gemini(self, system_prompt: str, user_prompt: str) -> Optional[Dict[str, Any]]:
        """Query către Google Gemini 1.5 Flash"""
        try:
            model = self.client.GenerativeModel(self.model)
            
            full_prompt = f"{system_prompt}\n\nContext:\n{user_prompt}"
            
            response = model.generate_content(
                full_prompt,
                generation_config={
                    "temperature": 0.7,
                    "max_output_tokens": 150,
                }
            )
            
            content = response.text
            
            # Încearcă să parsezi JSON, altfel returnează ca text
            try:
                parsed = json.loads(content)
            except json.JSONDecodeError:
                parsed = {
                    "analysis": content,
                    "confidence": 0.8,
                    "key_factors": []
                }
            
            logger.info(f"✅ Gemini Response: {parsed}")
            return parsed
        
        except Exception as e:
            logger.error(f"Eroare Gemini: {e}")
            return None
