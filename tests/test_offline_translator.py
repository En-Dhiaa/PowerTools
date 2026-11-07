"""
Unit Tests for Offline Translator Engine
PowerTool Extended Edition
"""

import sys
import os
import socket
import pytest

# Ensure module directory is in path
MODULE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src", "modules", "OfflineTranslator"))
if MODULE_DIR not in sys.path:
    sys.path.insert(0, MODULE_DIR)

from OfflineTranslatorEngine import OfflineTranslator, ModelManager, ModelNotInstalledError


@pytest.fixture(scope="module")
def translator():
    mgr = ModelManager()
    return OfflineTranslator(mgr)


def test_arabic_to_english_translation(translator):
    """Verify Arabic to English offline translation"""
    arabic_text = "مرحبا، كيف حالك اليوم؟"
    res = translator.translate(arabic_text)
    assert res.from_code == "ar"
    assert res.to_code == "en"
    assert len(res.translated_text) > 0
    # Expected translation: Hi/Hello, how are you today?
    lower = res.translated_text.lower()
    assert "how are you" in lower or "today" in lower


def test_english_to_arabic_translation(translator):
    """Verify English to Arabic offline translation"""
    english_text = "I need to finish this project today."
    res = translator.translate(english_text)
    assert res.from_code == "en"
    assert res.to_code == "ar"
    assert len(res.translated_text) > 0
    # Should produce Arabic text
    has_arabic = any(0x0600 <= ord(ch) <= 0x06FF for ch in res.translated_text)
    assert has_arabic is True


def test_empty_and_whitespace_input(translator):
    """Verify empty text or spaces return empty results without crashing"""
    assert translator.translate("").translated_text == ""
    assert translator.translate("   ").translated_text == ""
    assert translator.translate("\n\t").translated_text == ""


def test_multiple_lines_preservation(translator):
    """Verify multi-line paragraphs retain line breaks in translation"""
    text = "Good morning.\nHow are you?\nWelcome to PowerTool."
    res = translator.translate(text, from_code="en", to_code="ar")
    lines = res.translated_text.split("\n")
    assert len(lines) == 3


def test_arabic_diacritics_handling(translator):
    """Verify text with Harakat / Tashkeel translates correctly"""
    text_with_harakat = "مَرْحَبًا بِكُمْ فِي مَشْرُوعِ بَاوَر تُول"
    res = translator.translate(text_with_harakat, from_code="ar", to_code="en")
    assert len(res.translated_text) > 0
    assert res.from_code == "ar"


def test_language_detection(translator):
    """Verify automatic language detection accurately detects Arabic vs English"""
    assert OfflineTranslator.detect_language("أهلاً وسهلاً") == ("ar", "en")
    assert OfflineTranslator.detect_language("Welcome to PowerTool") == ("en", "ar")


def test_missing_model_error():
    """Verify clean ModelNotInstalledError when an uninstalled language pair is requested"""
    # Create temporary manager with non-existent directory
    mgr = ModelManager(base_models_dir="C:\\NonExistentPath\\Models")
    tr = OfflineTranslator(mgr)
    with pytest.raises(ModelNotInstalledError) as exc_info:
        tr.translate("test", from_code="fr", to_code="es")
    assert "not installed" in str(exc_info.value)


def test_strictly_offline_execution_network_blocked(translator, monkeypatch):
    """
    CRITICAL REQUIREMENT:
    Verify translation works 100% offline with network completely blocked.
    Monkeypatches socket.create_connection and socket.socket.connect to fail.
    """
    def blocked_connect(*args, **kwargs):
        raise OSError("Network connection blocked by test suite! Strict offline mode violated.")

    monkeypatch.setattr(socket, "create_connection", blocked_connect)
    monkeypatch.setattr(socket.socket, "connect", blocked_connect)

    # Must succeed without making any network call
    res = translator.translate("This is an offline test.", from_code="en", to_code="ar")
    assert len(res.translated_text) > 0
    assert any(0x0600 <= ord(ch) <= 0x06FF for ch in res.translated_text)
