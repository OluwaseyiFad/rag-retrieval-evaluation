import os
from pathlib import Path

from dotenv import load_dotenv
from neo4j import Driver, GraphDatabase


def create_neo4j_driver() -> Driver:
    load_dotenv(Path(__file__).resolve().parents[1] / ".env")
    required = ("NEO4J_URI", "NEO4J_USERNAME", "NEO4J_PASSWORD")
    missing = [name for name in required if not os.getenv(name)]
    if missing:
        raise ValueError(f"Set these variables in .env: {', '.join(missing)}")
    return GraphDatabase.driver(
        os.environ["NEO4J_URI"],
        auth=(os.environ["NEO4J_USERNAME"], os.environ["NEO4J_PASSWORD"]),
    )


if __name__ == "__main__":
    with create_neo4j_driver() as neo4j_driver:
        neo4j_driver.verify_connectivity()
        print("Connected to Neo4j.")
