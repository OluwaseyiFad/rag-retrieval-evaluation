
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


# print results
def print_results(strategy, results):
    print(f"\n{'=' * 80}")
    print(strategy.upper())
    print(f"{'=' * 80}")
    for rank, result in enumerate(results, start=1):
        print(f"\nRank: {rank}")
        print(f"Score: {result['score']:.4f}")
        print(f"Source: {result['source']}")
        print(f"Chunk: {result['chunk']}")
        print(f"Text:\n{result['text'][:1000]}")

        
# Write results
def write_results(strategy, results, f):
    f.write(f"\n{'=' * 80}")
    f.write(strategy.upper())
    f.write(f"{'=' * 80}")
    for rank, result in enumerate(results, start=1):
        f.write(f"\nRank: {rank}")
        f.write(f"\nScore: {result['score']:.4f}")
        f.write(f"\nSource: {result['source']}")
        f.write(f"\nChunk: {result['chunk']}")
        f.write(f"\nText:\n{result['text'][:1000]}")

