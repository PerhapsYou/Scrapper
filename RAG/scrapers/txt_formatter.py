import os
import re
from pathlib import Path
from nltk import sent_tokenize

INPUT_DIR = "../knowledge/"
OUTPUT_DIR = "../cleaned_knowledge/"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def is_heading(line):
    return line.strip().isupper() or re.match(r"^\d+[\).]", line.strip()) or line.strip().startswith("Q:")

def smart_chunk(text, max_len=500):
    paragraphs = text.split("\n")
    chunks = []
    chunk = ""
    for para in paragraphs:
        if len(chunk) + len(para) < max_len:
            chunk += para + "\n"
        else:
            chunks.append(chunk.strip())
            chunk = para + "\n"
    if chunk.strip():
        chunks.append(chunk.strip())
    return chunks

def clean_line(line):
    line = re.sub(r"\s+", " ", line)
    line = re.sub(r"[^\x00-\x7F]+", " ", line)
    return line.strip()

def format_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    current_section = []
    formatted_sections = []

    for line in lines:
        line = clean_line(line)
        if not line:
            continue

        if is_heading(line):
            if current_section:
                content = "\n".join(current_section).strip()
                chunks = smart_chunk(content)
                for chunk in chunks:
                    formatted_sections.append(f"=== Section ===\n{chunk}\n=== End ===")
                current_section = []

            formatted_sections.append(f"=== Section: {line.title()} ===")
        else:
            current_section.append(line)

    if current_section:
        content = "\n".join(current_section).strip()
        chunks = smart_chunk(content)
        for chunk in chunks:
            formatted_sections.append(f"=== Section ===\n{chunk}\n=== End ===")

    return "\n\n".join(formatted_sections)

def process_all_files():
    print(f"Scanning directory: {INPUT_DIR}")
    for filename in os.listdir(INPUT_DIR):
        if not filename.endswith(".txt"):
            continue
        input_path = os.path.join(INPUT_DIR, filename)
        output_path = os.path.join(OUTPUT_DIR, filename)
        print(f"🔧 Formatting: {filename}")

        try:
            formatted_text = format_file(input_path)
            if formatted_text.strip():
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(formatted_text)
                print(f"✅ Done: {filename}")
            else:
                print(f"⚠️ Skipped empty output: {filename}")
        except Exception as e:
            print(f"❌ Error formatting {filename}: {e}")

if __name__ == "__main__":
    process_all_files()