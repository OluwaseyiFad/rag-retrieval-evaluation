import json
import asyncio
from pathlib import Path

from transformers import AutoTokenizer
from neo4j_graphrag.llm import OpenAILLM
from .graph_retriever import retrieve


QUERIES = Path(__file__).parent / "meridian_benchmark" / "queries.json"


local_llm = OpenAILLM(
    model_name="qwen2.5:14b",
    base_url="http://127.0.0.1:11434/v1",
    api_key="ollama",
    model_params={
        "temperature": 0,
        "max_tokens": 4096,
    },
    timeout=300,
    max_retries=0,
)
tok = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-14B-Instruct")


async def main():
    results = []
    queries = json.loads(QUERIES.read_text())
    try:
        for query in queries:
            try:
                seen = set()  # Helps to track duplicate in graph facts
                result = retrieve(query["query"], 6)
                context = "\n"
                sources = []
                for r in result:
                    triples = []
                    for triple in r["triples"]:
                        if triple not in seen:
                            triples.append(triple)
                        seen.add(triple)
                    sources.append(r['source'])
                    context = context + f"[Source: {r['source']}]\n" + r["text"] + f"\nGraph facts: \n{"\n".join(triples)}\n...\n"
                prompt = (
                    "Answer the question using only the context below. "
                    "The context has source text and graph facts of the form 'A RELATION B'. "
                    "If the context does not state the answer, say 'not stated'. "
                    "Do not use outside knowledge. Give a short, direct answer.\n\n"
                    f"Context:\n{context}\n\n"
                    f"Question: {query['query']}\n\n"
                    "Answer:"
                )
                prompt_token = len(tok(prompt).input_ids)
                print(f"The prompt token is: {prompt_token}...\n")
                reply = await local_llm.ainvoke(prompt)
                answer = reply.content.strip()
                results.append({"id": query["id"], "type": query["type"], "query": query["query"], "answer": answer, "sources": sources})
            except Exception as exc:
                print(f"\nError occured during answering... due to {exc}\n")
                results.append({"id": query["id"], "type": query["type"], "query": query["query"], "answer": None, "sources": []})
        Path(__file__).with_name("answers_graph.json").write_text(json.dumps(results, indent=2))
    finally:
        await local_llm.aclose()
        
if __name__ == "__main__":
    asyncio.run(main())