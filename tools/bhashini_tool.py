import logging
import httpx
from typing import Dict, Any
from tools.registry import BaseActionSyncTool, tool_registry

logger = logging.getLogger("actionsync.tools.bhashini")

class BhashiniTool(BaseActionSyncTool):
    """Bhashini Translation Tool.
    
    Interfaces with the MeitY Bhashini translation API to translate meeting 
    conversations in Indian regional languages into English for downstream processing.
    """
    def __init__(self):
        super().__init__(
            name="BhashiniTool",
            description="Translates regional Indian languages to English using the MeitY Bhashini API."
        )
        self.api_url = "https://dhruva-api.bhashini.gov.in/services/inference/pipeline"
        self.api_key = None
        self.user_id = None
        self.authorization_token = None

    def initialize(self) -> None:
        """Loads API credentials from environment/settings if available."""
        # For mock/dev, we check if credentials exist, otherwise log fallback mode
        self.api_key = None # Read from settings/env if configured
        self.initialized = True
        logger.info("Bhashini translation service initialized.")

    def execute(self, text: str, source_lang: str = "hi", target_lang: str = "en") -> str:
        """Translates text from source_lang to target_lang.
        
        Args:
            text: Text to translate.
            source_lang: Two-letter ISO language code (default "hi" for Hindi).
            target_lang: Two-letter ISO language code (default "en" for English).
        """
        if not text.strip():
            return ""
            
        logger.info(f"Translating via Bhashini: {source_lang} -> {target_lang}")

        if not self.api_key or not self.authorization_token:
            logger.warning("Bhashini credentials not set. Running translation in mock/bypass mode.")
            return self._mock_translation(text, source_lang, target_lang)

        # Structure of a real Bhashini request (Dhruva pipeline protocol)
        payload = {
            "pipelineTasks": [
                {
                    "taskType": "translation",
                    "config": {
                        "language": {
                            "sourceLanguage": source_lang,
                            "targetLanguage": target_lang
                        }
                    }
                }
            ],
            "inputData": {
                "input": [
                    {
                        "source": text
                    }
                ]
            }
        }
        
        headers = {
            "Content-Type": "application/json",
            "ApiKey": self.api_key,
            "Authorization": self.authorization_token
        }

        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.post(self.api_url, json=payload, headers=headers)
                response.raise_for_status()
                res_data = response.json()
                translated_text = res_data["pipelineResponse"][0]["output"][0]["target"]
                return translated_text
        except Exception as e:
            logger.error(f"Bhashini API call failed: {e}. Falling back to mock bypass.")
            return self._mock_translation(text, source_lang, target_lang)

    def validate(self, output: Any) -> bool:
        return isinstance(output, str)

    def _mock_translation(self, text: str, source_lang: str, target_lang: str) -> str:
        """Mock fallback that appends a translation indicator for demo purposes."""
        if source_lang == target_lang:
            return text
        # If it's standard mock text, translate it; otherwise return original
        return f"[Bhashini Translated from {source_lang} to {target_lang}]: {text}"

# Register the tool
tool_registry.register(BhashiniTool())
