import logging
from google.genai import Client
from config.settings import settings
from tools.registry import tool_registry

logger = logging.getLogger("actionsync.utils.translator")

def translate_text(text: str, target_lang: str, source_lang: str = "en") -> str:
    """Translates text from source_lang to target_lang.
    
    Uses BhashiniTool for Indic regional languages if target_lang is an Indian language,
    and falls back to Gemini API for global languages or Bhashini failures/mock environments.
    """
    if not text or not isinstance(text, str) or not text.strip():
        return text
        
    if target_lang == source_lang or target_lang == "en":
        return text

    # List of Indian regional language ISO codes that Bhashini supports
    indic_langs = {"hi", "ta", "te", "kn", "mr", "bn", "ml", "gu", "pa", "or", "as"}
    
    # Try Bhashini for Indic languages
    if target_lang in indic_langs:
        try:
            bhashini = tool_registry.get_tool("BhashiniTool")
            if bhashini:
                logger.info(f"Translating via Bhashini to {target_lang}...")
                translated = bhashini.execute(text, source_lang=source_lang, target_lang=target_lang)
                return translated
        except Exception as e:
            logger.error(f"Bhashini translation failed: {e}. Falling back to Gemini.")

    # Fallback/Global Language translation using Gemini
    if settings.GEMINI_API_KEY:
        try:
            client = Client(api_key=settings.GEMINI_API_KEY)
            prompt = (
                f"You are a professional translator. Translate the following text from {source_lang} to {target_lang}. "
                f"Maintain the original meaning, tone, formatting, and structure. Do not add any conversational "
                f"commentary, quotes, or metadata—only return the translated text.\n\nText:\n{text}"
            )
            response = client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=prompt
            )
            if response.text:
                return response.text.strip()
        except Exception as e:
            logger.error(f"Gemini translation failed: {e}")

    # Ultimate fallback: return original text
    return text
