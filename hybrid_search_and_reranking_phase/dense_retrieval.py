import faiss
from sentence_transformers import SentenceTransformer

from chunking_comparison_phase.retrieval import write_results
from contextual_upgrade_phase.chunking import generate_chunks_with_context
from sources.queries import queries
from sources.documents import all_documents


model = SentenceTransformer("all-MiniLM-L6-V2")


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
            "chunk": chunk["chunk"]
        })
        
    return results


# Create index
def create_index(chunks, model=SentenceTransformer("all-MiniLM-L6-V2"), with_context=True):
    if with_context:
        texts = [f"Context: {chunk['context']}\nContent: {chunk['text']}" for chunk in chunks]
    else:
        texts = [chunk["text"] for chunk in chunks]
    embeddings = model.encode(texts, normalize_embeddings=True, convert_to_numpy=True)
    embeddings = embeddings.astype("float32")
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension) # initialize with vector dimension
    index.add(embeddings)
    return index


all_chunks = generate_chunks_with_context(all_documents)

# Checks that nothing gets cut off
limit = model.max_seq_length
over = [
    (c["source"], c["chunk"], n)
    for c in all_chunks
    if (n := len(model.tokenizer(f"Context: {c['context']}\nContent: {c['text']}")["input_ids"])) > limit
]
print(f"{len(over)}/{len(all_chunks)} chunks exceed {limit} tokens:", over[:10])

index_with_context = create_index(all_chunks, model, True)

with open("dense_retrieval_result.txt", "w", encoding="utf-8") as f:
    for query in queries:
        results = retrieve(query["query"], index_with_context, all_chunks, model, top_k=3)
        f.write(f"\nquery: {query["query"]}")
        write_results("Recursive with context using dense retrieval", results, f)
        f.write("\n\n\n\n")
