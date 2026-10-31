from neo4j_graphrag.retrievers import VectorCypherRetriever
from neo4j_graphrag.embeddings import OllamaEmbeddings

from .neo4j_driver import create_neo4j_driver


# RETRIEVAL_QUERY = """
# MATCH (node)-[:FROM_DOCUMENT]->(d:Document)
# OPTIONAL MATCH (node)<-[:FROM_CHUNK]-(e:__Entity__)
# OPTIONAL MATCH (e)-[r]-(o:__Entity__)
# WITH node, d, score,
#      collect(DISTINCT startNode(r).name + ' ' + type(r) + ' ' + endNode(r).name) AS triples
# RETURN node.text AS text, d.path AS source, node.index AS chunk, score, triples
# """

RETRIEVAL_QUERY = """
MATCH (node)-[:FROM_DOCUMENT]->(d:Document)
OPTIONAL MATCH (node)<-[:FROM_CHUNK]-(e:__Entity__)
OPTIONAL MATCH (e)-[r1]-(o:__Entity__)
OPTIONAL MATCH (o)-[r2]-(o2:__Entity__)
WITH node, d, score, collect(DISTINCT r1) + collect(DISTINCT r2) AS rels
UNWIND CASE WHEN size(rels) = 0 THEN [null] ELSE rels END AS r
WITH node, d, score,
     collect(DISTINCT startNode(r).name + ' ' + type(r) + ' ' + endNode(r).name) AS triples
RETURN node.text AS text, d.path AS source, node.index AS chunk, score, triples
"""


driver = create_neo4j_driver()
embedder = OllamaEmbeddings(
    model="locusai/all-minilm-l6-v2:latest"
)
retriever = VectorCypherRetriever(
    driver=driver,
    index_name="chunk_embeddings",
    embedder=embedder,
    retrieval_query=RETRIEVAL_QUERY,
    neo4j_database="neo4j",
)


def retrieve(question, top_k=3):
    result = retriever.get_search_results(query_text=question, top_k=top_k)
    result = [dict(record) for record in result.records]
    return result


# print results
def print_results(strategy, results):
    print(f"\n{'=' * 80}")
    print(strategy.upper())
    print(f"{'=' * 80}")
    for rank, result in enumerate(results, start=1):
        print(f"\nRank: {rank}")
        print(f"Score: {result['score']:.4f}")
        print(f"Source: {result['source']}")
        print(f"Chunk: {result['chunk']}")
        print(f"Graph facts: \n{"\n".join(result['triples'])}")
        print(f"Text:\n{result['text'][:1000]}\n\n----------------------\n\n")


# Write results
def write_results(strategy, results, f):
    f.write(f"\n{'=' * 80}")
    f.write(strategy.upper())
    f.write(f"{'=' * 80}")
    for rank, result in enumerate(results, start=1):
        f.write(f"\nRank: {rank}")
        f.write(f"\nScore: {result['score']:.4f}")
        f.write(f"\nSource: {result['source']}")
        f.write(f"\nChunk: {result['chunk']}")
        f.write(f"\nGraph facts: \n{"\n".join(result['triples'])}")
        f.write(f"\nText:\n{result['text'][:1000]}\n\n----------------------\n\n")


if __name__ == "__main__":
    try:
        sample_q = "How is Beacon Warehouse connected to Pinebridge Data?"
        results = retrieve(sample_q, 6)
        print_results("graphrag", results)
        with open("graphrag/retriever_sample_results.txt", "w") as f:
            write_results("graphrag", results, f)
    finally:
        driver.close()