import os
from pathlib import Path
from dotenv import load_dotenv
import asyncio
from neo4j import GraphDatabase
from neo4j_graphrag.llm import OpenAILLM
from neo4j_graphrag.embeddings import OllamaEmbeddings
from neo4j_graphrag.experimental.pipeline.kg_builder import SimpleKGPipeline

load_dotenv()

neo4j_driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI"),
    auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))
)
neo4j_driver.verify_connectivity()

local_llm = OpenAILLM(
    model_name="qwen2.5:7b",
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

kg_builder = SimpleKGPipeline(
    llm=local_llm,
    driver=neo4j_driver, 
    neo4j_database=os.getenv("NEO4J_DATABASE"), 
    embedder=embedder,
    from_file=False,
)

file_path = "graphrag/meridian_benchmark/sources/01_leadership_directory.txt"
text = Path(file_path).read_text(encoding="utf-8")
result = asyncio.run(kg_builder.run_async(text=text, file_path=file_path))
print(result.result)
