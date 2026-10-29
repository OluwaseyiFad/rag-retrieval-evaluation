import asyncio, json, os, sys
from pathlib import Path
from dotenv import load_dotenv
from neo4j_graphrag.llm import OpenAILLM
from .neo4j_driver import create_neo4j_driver

load_dotenv()

QUERIES = Path(__file__).parent / "meridian_benchmark" / "queries.json"
DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")


# Better to use a stronger and different model family as judge
local_llm = OpenAILLM(
    model_name="gemma3:27b",
    base_url="http://127.0.0.1:11434/v1",
    api_key="ollama",
    model_params={
        "temperature": 0,
        "max_tokens": 700,
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
PROPERTIES_QUERY = """
MATCH (d:Document {path: $stem})<-[:FROM_DOCUMENT]-(c:Chunk)<-[:FROM_CHUNK]-(n:__Entity__)
RETURN DISTINCT n.name AS name, properties(n) AS props
"""

def triples_for_document(driver, stem):
    triples = driver.execute_query(
        TRIPLES_QUERY, stem=stem, database_=DATABASE, routing_="r"
    ).records
    lines = [f"{r['a']} {r['r']} {r['b']}" for r in triples]
    
    entities = driver.execute_query(
        PROPERTIES_QUERY, stem=stem, database_=DATABASE, routing_="r"
    ).records
    
    for entity in entities:
        for k, v in entity["props"].items():
            # Filter out props already in lines or not needed
            if k not in ("name", "embedding", "id"):
                lines.append(f"{entity['name']} has {k}: {v}")
    return lines
                


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

    Path(__file__).with_name(f"coverage_{sys.argv[1] if len(sys.argv) > 1 else 'run'}.json").write_text(json.dumps(results, indent=2))



async def judge(fact, triples):
    prompt = (
        "Graph facts:\n" + "\n".join(triples) + f"\n\nFact to check: {fact}\n\n"
        "Relation names in the graph facts are equivalent to ordinary words: "
        "DEPENDS_ON = depends on, consumes, uses; LEADS = leads, is the lead of; "
        "OWNS = owns, is responsible for; MEMBER_OF = belongs to; "
        "SPONSORS = sponsors; SUPPLIES = supplies, provides.\n"
        "A clause may be supported by combining two or more graph facts that share an entity (for example 'A OWNS B' and 'C TARGETS B' together state that C targets something A owns); quote every fact you combine.\n"
        "Split ONLY the fact to check into its clauses (a name, a role, an "
        "amount, a date, a negation). Do not add clauses of your own. For each "
        "clause write one line in the form:\n"
        "CLAUSE: <the clause> | QUOTE: <the exact graph fact that states it, "
        "or none>\n"
        "A graph fact states a clause only if it contains the specific names, "
        "numbers and dates in that clause. Do not guess beyond that.\n"
        "Then, on a new last line, answer only YES if every clause has a "
        "quote, otherwise NO."
    )


    try:
        reply = await local_llm.ainvoke(prompt)
        llm_answer = reply.content.strip()
        last_line = llm_answer.splitlines()[-1] if llm_answer else ""
        verdict = last_line.strip().strip("*_ .`").upper()
        if verdict.startswith("YES"):
            return True, llm_answer
        elif verdict.startswith("NO"):
            return False, llm_answer
        else:
            return None, llm_answer
    except Exception as exc:
        print(f"Error {exc} occured while judging ....")
        return None, f"Error: {exc}"


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
                supported, judge_reply = await judge(fact, triples)
                results.append({
                    "id": q["id"], "type": q["type"], "fact": fact,
                    "supported": supported, "n_triples": len(triples),
                    "judge_reply": judge_reply,
                })
    finally:
        driver.close()
        await local_llm.aclose()

    report(results)

if __name__ == "__main__":
    asyncio.run(main())