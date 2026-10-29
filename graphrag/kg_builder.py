import os
from dotenv import load_dotenv
import asyncio
from neo4j import GraphDatabase
from neo4j_graphrag.llm import OpenAILLM
from neo4j_graphrag.embeddings import OllamaEmbeddings
from neo4j_graphrag.indexes import create_vector_index
from neo4j_graphrag.generation.prompts import ERExtractionTemplate
from neo4j_graphrag.components.schema import GraphSchema
from neo4j_graphrag.experimental.pipeline.kg_builder import SimpleKGPipeline
from neo4j_graphrag.components.text_splitters.fixed_size_splitter import FixedSizeSplitter

from .meridian_benchmark.sources.documents import all_documents

load_dotenv()

EMBEDDING_DIM = 384
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")

text_splitter = FixedSizeSplitter(chunk_size=500, chunk_overlap=100)

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

embedder = OllamaEmbeddings(
    model="locusai/all-minilm-l6-v2:latest"
)

# extraction prompt plus corpus rules iterated based on the defects found by graph_coverage
EXTRACTION_PROMPT = """
You are a top-tier algorithm designed for extracting
information in structured formats to build a knowledge graph.

Extract the entities (nodes) and specify their type from the following text.
Also extract the relationships between these nodes.

Return result as JSON using the following format:
{{"nodes": [ {{"id": "0", "label": "<node type>", "properties": {{"name": "<name from the text>"}} }}],
"relationships": [{{"type": "<RELATIONSHIP_TYPE>", "start_node_id": "0", "end_node_id": "1", "properties": {{}} }}] }}

Use only the following node and relationship types (if provided):
{schema}

Assign a unique ID (string) to each node, and reuse it to define relationships.
Do respect the source and target node types for relationship and
the relationship direction.

Rules for this text:
- Use the full proper name of every entity. When the text gives a short form ("X, also called Y"),
  put Y in the aliases property of X and do not create a separate entity for Y.
- A Person is a human being with a first and last name. Services, suppliers, interfaces and teams are never a Person.
- A sentence "A uses the B supplied by C" gives exactly two relationships: A USES_INTERFACE B and C SUPPLIES B.
  Never attach a supplier to an interface that comes from a different sentence.
  Handle each sentence on its own. Illustration only, never output these names:
  Text: Quill service uses the tracking feed supplied by Nimbus Logistics, also called NL.
  Output: {{"nodes": [{{"id": "0", "label": "Service", "properties": {{"name": "Quill service"}} }},
  {{"id": "1", "label": "SupplierInterface", "properties": {{"name": "tracking feed"}} }},
  {{"id": "2", "label": "Supplier", "properties": {{"name": "Nimbus Logistics", "aliases": "NL"}} }}],
  "relationships": [{{"type": "USES_INTERFACE", "start_node_id": "0", "end_node_id": "1", "properties": {{}} }},
  {{"type": "SUPPLIES", "start_node_id": "2", "end_node_id": "1", "properties": {{}} }}] }}
- Fill in every property the text states, even the optional ones: Incident date, impact, trigger and detection;
  CorrectiveAction category, status, due_date and closed_date; Allocation amount (integer) and valid_until;
  Deliverable status and date; Milestone date and previous_date.
- Write dates as YYYY-MM-DD. If the text gives a date without a year, use the year from the title of the text.
- Extract every relationship the text states, one per fact. Do not skip any.
- Never invent an entity or a value. Omit any property the text does not state. Never write N/A or Not specified.

Make sure you adhere to the following rules to produce valid JSON objects:
- Do not return any additional information other than the JSON in it.
- Omit any backticks around the JSON - simply output the JSON on its own.
- The JSON object must not wrapped into a list - it is its own JSON object.
- Property names must be enclosed in double quotes

Examples:
{examples}

Input text:

{text}
"""

# Alias nodes (LDG, GH, ...) are created by documents that never define them, so they are merged afterwards
MERGE_ALIASES_QUERY = """
MATCH (canon:__Entity__) WHERE canon.aliases IS NOT NULL
UNWIND split(toString(canon.aliases), ',') AS alias
WITH canon, trim(alias) AS alias WHERE alias <> ''
MATCH (dup:__Entity__)
WHERE dup <> canon AND dup.name = alias
  AND (dup.aliases IS NULL OR size(dup.name) < size(canon.name))
  AND any(l IN labels(dup) WHERE l IN labels(canon) AND NOT l STARTS WITH '__')
WITH dup, head(collect(canon)) AS canon
WITH canon, collect(DISTINCT dup) AS dups
CALL apoc.refactor.mergeNodes([canon] + dups, {properties: 'discard', mergeRels: true}) YIELD node
RETURN count(node) AS merged
"""


def build_pipeline(driver):
    return SimpleKGPipeline(
        llm=local_llm,
        driver=driver,
        neo4j_database=NEO4J_DATABASE,
        embedder=embedder,
        from_file=False,
        text_splitter=text_splitter,
        schema=GraphSchema.from_file("graphrag/schema.json"),
        prompt_template=ERExtractionTemplate(template=EXTRACTION_PROMPT),
        )


async def main():
    neo4j_driver = GraphDatabase.driver(
        os.getenv("NEO4J_URI"),
        auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))
    )
    try:
        neo4j_driver.verify_connectivity()
        # Create vector index since SimpleKGPipeline doesnt create one for its embeddings
        create_vector_index(
            neo4j_driver,
            name="chunk_embeddings",
            label="Chunk",
            embedding_property="embedding",
            dimensions=EMBEDDING_DIM,
            similarity_fn="cosine",
            fail_if_exists=False,
            neo4j_database=NEO4J_DATABASE,
        )
        kg_builder = build_pipeline(neo4j_driver)
        for document in all_documents:
            try:
                result = await kg_builder.run_async(text=document["text"], file_path=document["source"])
                print(document["source"], result.result)
            except Exception as exc:
                print(f"The SimpleKGPipeline failed for {document["source"]} due to {exc}")
        merged = neo4j_driver.execute_query(MERGE_ALIASES_QUERY, database_=NEO4J_DATABASE).records
        print(f"Merged alias nodes into {merged[0]['merged'] if merged else 0} canonical entities")
    finally:
        neo4j_driver.close()
        await local_llm.aclose()            


if __name__ == "__main__":
    asyncio.run(main())