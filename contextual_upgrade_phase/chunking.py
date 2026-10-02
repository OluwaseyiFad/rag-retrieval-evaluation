import json
import torch
from pathlib import Path
from transformers import pipeline

from comparison_phase.recursive_chunking import recursive_chunk_text

CONTEXT_CACHE = Path("contextual_upgrade_phase/contexts.json")

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
def generate_chunks_with_context(all_documents):
    all_chunks = []
    if CONTEXT_CACHE.exists():
        all_chunks = json.loads(CONTEXT_CACHE.read_text(encoding="utf-8"))
    else:
        for document in all_documents:
            for chunk_number, chunk in enumerate(recursive_chunk_text(document["text"])):
                all_chunks.append({
                    "context": situate_context(document["text"], chunk),
                    "text": chunk,
                    "source": document["source"],
                    "chunk": chunk_number,
                })
        CONTEXT_CACHE.write_text(json.dumps(all_chunks, indent=2), encoding="utf-8")
    return all_chunks
    