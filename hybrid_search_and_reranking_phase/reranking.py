# Reciprocal rank fusion
from sentence_transformers import SentenceTransformer
from chunking_comparison_phase.retrieval import write_results
from contextual_upgrade_phase.chunking import generate_chunks_with_context
from .sparse_retrieval import create_sparse_index, retrieve as sparse_retrieve
from .dense_retrieval import create_index, retrieve as dense_retrieve
from sources.documents import all_documents
from sources.queries import queries


model = SentenceTransformer("all-MiniLM-L6-V2")

chunks = generate_chunks_with_context(all_documents)

bm25_index = create_sparse_index(chunks)
embeddings_index = create_index(chunks)


def rrf(dense_results, sparse_results, k=60, top_k=3):
    fused = {}
    k = 60
    for results in (dense_results, sparse_results):
        for rank, result in enumerate(results, start=1):
            key = (result["source"], result["chunk"])
            if key not in fused:
                fused[key] = {**result, "score": 0.0}
            fused[key]["score"] += (1 / (rank+k))  # If a chunk gets found twice, it gets scored twice
    return sorted(fused.values(), key=lambda r: r["score"], reverse=True)[:top_k]


        

with open("hybrid_retrieval_with_rrf_result.txt", "w", encoding="utf-8") as f:
    for query in queries:
        dense_results = dense_retrieve(query["query"], embeddings_index, chunks, model, top_k=3)
        sparse_results = sparse_retrieve(query["query"],  bm25_index, chunks, 3)
        rrf_results = rrf(dense_results, sparse_results)
        f.write(f"\nquery: {query["query"]}")
        write_results("Hybrid (Sparse + Dense) Retrieval with RRF Reranker", rrf_results, f)
        f.write("\n\n\n\n")