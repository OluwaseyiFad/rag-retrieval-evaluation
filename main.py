import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from semantic_chunking import semantic_chunk_text
from fixed_chunking import fixed_size_chunk_text
from recursive_chunking import recursive_chunk_text
from pathlib import Path
from process_pdf import extract_pdf


pdf_folder = Path("sources")

all_documents = []

for pdf_path in pdf_folder.glob("*.pdf"):
    documents = extract_pdf(pdf_path)
    all_documents.extend(documents)

model = SentenceTransformer("all-MiniLM-L6-V2")


def create_index(chunks, model):
    texts = [ chunk["text"] for chunk in chunks]
    embeddings = model.encode(texts, normalize_embeddings=True, convert_to_numpy=True)
    embeddings = embeddings.astype("float32")
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension) # initialize with vector dimension
    index.add(embeddings)
    return index



# For fixed, recursive, and semantic chunking
def generate_chunks(chunk_func):
    all_chunks = []
    for document in all_documents:
        chunks = chunk_func(
            document["text"]
        )
        for chunk_number, chunk in enumerate(chunks):
            all_chunks.append({
                "text": chunk,
                "source": document["source"],
                "page": document["page"],
                "chunk": chunk_number
            })
    return all_chunks


# Retrieval
def retrieve(query, index, chunks, model, top_k=3):
    query_embedding = model.encode([query], normalize_embeddings=True, convert_to_numpy=True)
    query_embedding = query_embedding.astype("float32")
    scores, indices = index.search(query_embedding, top_k)
    results = []
    for score, idx in zip(scores[0], indices[0]):
        chunk = chunks[idx]
        results.append({
            "score": float(score),
            "text": chunk["text"],
            "source": chunk["source"],
            "page": chunk["page"],
            "chunk": chunk["chunk"]
        })
        
    return results


fixed_chunks = generate_chunks(fixed_size_chunk_text)
recursive_chunks = generate_chunks(recursive_chunk_text)
semantic_chunks = generate_chunks(semantic_chunk_text)

fixed_index = create_index(fixed_chunks, model)
recursive_index = create_index(recursive_chunks, model)
semantic_index = create_index(semantic_chunks, model)

query = "what is dynamic RAQ?"

fixed_results = retrieve(query, fixed_index, fixed_chunks, model, top_k=3)
recursive_results = retrieve(query, recursive_index, recursive_chunks, model, top_k=3)
semantic_results = retrieve(query, semantic_index, semantic_chunks, model, top_k=3)

print(f"fixed results: \n{fixed_results}\n\n\n")
print(f"recursive results: \n{recursive_results}\n\n\n")
print(f"semantic results: \n{semantic_results}\n\n\n")