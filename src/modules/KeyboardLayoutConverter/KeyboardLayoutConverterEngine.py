"""
Keyboard Layout Converter Engine for Powertool Extended Edition
Accurate physical key-position mapping between US QWERTY, Arabic 101, and Arabic 102.
Cross-platform support: Windows, Linux (X11 & Wayland).
Developed by En-Dhiaa.
"""

import sys
from typing import Tuple, Optional, Dict, List


class KeyboardLayoutConverterEngine:
    # Physical scancode mappings for standard US QWERTY -> Arabic 101
    EN_TO_AR_101: Dict[str, str] = {
        # Number / Symbol Row
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
        # QWERTY Row
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
        # Home Row
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
        # Bottom Row
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

    # Arabic 102 overrides (specifically handling extra key next to Left Shift / layout differences)
    EN_TO_AR_102: Dict[str, str] = EN_TO_AR_101.copy()
    EN_TO_AR_102.update({
        '|': '|',
        '\\': '\\',
    })

    # Ligature reverse mapping: 2-character sequences and Presentation Forms
    AR_TO_EN_LIGATURES: Dict[str, str] = {
        'لا': 'b',
        'لآ': 'B',
        'لإ': 'T',
        'لأ': 'G',
        # Unicode presentation forms
        '\uFEFB': 'b', '\uFEFC': 'b',
        '\uFEF5': 'B', '\uFEF6': 'B',
        '\uFEF9': 'T', '\uFEFA': 'T',
        '\uFEF7': 'G', '\uFEF8': 'G'
    }

    # Build reverse dictionaries
    AR_TO_EN_101_SINGLE: Dict[str, str] = {}
    for en_char, ar_char in EN_TO_AR_101.items():
        if len(ar_char) == 1:
            AR_TO_EN_101_SINGLE[ar_char] = en_char

    AR_TO_EN_102_SINGLE: Dict[str, str] = {}
    for en_char, ar_char in EN_TO_AR_102.items():
        if len(ar_char) == 1:
            AR_TO_EN_102_SINGLE[ar_char] = en_char

    @classmethod
    def detect_direction(cls, text: str) -> Tuple[str, float]:
        """
        Determines whether text is accidentally typed Arabic (needing ar->en)
        or accidentally typed English (needing en->ar).
        Returns ('ar_to_en' | 'en_to_ar', confidence).
        """
        if not text:
            return ('en_to_ar', 0.0)

        ar_count = sum(1 for ch in text if 0x0600 <= ord(ch) <= 0x06FF or 0xFB50 <= ord(ch) <= 0xFEFF)
        en_count = sum(1 for ch in text if ('a' <= ch <= 'z') or ('A' <= ch <= 'Z'))
        total = ar_count + en_count

        if total == 0:
            return ('en_to_ar', 0.0)

        confidence = max(ar_count, en_count) / total
        return ('ar_to_en' if ar_count >= en_count else 'en_to_ar', confidence)

    @classmethod
    def english_to_arabic(
        cls,
        text: str,
        layout: str = "101",
        preserve_punctuation: bool = False
    ) -> str:
        mapping = cls.EN_TO_AR_102 if layout == "102" else cls.EN_TO_AR_101
        result = []
        for ch in text:
            if preserve_punctuation and (ch in "!@#$%^&*()_+-=[]{}|;:'\",.<>/?"):
                result.append(ch)
            else:
                result.append(mapping.get(ch, ch))
        return "".join(result)

    @classmethod
    def arabic_to_english(
        cls,
        text: str,
        layout: str = "101",
        preserve_punctuation: bool = False
    ) -> str:
        single_map = cls.AR_TO_EN_102_SINGLE if layout == "102" else cls.AR_TO_EN_101_SINGLE
        result = []
        i = 0
        n = len(text)
        while i < n:
            # Check 2-character ligatures first
            if i + 1 < n and text[i:i + 2] in cls.AR_TO_EN_LIGATURES:
                result.append(cls.AR_TO_EN_LIGATURES[text[i:i + 2]])
                i += 2
                continue
            # Check 1-character ligatures (presentation forms)
            if text[i] in cls.AR_TO_EN_LIGATURES:
                result.append(cls.AR_TO_EN_LIGATURES[text[i]])
                i += 1
                continue

            ch = text[i]
            if preserve_punctuation and (ch in "!@#$%^&*()_+-=[]{}|;:'\",.<>/?،؟؛"):
                result.append(ch)
            else:
                result.append(single_map.get(ch, ch))
            i += 1

        return "".join(result)

    @classmethod
    def convert(
        cls,
        text: str,
        direction: str = "auto",
        layout: str = "101",
        preserve_punctuation: bool = False
    ) -> Tuple[str, str, float]:
        """
        Converts text bidirectionally.
        direction: 'auto', 'en_to_ar', or 'ar_to_en'.
        Returns (converted_text, applied_direction, confidence).
        """
        if not text:
            return ("", direction, 1.0)

        if direction == "auto":
            applied_dir, conf = cls.detect_direction(text)
        else:
            applied_dir = direction
            conf = 1.0

        if applied_dir == "en_to_ar":
            converted = cls.english_to_arabic(text, layout, preserve_punctuation)
        else:
            converted = cls.arabic_to_english(text, layout, preserve_punctuation)

        return (converted, applied_dir, conf)

