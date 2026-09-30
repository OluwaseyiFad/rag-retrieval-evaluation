import re
import numpy as np
from sentence_transformers import SentenceTransformer


model = SentenceTransformer("all-MiniLM-L6-v2")

    
def split_sentences(text):
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if s.strip()]


def get_similarities(sentences):
    if len(sentences) <= 1:
        return []
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
    max_chunk_size=500
):
    sentences = split_sentences(text)
    if len(sentences) <= 1:
        return []
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
    



