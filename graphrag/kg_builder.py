import os
from dotenv import load_dotenv
import asyncio
from neo4j import GraphDatabase
from neo4j_graphrag.llm import OpenAILLM
from neo4j_graphrag.embeddings import OllamaEmbeddings
from neo4j_graphrag.indexes import create_vector_index
from neo4j_graphrag.components.schema import GraphSchema
from neo4j_graphrag.experimental.pipeline.kg_builder import SimpleKGPipeline
from neo4j_graphrag.components.text_splitters.fixed_size_splitter import FixedSizeSplitter

from .meridian_benchmark.sources.documents import all_documents

load_dotenv()

EMBEDDING_DIM = 384
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")

text_splitter = FixedSizeSplitter(chunk_size=500, chunk_overlap=100)

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


def build_pipeline(driver):
    return SimpleKGPipeline(
        llm=local_llm,
        driver=driver,
        neo4j_database=NEO4J_DATABASE,
        embedder=embedder,
        from_file=False,
        text_splitter=text_splitter,
        schema=GraphSchema.from_file("graphrag/schema.json"),
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
    finally:
        neo4j_driver.close()
        await local_llm.aclose()            


if __name__ == "__main__":
    asyncio.run(main())