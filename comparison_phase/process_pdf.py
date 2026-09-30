import pymupdf
import re


def clean_text(text):
    text = re.sub(r"[ \t\r\f\v]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = text.strip()
    return text

def extract_pdf(pdf_path):
    documents = []
    
    with pymupdf.open(pdf_path) as pdf:
        for page_number, page in enumerate(pdf, start=1):
            text = page.get_text("text", sort=True)  # preserves the reading order from top left to bottom right
            text = clean_text(text)
            if text:
                documents.append({
                    "text": text,
                    "source": pdf_path.name,
                    "page": page_number
                })
                
    return documents

    

