import re
from num2words import num2words
import wrapperfunction.core.config as config

def process_text_name(txt):
    # Remove URL components
    individual_filename = txt.replace("https://", '').replace("www.", '').replace(".com", '')
    
    # Replace special characters with underscores
    individual_filename = re.sub(r'[?+.=\-\\\/|%]', '_', individual_filename)
    
    # Truncate if the filename is too long
    if len(individual_filename) >= 40:
        individual_filename = individual_filename[:25] + individual_filename[-30:]
    
    return individual_filename


def clean_text(text: str, is_ar: bool = False):
    # Remove any pattern like [doc*], where * represents numbers
    # Remove non-readable characters (anything not a letter, number, punctuation, or whitespace)
    # text = re.sub(r'[^\w\s,.!?\'\"-]', '', text)
    # text = re.sub(r'<[^>]*>|\[doc\d+\]', '', text)
    # text = re.sub(r"<[^>]*>|\[doc\d+\]|<pre[^>]*>.*?</pre>|doc\d+", "", text)
    text = re.sub(r"<[^>]*>|\[doc\d+\]|<pre[^>]*>.*?</pre>|doc\d+|###", "", text)
    if is_ar:
        text = replace_numbers_with_words(text)
        text = replace_ar_text(text)
    return text


def replace_number(match):
    number = match.group(0)
    number = number.replace(",", "")
    return num2words(int(number), lang="ar")


def replace_numbers_with_words(phrase):
    digit_pattern = r"[\u0660-\u0669\u0030-\u0039]+(?:,[\u0660-\u0669\u0030-\u0039]+)*"
    phrase = re.sub(digit_pattern, replace_number, phrase)
    return phrase

def replace_ar_text(text: str) -> str:
    for key, value in config.AR_DICT.items():
        text = text.replace(key, value)
    return text