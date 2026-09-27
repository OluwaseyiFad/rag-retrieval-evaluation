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


# print results
def print_results(strategy, results):
    print(f"\n{'=' * 80}")
    print(strategy.upper())
    print(f"{'=' * 80}")
    for rank, result in enumerate(results, start=1):
        print(f"\nRank: {rank}")
        print(f"Score: {result['score']:.4f}")
        print(f"Source: {result['source']}")
        print(f"Page: {result['page']}")
        print(f"Chunk: {result['chunk']}")
        print(f"Text:\n{result['text'][:1000]}")


fixed_chunks = generate_chunks(fixed_size_chunk_text)
recursive_chunks = generate_chunks(recursive_chunk_text)
semantic_chunks = generate_chunks(semantic_chunk_text)

fixed_index = create_index(fixed_chunks, model)
recursive_index = create_index(recursive_chunks, model)
semantic_index = create_index(semantic_chunks, model)

queries = [
    "How does user feedback affect the dynamic routing framework's handling of future queries?",

    "How does the dynamic RAG framework decide whether to use a canned response or retrieve information through RAG?",

    "What happens when the confidence score for an intent falls below the threshold for using a predefined FAQ response?",

    "What accuracy and response latency does the dynamic routing framework report?",

    "What are the two strategies used for adaptive retrieval and the two strategies used for query reformulation in multiturn RAG?",

    "How does SSRAG process a user's query before retrieving the final context?",

    "How does SSRAG combine vector-based retrieval with graph-based retrieval?",

    "Why is chunking an important preprocessing step in RAG systems?",

    "How does hybrid search combine keyword search and semantic search?",

    "Why is query reformulation necessary in multi-turn RAG systems?"
]


# Examinining the chunks for each strategies
# Ensure suitability for comparison
print("Fixed chunks: ", len(fixed_chunks))
print("Recursive chunks: ", len(recursive_chunks))
print("Semantic chunks: ", len(semantic_chunks))

def average_chunk_size(chunks):
    return sum(len(c["text"]) for c in chunks) / len(chunks)

print("Fixed avg:", average_chunk_size(fixed_chunks))
print("Recursive avg:", average_chunk_size(recursive_chunks))
print("Semantic avg:", average_chunk_size(semantic_chunks))


fixed_results = retrieve(queries[0], fixed_index, fixed_chunks, model, top_k=3)
recursive_results = retrieve(queries[0], recursive_index, recursive_chunks, model, top_k=3)
semantic_results = retrieve(queries[0], semantic_index, semantic_chunks, model, top_k=3)

print_results("Fixed", fixed_results)
print_results("Recursive", recursive_results)
print_results("Semantic", semantic_results)