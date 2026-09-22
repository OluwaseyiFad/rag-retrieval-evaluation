from pathlib import Path
from process_pdf import extract_pdf


pdf_folder = Path("sources")

all_documents = []

for pdf_path in pdf_folder.glob("*.pdf"):
    documents = extract_pdf(pdf_path)
    all_documents.extend(documents)
    

def fixed_size_chunk_text(text, chunk_size=500, overlap=100):
    chunks = []

    start = 0

    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])

        start += chunk_size - overlap

    return chunks

