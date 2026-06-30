import pytest
import os
from tools.registry import tool_registry, BaseActionSyncTool
from tools.whisper_tool import WhisperTool
from tools.bhashini_tool import BhashiniTool
from tools.doc_generator import DocumentGenerator
from tools.semantic_search import SemanticSearch

def test_registry_registration():
    class DummyTool(BaseActionSyncTool):
        def __init__(self):
            super().__init__("DummyTool", "Just a test tool")
        def execute(self, val):
            return val * 2
            
    dummy = DummyTool()
    tool_registry.register(dummy)
    
    assert tool_registry.get_tool("DummyTool") == dummy
    assert tool_registry.execute_tool("DummyTool", 5) == 10

def test_bhashini_translation_mock():
    tool = tool_registry.get_tool("BhashiniTool")
    assert isinstance(tool, BhashiniTool)
    res = tool.execute("नमस्ते", source_lang="hi", target_lang="en")
    assert "Bhashini Translated" in res or res == "नमस्ते"

def test_whisper_tool_mock():
    tool = tool_registry.get_tool("WhisperTool")
    assert isinstance(tool, WhisperTool)
    # Trigger transcription with mock file to test fallback/mock output
    res = tool._generate_mock_transcription("test_audio.mp3")
    assert "Welcome to the ActionSync AI" in res["text"]
    assert len(res["segments"]) > 0

def test_doc_generator_file_creation(tmp_path):
    # Override settings for report generation folder
    from config.settings import settings
    old_dir = settings.GENERATED_DOCS_DIR
    settings.GENERATED_DOCS_DIR = str(tmp_path)
    
    tool = tool_registry.get_tool("DocumentGenerator")
    assert isinstance(tool, DocumentGenerator)
    tool.initialize()
    
    mock_data = {
        "summarizer": {"executive_summary": "Test Summary", "key_topics": ["T1"], "meeting_context": "C1"},
        "decision": {"decisions": [{"title": "D1", "description": "Desc1", "decider_name": "User1"}]},
        "action_item": {"tasks": [{"title": "T1", "description": "Desc2", "assignee_name": "User2", "status": "Pending", "deadline": None}]},
        "risk": {"risks": [{"description": "R1", "impact_level": "High", "mitigation_strategy": "M1"}]},
        "timeline": {"events": []},
        "community_impact": {},
        "accountability": {},
        "clarification": {}
    }
    
    files = tool.execute("Test Meeting", mock_data)
    assert os.path.exists(files["markdown_path"])
    assert os.path.exists(files["pdf_path"])
    
    # Restore settings
    settings.GENERATED_DOCS_DIR = old_dir
