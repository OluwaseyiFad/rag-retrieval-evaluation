from rank_bm25 import BM25Okapi

from contextual_upgrade_phase.chunking import generate_chunks_with_context
from comparison_phase.retrieval import write_results
from sources.documents import all_documents
from sources.queries import queries


def tokenize(text):
    return text.lower().strip()


def create_sparse_index(chunks):
    tokenized_corpus = []
    for chunk in chunks:
        combined_chunk = f"Context: {chunk['context']}\nContent: {chunk['text']}"
        tokenized_corpus.append(tokenize(combined_chunk))
    return BM25Okapi(tokenized_corpus)



def retrieve(query, bm25_index, chunks, top_k):
    tokenized_query = tokenize(query.strip())
    # Get scores for all chunks against the query
    scores = bm25_index.get_scores(tokenized_query)
    # Sort indices to find the highest scoring chunks (highest first)
    top_indices = scores.argsort()[-top_k:][::-1]
    results = []
    for idx in top_indices:
        chunk = chunks[idx]
        results.append({
            "score": float(scores[idx]),
            "text": chunk["text"],
            "source": chunk["source"],
            "chunk": chunk["chunk"]
        })
        
    return results


chunks = generate_chunks_with_context(all_documents)
bm25_index = create_sparse_index(chunks)

with open("result.txt", "w", encoding="utf-8") as f:
    for query in queries:
        results = retrieve(query["query"],  bm25_index, chunks, 3)
        f.write(f"\nquery: {query["query"]}")
        write_results("Recursive with context using sparse retrieval", results, f)
        f.write("\n\n\n\n")

    