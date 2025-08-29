# from ai_module import analyze_text

# if __name__ == "__main__":
#     text = "I want to kill you."
#     result = analyze_text(text)
#     print("Input:", text)
#     print("Result:", result)

# from ai_module.text_analyzer import TextAnalyzer

# if __name__ == "__main__":
#     analyzer = TextAnalyzer(provider='azure')
    
#     text1 = "Hello, how are you today?"
#     result1 = analyzer.analyze(text1)
#     print("Test 1 - Normal text")
#     print(result1)
#     print("="*40)
    
#     text2 = "I will kill you."
#     result2 = analyzer.analyze(text2)
#     print("Test 2 - Harmful text")
#     print(result2)
#     print("="*40)

#     text3 = ""
#     result3 = analyzer.analyze(text3)
#     print("Test 3 - Empty text")
#     print(result3)

from ai_module.utils.ocr_extractor import OCRExtractor
from ai_module.text_analyzer import TextAnalyzer

def test_image_input():
    """Test OCR + TextAnalyzer with images."""
    ocr = OCRExtractor()
    analyzer = TextAnalyzer(provider='azure')

    image_paths = ["test_image1.jpg", "test_image2.jpg"]
    for idx, path in enumerate(image_paths, start=1):
        try:
            with open(path, "rb") as f:
                text = ocr.extract_text(f)
            # print(f"Image Test {idx} - Extracted Text:\n{text}")
            result = analyzer.analyze(text)
            print(f"Image Test {idx} - Analysis Result:\n{result}")
            print("="*40)
        except FileNotFoundError:
            print(f"Image Test {idx} - File not found: {path}")
            print("="*40)


if __name__ == "__main__":

    test_image_input()
