from deep_translator import GoogleTranslator

class TextTranslator:
    def translate(self, text: str, src_lang: str, dest_lang: str) -> str:
        """
        Translates text from a source language to a destination language.
        """
        if not text or src_lang == dest_lang:
            return text
        
        try:
            # The langdetect library uses 'zh-cn', 'zh-tw', but Google Translate uses 'zh-CN', 'zh-TW'
            if src_lang == 'zh-cn':
                src_lang = 'zh-CN'
            if dest_lang == 'zh-cn':
                dest_lang = 'zh-CN'
            if src_lang == 'zh-tw':
                src_lang = 'zh-TW'
            if dest_lang == 'zh-tw':
                dest_lang = 'zh-TW'

            return GoogleTranslator(source=src_lang, target=dest_lang).translate(text)
        except Exception as e:
            print(f"Error during translation: {e}")
            return text # Return original text on error

# Initialize a single translator for the app
text_translator = TextTranslator() 