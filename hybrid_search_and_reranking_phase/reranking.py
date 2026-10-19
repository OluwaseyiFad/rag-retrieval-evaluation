# Reciprocal rank fusion
from sentence_transformers import SentenceTransformer, CrossEncoder
from chunking_comparison_phase.retrieval import write_results
from contextual_upgrade_phase.chunking import generate_chunks_with_context
from .sparse_retrieval import create_sparse_index, retrieve as sparse_retrieve
from .dense_retrieval import create_index, retrieve as dense_retrieve
from sources.documents import all_documents
from sources.queries import queries


# Fuse dense_results + sparse_results using reciprocal rank fusion
def rrf(dense_results, sparse_results, k=60):
    fused = {}
    for results in (dense_results, sparse_results):
        for rank, result in enumerate(results, start=1):
            key = (result["source"], result["chunk"])
            if key not in fused:
                fused[key] = {**result, "score": 0.0}
            fused[key]["score"] += (1 / (rank+k))  # If a chunk gets found twice, it gets scored twice
    return sorted(fused.values(), key=lambda r: r["score"], reverse=True)

# Cross Encoder Reranking 
def rerank(query, candidates, reranker, top_k=3):
    pairs = [(query, candidate["text"]) for candidate in candidates]
    scores = reranker.predict(pairs)  # Higher means more relevant
    for candidate, score in zip(candidates, scores):
        candidate["score"] = float(score)  # score is a numpy number
    return sorted(candidates, key=lambda candidate: candidate["score"], reverse=True)[:top_k]
 

if __name__ == "__main__":
    model = SentenceTransformer("all-MiniLM-L6-V2")
    reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

    chunks = generate_chunks_with_context(all_documents)

    bm25_index = create_sparse_index(chunks=chunks)
    embeddings_index = create_index(chunks=chunks, model=model)
  
    with open("hybrid_retrieval_with_rrf_and_CERerank_result.txt", "w", encoding="utf-8") as f:
        for query in queries:
            dense_results = dense_retrieve(query["query"], embeddings_index, chunks, model, 10)
            sparse_results = sparse_retrieve(query["query"],  bm25_index, chunks, 10)
            rrf_results = rrf(dense_results, sparse_results)
            reranked_results = rerank(query["query"], rrf_results, reranker)
            f.write(f"\nquery: {query["query"]}")
            write_results("Hybrid (Sparse + Dense) Retrieval + RRF + Cross-Encoder Rerank", reranked_results, f)
            f.write("\n\n\n\n")