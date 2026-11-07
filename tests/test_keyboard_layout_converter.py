"""
Unit Tests for Keyboard Layout Converter
PowerTool Extended Edition
"""

import pytest

# Accurate Python reference implementation of KeyboardLayoutConverterEngine
class KeyboardLayoutConverterPython:
    EN_TO_AR_101 = {
        # Number row
        '`': 'ذ', '~': 'ّ',
        '1': '1', '!': '!',
        '2': '2', '@': '@',
        '3': '3', '#': '#',
        '4': '4', '$': '$',
        '5': '5', '%': '%',
        '6': '6', '^': '^',
        '7': '7', '&': '&',
        '8': '8', '*': '*',
        '9': '9', '(': ')',
        '0': '0', ')': '(',
        '-': '-', '_': '_',
        '=': '=', '+': '+',
        # QWERTY row
        'q': 'ض', 'Q': 'َ',
        'w': 'ص', 'W': 'ً',
        'e': 'ث', 'E': 'ُ',
        'r': 'ق', 'R': 'ٌ',
        't': 'ف', 'T': 'لإ',
        'y': 'غ', 'Y': 'إ',
        'u': 'ع', 'U': '`',
        'i': 'ه', 'I': '÷',
        'o': 'خ', 'O': '×',
        'p': 'ح', 'P': '؛',
        '[': 'ج', '{': '<',
        ']': 'د', '}': '>',
        '\\': '\\', '|': '|',
        # Home row
        'a': 'ش', 'A': 'ِ',
        's': 'س', 'S': 'ٍ',
        'd': 'ي', 'D': ']',
        'f': 'ب', 'F': '[',
        'g': 'ل', 'G': 'لأ',
        'h': 'ا', 'H': 'أ',
        'j': 'ت', 'J': 'ـ',
        'k': 'ن', 'K': '،',
        'l': 'م', 'L': '/',
        ';': 'ك', ':': ':',
        "'": 'ط', '"': '"',
        # Bottom row
        'z': 'ئ', 'Z': '~',
        'x': 'ء', 'X': 'ْ',
        'c': 'ؤ', 'C': '}',
        'v': 'ر', 'V': '{',
        'b': 'لا', 'B': 'لآ',
        'n': 'ى', 'N': 'آ',
        'm': 'ة', 'M': "'",
        ',': 'و', '<': ',',
        '.': 'ز', '>': '.',
        '/': 'ظ', '?': '؟',
        ' ': ' '
    }

    AR_TO_EN_LIGATURES = {
        'لا': 'b',
        'لآ': 'B',
        'لإ': 'T',
        'لأ': 'G',
        '\uFEFB': 'b', '\uFEFC': 'b',
        '\uFEF5': 'B', '\uFEF6': 'B',
        '\uFEF9': 'T', '\uFEFA': 'T',
        '\uFEF7': 'G', '\uFEF8': 'G'
    }

    AR_TO_EN_SINGLE = {}
    for en, ar in EN_TO_AR_101.items():
        if len(ar) == 1:
            AR_TO_EN_SINGLE[ar] = en

    @classmethod
    def detect_direction(cls, text: str):
        ar_count = sum(1 for ch in text if 0x0600 <= ord(ch) <= 0x06FF or 0xFB50 <= ord(ch) <= 0xFEFF)
        en_count = sum(1 for ch in text if ('a' <= ch <= 'z') or ('A' <= ch <= 'Z'))
        total = ar_count + en_count
        conf = max(ar_count, en_count) / total if total > 0 else 0.0
        return ('ar_to_en' if ar_count >= en_count else 'en_to_ar', conf)

    @classmethod
    def en_to_ar(cls, text: str, preserve_punctuation=False):
        res = []
        for ch in text:
            if preserve_punctuation and (ch in "!@#$%^&*()_+-=[]{}|;:'\",.<>/?"):
                res.append(ch)
            else:
                res.append(cls.EN_TO_AR_101.get(ch, ch))
        return "".join(res)

    @classmethod
    def ar_to_en(cls, text: str, preserve_punctuation=False):
        res = []
        i = 0
        n = len(text)
        while i < n:
            if i + 1 < n and text[i:i+2] in cls.AR_TO_EN_LIGATURES:
                res.append(cls.AR_TO_EN_LIGATURES[text[i:i+2]])
                i += 2
                continue
            if text[i] in cls.AR_TO_EN_LIGATURES:
                res.append(cls.AR_TO_EN_LIGATURES[text[i]])
                i += 1
                continue
            ch = text[i]
            if preserve_punctuation and (ch in "!@#$%^&*()_+-=[]{}|;:'\",.<>/?،؟؛"):
                res.append(ch)
            else:
                res.append(cls.AR_TO_EN_SINGLE.get(ch, ch))
            i += 1
        return "".join(res)

    @classmethod
    def convert(cls, text: str, preserve_punctuation=False):
        if not text:
            return text
        dir_name, _ = cls.detect_direction(text)
        if dir_name == 'en_to_ar':
            return cls.en_to_ar(text, preserve_punctuation)
        else:
            return cls.ar_to_en(text, preserve_punctuation)


# ================= TESTS =================

def test_prompt_example_1_go_home_now():
    """Verify exact example from prompt: 'go home now' -> 'لخ اخةث ىخص' and reverse"""
    en = "go home now"
    ar = "لخ اخةث ىخص"
    assert KeyboardLayoutConverterPython.en_to_ar(en) == ar
    assert KeyboardLayoutConverterPython.ar_to_en(ar) == en
    assert KeyboardLayoutConverterPython.convert(en) == ar
    assert KeyboardLayoutConverterPython.convert(ar) == en


def test_prompt_example_2_hello():
    """Verify 'hello' -> 'اثممخ' and reverse"""
    en = "hello"
    ar = "اثممخ"
    assert KeyboardLayoutConverterPython.en_to_ar(en) == ar
    assert KeyboardLayoutConverterPython.ar_to_en(ar) == en


def test_prompt_example_3_marhaba():
    """Verify 'مرحبا' -> 'lvpfh' and reverse"""
    ar = "مرحبا"
    en = "lvpfh"
    assert KeyboardLayoutConverterPython.ar_to_en(ar) == en
    assert KeyboardLayoutConverterPython.en_to_ar(en) == ar


def test_uppercase_shift_mapping():
    """Verify uppercase letters map to Arabic shifted keys (Alef with Hamza, Tanwin, etc.)"""
    assert KeyboardLayoutConverterPython.en_to_ar("H") == "أ"
    assert KeyboardLayoutConverterPython.en_to_ar("Y") == "إ"
    assert KeyboardLayoutConverterPython.en_to_ar("N") == "آ"
    assert KeyboardLayoutConverterPython.en_to_ar("T") == "لإ"
    assert KeyboardLayoutConverterPython.en_to_ar("G") == "لأ"
    assert KeyboardLayoutConverterPython.en_to_ar("B") == "لآ"

    assert KeyboardLayoutConverterPython.ar_to_en("أ") == "H"
    assert KeyboardLayoutConverterPython.ar_to_en("إ") == "Y"
    assert KeyboardLayoutConverterPython.ar_to_en("آ") == "N"
    assert KeyboardLayoutConverterPython.ar_to_en("لإ") == "T"
    assert KeyboardLayoutConverterPython.ar_to_en("لأ") == "G"
    assert KeyboardLayoutConverterPython.ar_to_en("لآ") == "B"


def test_numbers_preservation():
    """Verify numbers 0-9 preserve their values across physical key rows"""
    nums = "1234567890"
    assert KeyboardLayoutConverterPython.en_to_ar(nums) == nums
    assert KeyboardLayoutConverterPython.ar_to_en(nums) == nums


def test_arabic_specific_punctuation():
    """Verify Arabic comma, semicolon, question mark map to physical key equivalents"""
    # '?' -> '؟'
    assert KeyboardLayoutConverterPython.en_to_ar("?") == "؟"
    assert KeyboardLayoutConverterPython.ar_to_en("؟") == "?"

    # 'P' -> '؛'
    assert KeyboardLayoutConverterPython.en_to_ar("P") == "؛"
    assert KeyboardLayoutConverterPython.ar_to_en("؛") == "P"

    # 'K' -> '،'
    assert KeyboardLayoutConverterPython.en_to_ar("K") == "،"
    assert KeyboardLayoutConverterPython.ar_to_en("،") == "K"


def test_multiline_selection():
    """Verify multi-line text conversion preserves newlines and spacing"""
    multi_en = "first line\nsecond line\nthird line"
    multi_ar = KeyboardLayoutConverterPython.en_to_ar(multi_en)
    assert "\n" in multi_ar
    assert len(multi_ar.split("\n")) == 3
    assert KeyboardLayoutConverterPython.ar_to_en(multi_ar) == multi_en


def test_reversibility_cycle():
    """Verify Convert(Convert(text)) == text for standard keyboard inputs"""
    samples = [
        "quick brown fox",
        "The project is ready for deployment.",
        "اثممخ صخقمع",
        "لخ اخةث ىخص"
    ]
    for sample in samples:
        converted = KeyboardLayoutConverterPython.convert(sample)
        reverted = KeyboardLayoutConverterPython.convert(converted)
        assert reverted == sample


def test_emoji_and_unrelated_unicode_preservation():
    """Verify emojis and non-standard Unicode characters are not corrupted"""
    text_with_emoji = "hello 😊🚀 world"
    converted = KeyboardLayoutConverterPython.convert(text_with_emoji)
    assert "😊" in converted
    assert "🚀" in converted
    reverted = KeyboardLayoutConverterPython.convert(converted)
    assert reverted == text_with_emoji


def test_empty_and_whitespace():
    """Verify empty and whitespace strings do not raise errors"""
    assert KeyboardLayoutConverterPython.convert("") == ""
    assert KeyboardLayoutConverterPython.convert("   ") == "   "
    assert KeyboardLayoutConverterPython.convert("\t\n") == "\t\n"


def test_preserve_punctuation_option():
    """Verify preserve_punctuation flag retains punctuation intact"""
    res = KeyboardLayoutConverterPython.en_to_ar("hello?", preserve_punctuation=True)
    assert res.endswith("?")
