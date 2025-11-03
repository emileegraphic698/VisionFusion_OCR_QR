# config.py
"""
🎯 مدیریت مرکزی مسیرها برای Streamlit Cloud
"""
import os
from pathlib import Path

def get_base_dir():
    """تشخیص محیط و بازگشت مسیر پایه"""
    # چک محیط Streamlit Cloud
    if os.getenv("STREAMLIT_SHARING_MODE") or os.getenv("STREAMLIT_RUNTIME_ENV"):
        base = Path("/tmp/exhibition_data")
    else:
        # محیط لوکال
        base = Path.cwd() / "session_current"
    
    base.mkdir(parents=True, exist_ok=True)
    return base

# 📁 مسیر پایه
BASE_DIR = get_base_dir()

# 📁 زیرپوشه‌های ثابت
UPLOADS_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR
LOGS_DIR = BASE_DIR / "logs"
JSON_DIR = BASE_DIR / "json_data"
RENAMED_DIR = BASE_DIR / "renamed"
DEBUG_DIR = BASE_DIR / "_debug"

# ساخت همه پوشه‌ها
for folder in [UPLOADS_DIR, OUTPUT_DIR, LOGS_DIR, JSON_DIR, RENAMED_DIR, DEBUG_DIR]:
    folder.mkdir(parents=True, exist_ok=True)

# 📄 فایل‌های خروجی
OCR_OUTPUT = OUTPUT_DIR / "gemini_output.json"
QR_RAW = OUTPUT_DIR / "final_superqr_v6_raw.json"
QR_CLEAN = OUTPUT_DIR / "final_superqr_v6_clean.json"
MIX_OUTPUT = OUTPUT_DIR / "mix_ocr_qr.json"
SCRAPE_OUTPUT = OUTPUT_DIR / "gemini_scrap_output.json"
WEB_ANALYSIS = OUTPUT_DIR / "web_analysis.xlsx"

# 🔧 تنظیم Environment Variables
os.environ["SESSION_DIR"] = str(BASE_DIR)
os.environ["SOURCE_FOLDER"] = str(UPLOADS_DIR)
os.environ["OUTPUT_DIR"] = str(OUTPUT_DIR)

print(f"✅ Config loaded: BASE_DIR={BASE_DIR}")