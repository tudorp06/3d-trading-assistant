import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from config import settings
import os

logger = logging.getLogger(__name__)

class CacheManager:
    """Manager pentru cache local + cooldown tracking cu SQLite"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or settings.db_path
        self.cooldown_minutes = settings.cooldown_minutes
        self._init_db()
    
    def _init_db(self):
        """Inițializează baza de date SQLite"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabel pentru cache analize
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analysis_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL,
                scenario TEXT NOT NULL,
                analysis_text TEXT NOT NULL,
                confidence REAL,
                key_factors TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(ticker, scenario)
            )
        """)
        
        # Tabel pentru cooldown tracking
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cooldown_tracker (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL UNIQUE,
                last_trigger_at TIMESTAMP NOT NULL,
                scenario TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
        logger.info(f"✅ Database initialized at {self.db_path}")
    
    def save_analysis(self, ticker: str, scenario: str, analysis: Dict[str, Any]) -> bool:
        """Salvează o analiză LLM în cache"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            analysis_text = analysis.get("analysis", "")
            confidence = analysis.get("confidence", 0.5)
            key_factors = json.dumps(analysis.get("key_factors", []))
            
            cursor.execute("""
                INSERT OR REPLACE INTO analysis_cache 
                (ticker, scenario, analysis_text, confidence, key_factors)
                VALUES (?, ?, ?, ?, ?)
            """, (ticker, scenario, analysis_text, confidence, key_factors))
            
            conn.commit()
            conn.close()
            
            logger.info(f"💾 Analysis cached for {ticker} ({scenario})")
            return True
        
        except Exception as e:
            logger.error(f"Error saving analysis: {e}")
            return False
    
    def get_cached_analysis(self, ticker: str, scenario: str) -> Optional[Dict[str, Any]]:
        """Retrieves a cached analysis if available and not expired"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT analysis_text, confidence, key_factors, created_at 
                FROM analysis_cache 
                WHERE ticker = ? AND scenario = ?
                ORDER BY created_at DESC LIMIT 1
            """, (ticker, scenario))
            
            row = cursor.fetchone()
            conn.close()
            
            if not row:
                return None
            
            analysis_text, confidence, key_factors_json, created_at = row
            
            # Verifică dacă cache nu e expirat (30 ore)
            created = datetime.fromisoformat(created_at)
            if datetime.now() - created > timedelta(hours=30):
                logger.info(f"Cache expired for {ticker}")
                return None
            
            logger.info(f"📖 Cached analysis found for {ticker}")
            return {
                "analysis": analysis_text,
                "confidence": confidence,
                "key_factors": json.loads(key_factors_json or "[]"),
                "from_cache": True,
                "cached_at": created_at
            }
        
        except Exception as e:
            logger.error(f"Error retrieving cache: {e}")
            return None
    
    def set_cooldown(self, ticker: str, scenario: str) -> bool:
        """Marchează un ticker în cooldown pentru a evita spam-ul de API"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO cooldown_tracker (ticker, last_trigger_at, scenario)
                VALUES (?, ?, ?)
            """, (ticker, datetime.now(), scenario))
            
            conn.commit()
            conn.close()
            
            logger.info(f"❄️ Cooldown set for {ticker} ({self.cooldown_minutes} min)")
            return True
        
        except Exception as e:
            logger.error(f"Error setting cooldown: {e}")
            return False
    
    def is_in_cooldown(self, ticker: str) -> bool:
        """Verifică dacă un ticker este în cooldown"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT last_trigger_at FROM cooldown_tracker WHERE ticker = ?
            """, (ticker,))
            
            row = cursor.fetchone()
            conn.close()
            
            if not row:
                return False
            
            last_trigger = datetime.fromisoformat(row[0])
            cooldown_end = last_trigger + timedelta(minutes=self.cooldown_minutes)
            
            if datetime.now() < cooldown_end:
                logger.info(f"⏳ {ticker} still in cooldown (expires at {cooldown_end})")
                return True
            
            return False
        
        except Exception as e:
            logger.error(f"Error checking cooldown: {e}")
            return False
    
    def get_all_cached(self) -> list:
        """Returnează toate analizele cached"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT ticker, scenario, analysis_text, created_at 
                FROM analysis_cache ORDER BY created_at DESC
            """)
            
            rows = cursor.fetchall()
            conn.close()
            
            return [
                {
                    "ticker": row[0],
                    "scenario": row[1],
                    "analysis": row[2],
                    "created_at": row[3]
                }
                for row in rows
            ]
        
        except Exception as e:
            logger.error(f"Error retrieving all cached: {e}")
            return []
