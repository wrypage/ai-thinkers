import os
import chardet
import re
from pathlib import Path

# Project root directory (this folder)
BASE_DIR = Path(__file__).parent.resolve()

def detect_encoding(filepath):
    with open(filepath, 'rb') as f:
        result = chardet.detect(f.read(5000))
        return result['encoding']

def convert_to_utf8(filepath):
    encoding = detect_encoding(filepath)
    if encoding.lower() != 'utf-8':
        with open(filepath, 'r', encoding=encoding, errors='replace') as f:
            content = f.read()
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Converted {filepath.name} from {encoding} to UTF-8")
    else:
        print(f"{filepath.name} already UTF-8")

def clean_text(text):
    # Normalize line breaks
    text = text.replace('\r\n', '\n').replace('\r', '\n')

    # Remove page headers/footers (simple heuristics)
    lines = text.split('\n')
    cleaned = []
    for line in lines:
        if re.match(r'^\s*\d{1,4}\s*$', line):  # page number lines
            continue
        if re.match(r'^[A-Z\s]{6,}$', line.strip()) and len(line.strip()) < 40:
            continue  # headers in all caps
        cleaned.append(line)
    return '\n'.join(cleaned)

def process_all_txt_files():
    for thinker_dir in BASE_DIR.iterdir():
        if thinker_dir.is_dir():
            for file in thinker_dir.glob("*.txt"):
                try:
                    convert_to_utf8(file)
                    with open(file, 'r', encoding='utf-8') as f:
                        text = f.read()
                    cleaned_text = clean_text(text)
                    with open(file, 'w', encoding='utf-8') as f:
                        f.write(cleaned_text)
                    print(f"Cleaned: {file}")
                except Exception as e:
                    print(f"Error processing {file}: {e}")

if __name__ == "__main__":
    process_all_txt_files()
