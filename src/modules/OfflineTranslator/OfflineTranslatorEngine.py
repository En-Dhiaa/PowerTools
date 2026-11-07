"""
Offline Translator Engine for PowerTool Extended Edition
Strictly offline neural machine translation between Arabic and English
Powered by CTranslate2 and SentencePiece (.argosmodel format)
"""

import os
import sys
import json
import time
import zipfile
import shutil
import urllib.request
import hashlib
from typing import Optional, List, Dict, Callable, Tuple

try:
    import ctranslate2
    import sentencepiece as spm
except ImportError:
    ctranslate2 = None
    spm = None


class ModelNotInstalledError(Exception):
    def __init__(self, from_code: str, to_code: str):
        super().__init__(f"Offline translation model for '{from_code}' -> '{to_code}' is not installed.")
        self.from_code = from_code
        self.to_code = to_code


class TranslationResult:
    def __init__(self, original_text: str, translated_text: str, from_code: str, to_code: str, duration_ms: float):
        self.original_text = original_text
        self.translated_text = translated_text
        self.from_code = from_code
        self.to_code = to_code
        self.duration_ms = duration_ms

    def to_dict(self) -> Dict:
        return {
            "original_text": self.original_text,
            "translated_text": self.translated_text,
            "from_code": self.from_code,
            "to_code": self.to_code,
            "duration_ms": round(self.duration_ms, 2)
        }


class ModelPackage:
    def __init__(self, from_code: str, to_code: str, from_name: str, to_name: str,
                 version: str, size_bytes: int, download_url: str, sha256: str = ""):
        self.from_code = from_code
        self.to_code = to_code
        self.from_name = from_name
        self.to_name = to_name
        self.version = version
        self.size_bytes = size_bytes
        self.download_url = download_url
        self.sha256 = sha256

    @property
    def package_id(self) -> str:
        return f"{self.from_code}_{self.to_code}"

    def to_dict(self, is_installed: bool = False, disk_path: str = "") -> Dict:
        return {
            "id": self.package_id,
            "from_code": self.from_code,
            "to_code": self.to_code,
            "from_name": self.from_name,
            "to_name": self.to_name,
            "version": self.version,
            "size_bytes": self.size_bytes,
            "size_mb": round(self.size_bytes / (1024 * 1024), 1),
            "download_url": self.download_url,
            "is_installed": is_installed,
            "disk_path": disk_path
        }


class ModelManager:
    OFFICIAL_PACKAGES = [
        ModelPackage(
            from_code="ar",
            to_code="en",
            from_name="Arabic",
            to_name="English",
            version="1.0",
            size_bytes=81869670,
            download_url="https://argos-net.com/v1/translate-ar_en-1_0.argosmodel"
        ),
        ModelPackage(
            from_code="en",
            to_code="ar",
            from_name="English",
            to_name="Arabic",
            version="1.0",
            size_bytes=88502631,
            download_url="https://argos-net.com/v1/translate-en_ar-1_0.argosmodel"
        )
    ]

    def __init__(self, base_models_dir: Optional[str] = None):
        if not base_models_dir:
            local_appdata = os.environ.get("LOCALAPPDATA", os.path.expanduser("~\\AppData\\Local"))
            self.base_dir = os.path.join(local_appdata, "Microsoft", "PowerToys", "OfflineTranslator", "models")
        else:
            self.base_dir = base_models_dir

        os.makedirs(self.base_dir, exist_ok=True)

    def get_model_dir(self, from_code: str, to_code: str) -> str:
        root_dir = os.path.join(self.base_dir, f"translate-{from_code}_{to_code}")
        sub_dir = os.path.join(root_dir, f"{from_code}_{to_code}")
        if os.path.isdir(sub_dir) and (os.path.isfile(os.path.join(sub_dir, "model", "model.bin")) or os.path.isfile(os.path.join(sub_dir, "model.bin"))):
            return sub_dir
        return root_dir

    def is_model_installed(self, from_code: str, to_code: str) -> bool:
        mdir = self.get_model_dir(from_code, to_code)
        if not os.path.isdir(mdir):
            return False

        has_model = (os.path.isfile(os.path.join(mdir, "model", "model.bin")) or
                     os.path.isfile(os.path.join(mdir, "model.bin")))
        has_spm = (os.path.isfile(os.path.join(mdir, "sentencepiece.model")) or
                   os.path.isfile(os.path.join(mdir, "source.spm")))
        return has_model and has_spm

    def list_packages(self) -> List[Dict]:
        results = []
        for pkg in self.OFFICIAL_PACKAGES:
            installed = self.is_model_installed(pkg.from_code, pkg.to_code)
            mdir = self.get_model_dir(pkg.from_code, pkg.to_code) if installed else ""
            results.append(pkg.to_dict(is_installed=installed, disk_path=mdir))
        return results

    def get_disk_space_info(self) -> Dict:
        try:
            total, used, free = shutil.disk_usage(self.base_dir)
            return {
                "total_gb": round(total / (1024**3), 2),
                "used_gb": round(used / (1024**3), 2),
                "free_gb": round(free / (1024**3), 2),
                "path": self.base_dir
            }
        except Exception:
            return {"free_gb": 0.0, "path": self.base_dir}

    def download_and_install_package(
        self,
        from_code: str,
        to_code: str,
        progress_callback: Optional[Callable[[float, str], None]] = None
    ) -> bool:
        pkg = next((p for p in self.OFFICIAL_PACKAGES if p.from_code == from_code and p.to_code == to_code), None)
        if not pkg:
            raise ValueError(f"No package available for {from_code} -> {to_code}")

        temp_zip = os.path.join(self.base_dir, f"temp_{pkg.package_id}.zip")
        dest_dir = self.get_model_dir(from_code, to_code)

        try:
            if progress_callback:
                progress_callback(0.0, f"Connecting to download {pkg.from_name} -> {pkg.to_name} model...")

            req = urllib.request.Request(pkg.download_url, headers={"User-Agent": "PowerTool-Extended/1.0"})
            with urllib.request.urlopen(req, timeout=30) as response:
                total_size = int(response.headers.get("Content-Length", pkg.size_bytes))
                downloaded = 0
                chunk_size = 1024 * 64

                with open(temp_zip, "wb") as f_out:
                    while True:
                        chunk = response.read(chunk_size)
                        if not chunk:
                            break
                        f_out.write(chunk)
                        downloaded += len(chunk)
                        if progress_callback and total_size > 0:
                            percent = min(100.0, (downloaded / total_size) * 85.0)
                            progress_callback(percent, f"Downloading: {round(downloaded / (1024*1024), 1)} MB / {round(total_size / (1024*1024), 1)} MB")

            if progress_callback:
                progress_callback(90.0, "Extracting and verifying model files...")

            # Extract zip
            if os.path.exists(dest_dir):
                shutil.rmtree(dest_dir)
            os.makedirs(dest_dir, exist_ok=True)

            with zipfile.ZipFile(temp_zip, "r") as zip_ref:
                zip_ref.extractall(dest_dir)

            # Write metadata
            meta = {
                "from_code": from_code,
                "to_code": to_code,
                "version": pkg.version,
                "installed_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            with open(os.path.join(dest_dir, "metadata.json"), "w", encoding="utf-8") as f_meta:
                json.dump(meta, f_meta, indent=2)

            if progress_callback:
                progress_callback(100.0, "Installation complete.")

            return True
        finally:
            if os.path.exists(temp_zip):
                try:
                    os.remove(temp_zip)
                except Exception:
                    pass

    def remove_package(self, from_code: str, to_code: str) -> bool:
        mdir = self.get_model_dir(from_code, to_code)
        if os.path.exists(mdir):
            shutil.rmtree(mdir)
            return True
        return False


class OfflineTranslator:
    def __init__(self, manager: Optional[ModelManager] = None):
        self.manager = manager or ModelManager()
        self._translators: Dict[str, ctranslate2.Translator] = {}
        self._tokenizers: Dict[str, spm.SentencePieceProcessor] = {}

    @staticmethod
    def detect_language(text: str) -> Tuple[str, str]:
        """Detect whether text is primarily Arabic or English/Latin"""
        arabic_chars = 0
        latin_chars = 0

        for ch in text:
            cp = ord(ch)
            if 0x0600 <= cp <= 0x06FF or 0xFB50 <= cp <= 0xFDFF or 0xFE70 <= cp <= 0xFEFF:
                arabic_chars += 1
            elif (0x0041 <= cp <= 0x005A) or (0x0061 <= cp <= 0x007A):
                latin_chars += 1

        if arabic_chars > latin_chars:
            return "ar", "en"
        return "en", "ar"

    def _load_model(self, from_code: str, to_code: str):
        key = f"{from_code}_{to_code}"
        if key in self._translators:
            return self._translators[key], self._tokenizers[key]

        if not self.manager.is_model_installed(from_code, to_code):
            raise ModelNotInstalledError(from_code, to_code)

        mdir = self.manager.get_model_dir(from_code, to_code)

        # Find model directory path for ctranslate2
        model_path = os.path.join(mdir, "model")
        if not os.path.isdir(model_path):
            model_path = mdir

        spm_path = os.path.join(mdir, "sentencepiece.model")
        if not os.path.isfile(spm_path):
            spm_path = os.path.join(mdir, "source.spm")

        translator = ctranslate2.Translator(model_path, device="cpu", inter_threads=2, intra_threads=4)
        sp = spm.SentencePieceProcessor()
        sp.load(spm_path)

        self._translators[key] = translator
        self._tokenizers[key] = sp
        return translator, sp

    def translate(self, text: str, from_code: Optional[str] = None, to_code: Optional[str] = None) -> TranslationResult:
        """
        Strictly offline translation.
        NO network calls are permitted.
        """
        if not text or not text.strip():
            return TranslationResult(text, "", from_code or "en", to_code or "ar", 0.0)

        start_time = time.perf_counter()

        # Auto-detect language if not specified
        if not from_code or from_code == "auto" or not to_code or to_code == "auto":
            detected_from, detected_to = self.detect_language(text)
            from_code = from_code if from_code and from_code != "auto" else detected_from
            to_code = to_code if to_code and to_code != "auto" else detected_to

        translator, sp = self._load_model(from_code, to_code)

        # Split into lines to preserve structure
        lines = text.split("\n")
        translated_lines = []

        for line in lines:
            line_str = line.strip()
            if not line_str:
                translated_lines.append("")
                continue

            tokens = sp.encode_as_pieces(line_str)
            results = translator.translate_batch([tokens])
            out_tokens = results[0].hypotheses[0]
            out_text = sp.decode_pieces(out_tokens)
            translated_lines.append(out_text)

        final_translation = "\n".join(translated_lines)
        duration_ms = (time.perf_counter() - start_time) * 1000.0

        return TranslationResult(
            original_text=text,
            translated_text=final_translation,
            from_code=from_code,
            to_code=to_code,
            duration_ms=duration_ms
        )
