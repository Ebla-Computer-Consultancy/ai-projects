import re
from num2words import num2words
import wrapperfunction.core.config as config
import json
import os
import requests


def process_text_name(txt):
    # Remove URL components
    individual_filename = (
        txt.replace("https://", "")
        .replace("http://", "")
        .replace("www.", "")
        .replace(".com", "")
    )

    # Replace special characters with underscores
    individual_filename = re.sub(r"[?+.=\_\\\/|%]", "-", individual_filename)
    individual_filename = re.sub(r"__", "-", individual_filename)
    # Truncate if the filename is too long
    if len(individual_filename) >= 40:
        individual_filename = individual_filename[:25] + individual_filename[-30:]
    return individual_filename


def download_pdfs(input_file, output_folder):
    # Load the input JSON
    with open(input_file, "r", encoding="utf8") as file:
        data = json.load(file)

    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)

    for item in data:
        if "pdf_url" in item:
            pdf_url = item["pdf_url"]
            title = item.get(
                "title", pdf_url.split("/")[-1]
            )  # Use title if available, otherwise filename from URL

            # Download the PDF
            response = requests.get(pdf_url)
            pdf_path = os.path.join(output_folder, title)

            with open(pdf_path, "wb") as pdf_file:
                pdf_file.write(response.content)


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


def get_title(url, title=""):
    if title == "":
        title = url.split("/")[-1]
    return title


def sanitize_filename(filename):
    return re.sub(r'[<>:"\\|?*]', "", filename)
