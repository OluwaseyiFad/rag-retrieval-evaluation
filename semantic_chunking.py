import re
import numpy as np
from pathlib import Path
from process_pdf import extract_pdf
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


pdf_folder = Path("sources")

all_documents = []
model = SentenceTransformer("all-MiniLM-L6-v2")

for pdf_path in pdf_folder.glob("*.pdf"):
    documents = extract_pdf(pdf_path)
    all_documents.extend(documents)
    
    
def split_sentences(text):
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if s.strip()]


def get_similarities(sentences):
    if len(sentences) <= 1:
        return sentences
    embeddings = model.encode(sentences, normalize_embeddings=True)
    similarities = []
    for i in range(len(sentences) - 1):
        similarity = np.dot(
            embeddings[i],
            embeddings[i + 1]
        )
        similarities.append(float(similarity))
    return similarities
    

def semantic_chunk_text(
    text,
    breakpoint_percentile=20,
    max_chunk_size=1000
):
    sentences = split_sentences(text)
    if len(sentences) <= 1:
        return sentences
    similarities = get_similarities(sentences)
    threshold = np.percentile(similarities, breakpoint_percentile)
    chunks = []
    current_chunk = [sentences[0]]
    for i, similarity in enumerate(similarities):
        next_sentence = sentences[i + 1]
        candidate = " ".join(current_chunk + [next_sentence])
        # falls below sementic similarity threshhold or greater than max chunk size
        if similarity <= threshold or len(candidate) > max_chunk_size:
            chunks.append(" ".join(current_chunk))
            current_chunk = [next_sentence]
        else:
            current_chunk.append(next_sentence)
            
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    return chunks
    


all_chunks = []

for document in all_documents:
    chunks = semantic_chunk_text(document["text"])
    for chunk_number, chunk in enumerate(chunks):
        all_chunks.append({
            "text": chunk,
            "source": document["source"],
            "page": document["page"],
            "chunk": chunk_number
        })


print(all_chunks[:2])

