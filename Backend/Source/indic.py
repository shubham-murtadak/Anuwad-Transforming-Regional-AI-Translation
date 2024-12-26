import torch
from IndicTransToolkit import IndicProcessor
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from .log import logging

# Load necessary components
ip = IndicProcessor(inference=True)
tokenizer = AutoTokenizer.from_pretrained("ai4bharat/indictrans2-en-indic-dist-200M", trust_remote_code=True)
model = AutoModelForSeq2SeqLM.from_pretrained("ai4bharat/indictrans2-en-indic-dist-200M", trust_remote_code=True)

def translate_text_indic(input_text: str, src_lang: str, tgt_lang: str) -> str:
    """
    Translates text from a source language to a target language.
    
    Args:
        input_text (str): Text to be translated.
        src_lang (str): Source language code (e.g., 'eng_Latn').
        tgt_lang (str): Target language code (e.g., 'hin_Deva').
        
    Returns:
        str: Translated text.
    """

    logging.info("inside indic translation :")
    # print("inside indic translation :")

    # Language code mapping
    language_mapping = {
        'en': 'eng_Latn',
        'hi': 'hin_Deva',
        'mr': 'mar_Deva',
        'ta': 'tam_Taml',
        'bn': 'ben_Beng',
        'kn': 'kan_Knda',
        'or': 'ory_Orya',
        'te': 'tel_Telu',
        'gu': 'guj_Gujr',
        'ml': 'mal_Mlym',
        'pa': 'pan_Guru',
        'as': 'asm_Beng'
    }
    
    # Map language codes to model-specific formats
    src_lang = language_mapping.get(src_lang, src_lang)
    tgt_lang = language_mapping.get(tgt_lang, tgt_lang)
    
    # Preprocess input text
    batch = ip.preprocess_batch([input_text], src_lang=src_lang, tgt_lang=tgt_lang)
    batch = tokenizer(batch, padding="longest", truncation=True, max_length=256, return_tensors="pt")
    
    # Generate translation
    with torch.inference_mode():
        outputs = model.generate(**batch, num_beams=5, num_return_sequences=1, max_length=256)
    
    # Decode the output
    with tokenizer.as_target_tokenizer():
        outputs = tokenizer.batch_decode(outputs, skip_special_tokens=True, clean_up_tokenization_spaces=True)
    
    # Post-process the output
    translated_text = ip.postprocess_batch(outputs, lang=tgt_lang)

    logging.info("translation done by indic is :",translated_text[0])

    # print("translation done by indic is :",translated_text[0])
    
    return translated_text[0] if translated_text else ""



if __name__=='__main__':
    # Example usage
    languageMap = {
        'English': 'en',
        'Hindi': 'hi',
        'Marathi': 'mr',
        'Kannada': 'kn',
        'Tamil': 'ta',
        'Telugu': 'te',
        'Bangla': 'bn'
    }

    input_text = "Technology has become an essential part of our daily lives, shaping how we work, communicate, and entertain ourselves."



    # Test translations
    for lang_name, lang_code in languageMap.items():
        translated = translate_text_indic(input_text=input_text, src_lang='en', tgt_lang=lang_code)
        print(f"Translated to {lang_name}: {translated}")
