"""
Offline Translator CLI & IPC Bridge
PowerTool Extended Edition
"""

import sys
import os
import json
import argparse
from typing import Optional

# Ensure local module directory is in path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from OfflineTranslatorEngine import OfflineTranslator, ModelManager, TranslationResult, ModelNotInstalledError


def get_selected_text_windows() -> str:
    """Safely captures selected text using Windows clipboard without destroying previous contents"""
    try:
        import ctypes
        from ctypes import wintypes
        import time

        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32

        CF_UNICODETEXT = 13
        GMEM_MOVEABLE = 0x0002

        # 1. Backup current clipboard text
        backup_text = ""
        if user32.OpenClipboard(None):
            h_clip = user32.GetClipboardData(CF_UNICODETEXT)
            if h_clip:
                p_text = kernel32.GlobalLock(h_clip)
                if p_text:
                    backup_text = ctypes.wstring_at(p_text)
                    kernel32.GlobalUnlock(h_clip)
            user32.CloseClipboard()

        # 2. Empty clipboard
        if user32.OpenClipboard(None):
            user32.EmptyClipboard()
            user32.CloseClipboard()

        # 3. Send Ctrl+C
        # Key codes: VK_CONTROL = 0x11, 'C' = 0x43
        KEYEVENTF_KEYUP = 0x0002
        user32.keybd_event(0x11, 0, 0, 0)
        user32.keybd_event(0x43, 0, 0, 0)
        user32.keybd_event(0x43, 0, KEYEVENTF_KEYUP, 0)
        user32.keybd_event(0x11, 0, KEYEVENTF_KEYUP, 0)

        # 4. Wait for clipboard to populate
        selected_text = ""
        start = time.time()
        while time.time() - start < 0.25:
            time.sleep(0.02)
            if user32.OpenClipboard(None):
                h_data = user32.GetClipboardData(CF_UNICODETEXT)
                if h_data:
                    p_data = kernel32.GlobalLock(h_data)
                    if p_data:
                        selected_text = ctypes.wstring_at(p_data)
                        kernel32.GlobalUnlock(h_data)
                user32.CloseClipboard()
                if selected_text:
                    break

        # 5. Restore clipboard if no new text was selected
        if not selected_text and backup_text:
            if user32.OpenClipboard(None):
                user32.EmptyClipboard()
                encoded = (backup_text + "\0").encode("utf-16le")
                h_mem = kernel32.GlobalAlloc(GMEM_MOVEABLE, len(encoded))
                if h_mem:
                    p_mem = kernel32.GlobalLock(h_mem)
                    ctypes.memmove(p_mem, encoded, len(encoded))
                    kernel32.GlobalUnlock(h_mem)
                    user32.SetClipboardData(CF_UNICODETEXT, h_mem)
                user32.CloseClipboard()

        return selected_text
    except Exception:
        return ""


def main():
    parser = argparse.ArgumentParser(description="PowerTool Offline Translator Engine CLI")
    parser.add_argument("--popup", action="store_true", help="Launch interactive floating translation popup")
    parser.add_argument("--replace", action="store_true", help="Translate selection and replace in active window")
    parser.add_argument("--reverse", action="store_true", help="Reverse translation direction")
    parser.add_argument("--text", type=str, default="", help="Text to translate")
    parser.add_argument("--from", dest="from_code", type=str, default="auto", help="Source language (ar, en, auto)")
    parser.add_argument("--to", dest="to_code", type=str, default="auto", help="Target language (ar, en, auto)")
    parser.add_argument("--list-models", action="store_true", help="List available and installed models")
    parser.add_argument("--download-model", type=str, default="", help="Download model by id (e.g. ar_en, en_ar)")
    parser.add_argument("--delete-model", type=str, default="", help="Delete model by id (e.g. ar_en, en_ar)")
    parser.add_argument("--disk-info", action="store_true", help="Show model directory disk usage")

    args = parser.parse_args()
    mgr = ModelManager()

    if args.list_models:
        packages = mgr.list_packages()
        print(json.dumps(packages, indent=2))
        return

    if args.disk_info:
        disk_info = mgr.get_disk_space_info()
        print(json.dumps(disk_info, indent=2))
        return

    if args.download_model:
        parts = args.download_model.split("_")
        if len(parts) == 2:
            def on_progress(pct, msg):
                print(f"PROGRESS:{pct:.1f}:{msg}", flush=True)
            success = mgr.download_and_install_package(parts[0], parts[1], on_progress)
            print(json.dumps({"success": success, "model": args.download_model}))
        else:
            print(json.dumps({"error": f"Invalid model id: {args.download_model}"}))
        return

    if args.delete_model:
        parts = args.delete_model.split("_")
        if len(parts) == 2:
            success = mgr.remove_package(parts[0], parts[1])
            print(json.dumps({"success": success, "deleted": args.delete_model}))
        return

    # Popup UI launch
    if args.popup:
        text = args.text
        if not text:
            text = get_selected_text_windows()

        from OfflineTranslatorUI import launch_popup
        launch_popup(text)
        return

    # Direct CLI Translation
    text = args.text
    if not text:
        text = get_selected_text_windows()

    if not text:
        print(json.dumps({"error": "No text provided or selected"}))
        return

    translator = OfflineTranslator(mgr)
    from_c = args.from_code
    to_c = args.to_code

    if args.reverse:
        detected_from, detected_to = OfflineTranslator.detect_language(text)
        from_c = detected_to
        to_c = detected_from

    try:
        result = translator.translate(text, from_c, to_c)
        print(json.dumps(result.to_dict(), ensure_ascii=False))
    except ModelNotInstalledError as e:
        print(json.dumps({"error": str(e), "missing_model": True, "from": e.from_code, "to": e.to_code}))
    except Exception as e:
        print(json.dumps({"error": str(e)}))


if __name__ == "__main__":
    main()
