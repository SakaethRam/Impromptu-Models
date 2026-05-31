import os
import html
from docx import Document

# Hardcoded folder paths
DOCX_FOLDER = r"C:\Users\sakae\VISPER - Translation Model\DeepL - DOCX"
SRT_FOLDER = r"C:\Users\sakae\VISPER - Translation Model\VISPER TRANSLATED SCRIPTS"

def clean_text(text: str) -> str:
    """
    Removes unnecessary HTML entities like &gt; &lt; &amp; etc.
    """
    return html.unescape(text.strip())

def docx_to_srt(docx_path, srt_path):
    doc = Document(docx_path)
    with open(srt_path, "w", encoding="utf-8") as f:
        for para in doc.paragraphs:
            text = clean_text(para.text)
            if text:
                f.write(text + "\n")
            else:
                f.write("\n")  # preserve blank lines

def main():
    if not os.path.exists(SRT_FOLDER):
        os.makedirs(SRT_FOLDER)

    for filename in os.listdir(DOCX_FOLDER):
        if filename.endswith(".docx"):
            docx_path = os.path.join(DOCX_FOLDER, filename)
            srt_path = os.path.join(SRT_FOLDER, os.path.splitext(filename)[0] + ".srt")
            docx_to_srt(docx_path, srt_path)
            print(f"Converted and cleaned: {filename} → {os.path.basename(srt_path)}")

if __name__ == "__main__":
    main()
