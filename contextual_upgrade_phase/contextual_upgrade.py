import json
import torch
from transformers import pipeline
from pathlib import Path
import faiss
from sentence_transformers import SentenceTransformer

from comparison_phase.recursive_chunking import recursive_chunk_text
from comparison_phase.retrieval import write_results, retrieve
from sources.queries import queries

CONTEXT_CACHE = Path("contextual_upgrade_phase/contexts.json")

source_folder = Path("sources")

all_documents = []

for txt_path in source_folder.glob("*.txt"):
    text = txt_path.read_text(encoding="utf-8")
    all_documents.append({
            "text": text,
            "source": txt_path.name
    })
   
# print("All documents: ", all_documents) 

model = SentenceTransformer("all-MiniLM-L6-V2")


DOCUMENT_CONTEXT_PROMPT = """
<document>
{doc_content}
</document>
"""

CHUNK_CONTEXT_PROMPT = """
Here is the chunk we want to situate within the whole document
<chunk>
{chunk_content}
</chunk>
Please give in 1-2 sentences a short succinct context to situate this chunk within the overall document for the purposes of improving search retrieval of the chunk.
Answer only with the succinct context and nothing else.
"""

model_id = "HuggingFaceTB/SmolLM2-1.7B-Instruct"
pipe = pipeline(
    "text-generation",
    model=model_id,
    dtype=torch.bfloat16,
    device_map="auto",
)

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


# Generate context to be prepended to each chunk
def situate_context(doc, chunk):
    combined_content = f"{DOCUMENT_CONTEXT_PROMPT.format(doc_content=doc)}\n{CHUNK_CONTEXT_PROMPT.format(chunk_content=chunk)}"
    messages = [
        {
            "role": "user", 
            "content": combined_content
        },
    ]
    response = pipe(
        messages,
        max_new_tokens=100, # keeps context + chunk under 256-token limit
        do_sample=False, # same contexts on every run
        
    )
    return response[0]["generated_text"][-1]['content'].strip()

# To cache and reuse generated contexts
# If prompt or chunks change, delete contexts.json
if CONTEXT_CACHE.exists():
    all_chunks = json.loads(CONTEXT_CACHE.read_text(encoding="utf-8"))
else:
    all_chunks = []
    for document in all_documents:
        for chunk_number, chunk in enumerate(recursive_chunk_text(document["text"])):
            all_chunks.append({
                "context": situate_context(document["text"], chunk),
                "text": chunk,
                "source": document["source"],
                "chunk": chunk_number,
            })
    CONTEXT_CACHE.write_text(json.dumps(all_chunks, indent=2), encoding="utf-8")


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



