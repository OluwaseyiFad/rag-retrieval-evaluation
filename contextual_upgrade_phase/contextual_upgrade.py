import faiss
from sentence_transformers import SentenceTransformer

from comparison_phase.retrieval import write_results, retrieve
from .chunking import generate_chunks_with_context
from sources.queries import queries
from sources.documents import all_documents


model = SentenceTransformer("all-MiniLM-L6-V2")


# Create index
def create_index(chunks, model, with_context):
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
index_without_context = create_index(all_chunks, model, False)

with open("result.txt", "w", encoding="utf-8") as f:
    for query in queries:
        with_context_results = retrieve(query["query"], index_with_context, all_chunks, model, top_k=3)
        without_context_results = retrieve(query["query"], index_without_context, all_chunks, model, top_k=3)
        f.write(f"\nquery: {query["query"]}")
        write_results("Recursive with context prepended", with_context_results, f)
        write_results("Recursive without context preprended", without_context_results, f)
        f.write("\n\n\n\n")



