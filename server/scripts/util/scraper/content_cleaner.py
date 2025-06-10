from rapidfuzz import fuzz
import re
import ast

def normalize(text):
    return re.sub(r'\s+', ' ', text.strip().lower())

def deduplicate_content(text_content, threshold=90):
    deduped = {}
    old_text_content = {}

    text_content = ast.literal_eval(text_content)

    for tag, text in text_content.items():
        norm_text = normalize(text)
        is_duplicate = any(
            fuzz.ratio(norm_text, normalize(old_text)) >= threshold
            for old_text in old_text_content.values()
        )
        if not is_duplicate:
            deduped[tag] = text
            old_text_content[tag] = text

    return str(deduped)