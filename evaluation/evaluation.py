import copy
from sentence_transformers import SentenceTransformer, CrossEncoder

from contextual_upgrade_phase.chunking import generate_chunks_with_context
from hybrid_search_and_reranking_phase.sparse_retrieval import create_sparse_index, retrieve as sparse_retrieve
from hybrid_search_and_reranking_phase.dense_retrieval import create_index, retrieve as dense_retrieve
from hybrid_search_and_reranking_phase.reranking import rrf, rerank
from sources.documents import all_documents
from sources.queries import queries


def normalize(text):
    return " ".join(text.lower().split())


# Indices of the evidence facts found in a chunk (a list fact holds alternative quotes)
def facts_in_chunk(chunk, evidence):
    text = normalize(chunk["text"])
    found = set()
    for i, fact in enumerate(evidence):
        quotes = fact if isinstance(fact, list) else [fact]
        if any(normalize(quote) in text for quote in quotes):
            found.add(i)
    return found


# Share of the needed facts found in the top k chunks
def recall_at_k(results, evidence, k):
    found = set()
    for chunk in results[:k]:
        found |= facts_in_chunk(chunk, evidence)
    return len(found) / len(evidence)


# 1 / rank of the first chunk containing any needed fact
def reciprocal_rank(results, evidence):
    for rank, chunk in enumerate(results, start=1):
        if facts_in_chunk(chunk, evidence):
            return 1 / rank
    return 0.0


if __name__ == "__main__":
    model = SentenceTransformer("all-MiniLM-L6-V2")
    reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

    chunks = generate_chunks_with_context(all_documents)
    bm25_index = create_sparse_index(chunks)
    embeddings_index = create_index(chunks, model)

    scores = {"Dense": [], "Sparse": [], "Hybrid RRF": [], "Hybrid RRF + rerank": []}
    for query in queries:
        dense_results = dense_retrieve(query["query"], embeddings_index, chunks, model, 10)
        sparse_results = sparse_retrieve(query["query"], bm25_index, chunks, 10)
        rrf_results = rrf(dense_results, sparse_results)
        reranked_results = rerank(query["query"], copy.deepcopy(rrf_results), reranker, top_k=10)
        all_results = [dense_results, sparse_results, rrf_results, reranked_results]
        for method, results in zip(scores, all_results):
            scores[method].append((
                recall_at_k(results, query["evidence"], 3),
                recall_at_k(results, query["evidence"], 5),
                reciprocal_rank(results, query["evidence"]),
            ))

    print(f"{'Method':<22}{'Recall@3':<10}{'Recall@5':<10}MRR")
    for method, rows in scores.items():
        r3, r5, mrr = (sum(column) / len(rows) for column in zip(*rows))
        print(f"{method:<22}{r3:<10.3f}{r5:<10.3f}{mrr:.3f}")
