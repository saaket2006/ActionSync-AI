import pytest
from unittest.mock import MagicMock, patch
import tools.bhashini_tool  # Registers BhashiniTool in the registry
from utils.translator import translate_text

def test_translate_english_to_english():
    text = "Hello world"
    res = translate_text(text, "en")
    assert res == text

def test_translate_bhashini_fallback():
    # Translating to Hindi (hi) which is an Indic language
    text = "Hello world"
    res = translate_text(text, "hi")
    # Since Bhashini API credentials are not set, it should run in mock bypass mode
    assert "[Bhashini Translated from en to hi]" in res

@patch("utils.translator.Client")
def test_translate_gemini_fallback(mock_client_class):
    # Set up mock Gemini client and response
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client
    
    mock_response = MagicMock()
    mock_response.text = "Hola Mundo"
    mock_client.models.generate_content.return_value = mock_response
    
    from config.settings import settings
    # Temporarily set API key to trigger Gemini translation path
    old_key = settings.GEMINI_API_KEY
    settings.GEMINI_API_KEY = "mock_key"
    
    try:
        text = "Hello world"
        res = translate_text(text, "es")  # Spanish is a global language
        assert res == "Hola Mundo"
        mock_client.models.generate_content.assert_called_once()
    finally:
        settings.GEMINI_API_KEY = old_key
