import asyncio, json, os
from pathlib import Path
from dotenv import load_dotenv
from neo4j_graphrag.llm import OpenAILLM
from .neo4j_driver import create_neo4j_driver

load_dotenv()

QUERIES = Path(__file__).parent / "meridian_benchmark" / "queries.json"
DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")


# Better to use a stronger and different model as judge
local_llm = OpenAILLM(
    model_name="qwen2.5:7b",
    base_url="http://127.0.0.1:11434/v1",
    api_key="ollama",
    model_params={
        "temperature": 0,
        "max_tokens": 50,  # Only need yes or no
    },
    timeout=300,
    max_retries=0,
)


# With triples, the judge can check if the graph contains enough information to support known facts
# Therefore enabling us to ascertain the graph quality 
TRIPLES_QUERY = """
MATCH (d:Document {path: $stem})<-[:FROM_DOCUMENT]-(c:Chunk)<-[:FROM_CHUNK]-(a)
MATCH (a)-[r]->(b)-[:FROM_CHUNK]->(c)
WHERE NOT type(r) IN ['FROM_CHUNK', 'FROM_DOCUMENT', 'NEXT_CHUNK']
RETURN DISTINCT a.name AS a, type(r) AS r, b.name AS b
"""

def triples_for_document(driver, stem):
    records = driver.execute_query(
        TRIPLES_QUERY, stem=stem, database_=DATABASE, routing_="r"
    ).records
    return [f"{r['a']} {r['r']} {r['b']}" for r in records]


def report(results):
    supported_cnts = {"single_hop": 0, "multi_hop": 0, "connection": 0, "aggregation": 0}
    unsupported_cnts = {"single_hop": 0, "multi_hop": 0, "connection": 0, "aggregation": 0}
    for result in results:
        if result["supported"] is None:
            print("An error occured while judging...")
        elif result["supported"]:
            supported_cnts[result["type"]] += 1
        else:
            unsupported_cnts[result["type"]] += 1
    for k, v in supported_cnts.items():
        print(f"Type {k} facts is supported by the triples {v} times and unsupported {unsupported_cnts[k]} times")
        
    Path(__file__).with_name("coverage_baseline.json").write_text(json.dumps(results, indent=2))



async def judge(fact, triples):
    prompt = (
        "Graph triples:\n" + "\n".join(triples) + f"\n\nFact: {fact}\n\n"
        "Do the triples together state this fact, including every clause? "
        "Answer only YES or NO."
    )
    try:
        reply = await local_llm.ainvoke(prompt)
        # Better to investigate the LLM output return either YES OR NO
        verdict = reply.content.strip().upper()
        if verdict not in ("YES", "NO"):
            print("LLM disobeyed instruction") # Must ensure this is not printed
        return verdict.startswith("YES")
    except Exception:
        return None
    

async def main():
    queries = json.loads(QUERIES.read_text())
    queries = [q for q in queries if q.get("expected_facts")]
    driver = create_neo4j_driver()
    results = []
    try:
        for q in queries:
            all_triples = set()
            for doc in q["evidence_documents"]:
                for t in triples_for_document(driver, Path(doc).stem):
                    all_triples.add(t)
            triples = sorted(all_triples)  # To ensure similar order across runs
            for fact in q["expected_facts"]:
                supported = await judge(fact, triples)
                results.append({
                    "id": q["id"], "type": q["type"], "fact": fact,
                    "supported": supported, "n_triples": len(triples),
                })
    finally:
        driver.close()
        await local_llm.aclose()
    
    report(results)
        
        
if __name__ == "__main__":
    asyncio.run(main())