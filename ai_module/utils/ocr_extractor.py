# ai_module/utils/ocr_extractor.py

import easyocr
from PIL import Image
import io

class OCRExtractor:
    """
    Lightweight local OCR using EasyOCR.
    """

    def __init__(self, languages=None):
        """
        Initialize OCR extractor.
        """
        if languages is None:
            languages = ['en']  # default English
        self.reader = easyocr.Reader(languages)

    def extract_text(self, image) -> str:
        """
        Extract text from a local image.
        """
        # Convert file-like object to PIL.Image
        if not isinstance(image, str):
            if hasattr(image, "read"):  # file-like object
                image = Image.open(image)
            elif isinstance(image, Image.Image):
                pass
            else:
                raise ValueError("image must be a file path, PIL.Image, or file-like object")

        try:
            result = self.reader.readtext(image, detail=0)
            return "\n".join(result).strip()
        except Exception as e:
            return f"[OCR Error] {str(e)}"
