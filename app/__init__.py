"""
Yabix VisionFusion OCR + QR Intelligence Suite
------------------------------------------------
This package provides core modules for:
- OCR extraction (ocr_dyn)
- QR decoding (qr_dyn)
- Data merging (mix_ocr_qr)
- Web scraping and enrichment (scrap)
- Excel mode processing (excel_mode)
- Final data fusion (final_mix)
"""

__version__ = "1.0.0"
__author__ = "Yabix AI"
__email__ = "yasa.aidv@gmail.com"

from .ocr_dyn import *
from .qr_dyn import *
from .mix_ocr_qr import *
from .scrap import *
from .excel_mode import *
from .final_mix import *
