import os
from docx import Document

# Hardcoded folder paths
SRT_FOLDER = r"C:\Users\sakae\VISPER - Translation Model\SRT Files"
DOCX_FOLDER = r"C:\Users\sakae\VISPER - Translation Model\SRT - DOCX"

def srt_to_docx(srt_path, docx_path):
    doc = Document()
    with open(srt_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line in lines:
        # Preserve line breaks, numbers, timestamps, tags (<b>, etc.)
        doc.add_paragraph(line.rstrip("\n"))
    doc.save(docx_path)

def main():
    if not os.path.exists(DOCX_FOLDER):
        os.makedirs(DOCX_FOLDER)

    for filename in os.listdir(SRT_FOLDER):
        if filename.endswith(".srt"):
            srt_path = os.path.join(SRT_FOLDER, filename)
            docx_path = os.path.join(DOCX_FOLDER, os.path.splitext(filename)[0] + ".docx")
            srt_to_docx(srt_path, docx_path)
            print(f"Converted: {filename} → {os.path.basename(docx_path)}")

if __name__ == "__main__":
    main()
