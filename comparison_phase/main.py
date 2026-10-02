import faiss
from sentence_transformers import SentenceTransformer


from .semantic_chunking import semantic_chunk_text
from .fixed_chunking import fixed_size_chunk_text
from .recursive_chunking import recursive_chunk_text
from sources.queries import queries
from sources.documents import all_documents
from .retrieval import retrieve, write_results


model = SentenceTransformer("all-MiniLM-L6-V2")


def create_index(chunks, model):
    texts = [chunk["text"] for chunk in chunks]
    embeddings = model.encode(texts, normalize_embeddings=True, convert_to_numpy=True)
    embeddings = embeddings.astype("float32")
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension) # initialize with vector dimension
    index.add(embeddings)
    return index



# For fixed, recursive, and semantic chunking
def generate_chunks(chunk_func, documents):
    all_chunks = []
    for document in documents:
        chunks = chunk_func(
            document["text"]
        )
        for chunk_number, chunk in enumerate(chunks):
            all_chunks.append({
                "text": chunk,
                "source": document["source"],
                "chunk": chunk_number
            })
    return all_chunks



def main():
    fixed_chunks = generate_chunks(fixed_size_chunk_text, all_documents)
    recursive_chunks = generate_chunks(recursive_chunk_text, all_documents)
    semantic_chunks = generate_chunks(semantic_chunk_text, all_documents)

    fixed_index = create_index(fixed_chunks, model)
    recursive_index = create_index(recursive_chunks, model)
    semantic_index = create_index(semantic_chunks, model)



    # Examinining the chunks for each strategies
    # Ensure suitability for comparison
    # print("Fixed chunks: ", len(fixed_chunks))
    # print("Recursive chunks: ", len(recursive_chunks))
    # print("Semantic chunks: ", len(semantic_chunks))

    # def average_chunk_size(chunks):
    #     return sum(len(c["text"]) for c in chunks) / len(chunks)

    # print("Fixed avg:", average_chunk_size(fixed_chunks))
    # print("Recursive avg:", average_chunk_size(recursive_chunks))
    # print("Semantic avg:", average_chunk_size(semantic_chunks))


    with open("result.txt", "w", encoding="utf-8") as f:
        for query in queries:
            fixed_results = retrieve(query["query"], fixed_index, fixed_chunks, model, top_k=3)
            recursive_results = retrieve(query["query"], recursive_index, recursive_chunks, model, top_k=3)
            semantic_results = retrieve(query["query"], semantic_index, semantic_chunks, model, top_k=3)
            f.write(f"\nquery: {query["query"]}")
            write_results("Fixed", fixed_results, f)
            write_results("Recursive", recursive_results, f)
            write_results("Semantic", semantic_results, f)
            f.write("\n\n\n\n")
            
            
if __name__ == "__main__":
    main()