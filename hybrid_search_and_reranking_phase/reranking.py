# Reciprocal rank fusion
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
            