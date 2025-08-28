# from ai_module import analyze_text

# if __name__ == "__main__":
#     text = "I want to kill you."
#     result = analyze_text(text)
#     print("Input:", text)
#     print("Result:", result)

from ai_module.text_analyzer import TextAnalyzer

if __name__ == "__main__":
    analyzer = TextAnalyzer(provider='azure')
    
    text1 = "Hello, how are you today?"
    result1 = analyzer.analyze(text1)
    print("Test 1 - Normal text")
    print(result1)
    print("="*40)
    
    text2 = "I will kill you."
    result2 = analyzer.analyze(text2)
    print("Test 2 - Harmful text")
    print(result2)
    print("="*40)

    text3 = ""
    result3 = analyzer.analyze(text3)
    print("Test 3 - Empty text")
    print(result3)
