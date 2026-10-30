## Comparison between three chunking strategies namely:
- **Fixed chunking**: Slices text by a fixed number of characters without much consideration for semantic or separator boundaries
- **Recursive chunking**: Slices text hierarchically with a list of separators and then recursively merge with overlap with consideration for a max number of characters
- **Semantic chunking**: calculates embedding distances between consecutive sentences to split when a semnatic boundary below set threshold is given.

This is by no means a clean comparison due to a couple of implementation inefficiencies such as:
- No overlap used in semantic chunking while it was used in fixed and recursive chunking
- The chunking did not effectively account for natural breaks such as new para, subsections, sections etc.
- There were no cleaning of irrelevant details.
- Semantic chunking might benefit from experiment different percentile for similarity comparison since the `0.20` might have been too aggrresive thereby producing lower average characters per chunk relative to the other two methods.
- Lose on separator in recursive splitting which may cause breaks in boundaries.
- The max characters used in this evaluation may have favored a particular strategy over another for this particular task

Results based on `top_k = 3`, considering MRR(how high the first useful chunk ranks):
- When the `max_characters` were set to `300`, semantic strategy wins.
- When the `max_characters` were set to `500`, recursive with overlap strategy won

Overall, these comparison was done for the purpose of understanding how these different chunking strategies work in a RAG implementation. Based on the result of the limited comparison, recursive with overlap stategy is chosen to move forward and additional RAG upgrades shall be applied to it


## Contextual Retrieval Upgrade

What is contextual retrieval? Contextual retrieval is the prepending of a short LLM generated description of what each chunk is about, which is expected to improve retrieval relevance. 

contextual retrieval upgrade will be applied with the recursive with overlap strategy only. 

Based on the comparison run between:
- recursive with overlap chunking

&

- recursive with overlap chunking with prepended LLM generated context.

Small improvements were noticed with the most correct result now appearing into the first place. The top-3 results are no better overall.

However, the sources text are too small, 45 queries is limited, and the quality of context generated has to be evaluated itself for maximum gains. The contexts generated generated here are more like a summary of the chunk in of itself, hence the context generation prompt has to be properly tuned.


## Hybrid Search (Sparse + Dense) with Reranking

The current implementation is dense retrieval which aims at querying based on semantic similarity using embeddings. While sparse retrieval is keyword based, meaning it searches based on occurences of keyword similarity between queries and sources. Dense uses cosine similarity between -1 and 1 for scoring while Sparse (BM25) adds up a score for every query word that appears in the chunk. 

These two implementation are not production-optimal on their own, but combining them is great because they are able to complement each other's blindspot. A necessary step in this process is reranking as will be demonstrated in the relevant source files in `hybrid_search_and_reranking_phase` folder.

Both method (dense and sparse retrieval) are treated as distinct pipelines in this implementation because their scores are on different scales (cosine `-1` to `1` vs unbounder BM25), so rank-based fusion avoids hand-tuning score weights. 

Reciprocal Rank Fusion is used in this work to fuse the dense and sparse result lists into one ranking. The efficacy of RRF is strongly linked to the value of smoothering constant (`k`) hence thorough tuning is advised for optimal results.

In the second reranking phase, a cross-encoder reranker was employed; CrossEncoder reranker is the process where the query and the chunk is passed through a transformer model that outputs a relevance score. This is the most common setup in production when using an hybrid retrieval approach (Hybrid Retrieval + RRF + Cross-Encoder Reranking)


## Evaluation

This is the evaluation phase where all methods that have been implemented thus far are evaluated. 3 metrics are used for evaluation namely Recall@3, Recall@5 and MRR. Recall@k measures how many relevant evidence facts are found in the top k of a particular method against the actual number of relevant evidence facts for that query. So, for example if the total number of relevant evidence facts is 4, and 3 happens to be found in the top k of a method, then its recall@k would be `3/4 = 0.75`. MRR which stands for Mean Reciprocal Rank is an important complementary metric to Recall@k as it measures the position of the ranking of the relevant evidence facts found. So Recall@k cares about if they are present, while MRR cares about the position in which they are found (`1/R`) e.g if the first relevant evidence fact is found in rank 1, we get `1/1 = 1.0` (perfect), if in rank 3 we get `1/3 = 0.33`.

```
Method                Recall@3  Recall@5  MRR
Dense                 0.878     0.922     0.872
Sparse                0.933     0.967     0.894
Hybrid RRF            0.944     0.967     0.890
Hybrid RRF + rerank   0.989     0.989     0.944
```

The result came at no surprise. Sparse wins over Dense because the query and sources used in this evaluation have similar keywords, hence one might get different results if the queries were more paraphrased. We also saw that the improvement for the Hybrid retrieval over Sparse retrieval is most apparent when it was paired with the Cross-Encoder reranker.

Interestingly Hybrid RRF + rerank seems to capture its relevant evidence in its top 3 such that even when k was increased to 5, the recall remained thesame. As opposed to other methods whose recall@k improved as k was increased from 3 to 5.

It is important to mention that these results are specific to the sources, parameters, metrics used in this evaluation, and a production-optimal evaluation would require more careful sources selection, paramter tunining, and robust evaluation metrics etc. 


## GraphRAG

Baseline RAG have been known to have shortcomings in answering complex queries that requires multi-hop reasining, which is what GraphRAG aims to address. When the answer to a query requires consolidations of facts from different section of a dataset, GraphRAG is best suited for such task. What is GraphRAG. GraphRAG is the use of LLM to extract entities and relationships from a dataset, and then building knowlegde graphs with it. And then layering graph traversal and community summarization on top of retrieval.


When building a SimpleKGPipeline, it uses a default large chunk size, so one must use a text splitter to experiment with different chunk size and chunk overlap and see how it affects extracted entities and the knowledge graph. For example large chunk size may provide more context for extracted entities but provides less granular data.

Also very important is to have a properly defined schema so that the extracted entity and built knowledge graph can be more relevant and structured. Schema definition expresses the nodes, relationships and patterns that is to be extracted from the text. Experimentation and iteration is sometimes needed to arrive at the optimal schema.  I used LLM to extract the schema as depicted in `extract_schema.py`, saved it as json, and then edited it in place to fit my desired structure before passing it to the SimpleKGPipeline. schemas were extracted for each source files, and then examined with the aid of LLM to create a single combined deduplicated schema `schema.json`.

When creating knowledge graphs, there are two kinds of graph: a lexical graph, which represents the text itself (documents, chunks and how they connect), and a domain graph, which represents the real-world entities and relationships the data describes. In this implementation, I used unstructured data, and from it I built both a lexical graph and an LLM-extracted domain graph, connected through FROM_CHUNK relationships. It is important to thoroughly the created graphs as the graphRAG efficacy is tied to the extracted graph quality as much as the retrieval quality. Graphs were created for each documents and examined. Thorough examination of the graphs is mandatory as everything downstream of it is predicated on its quality. As a consequence.

I implemented an LLM judge for evaluating the triples from graphs against facts. Iteration follows accordingly to get to the optimal graph construction. A lot of iteration is done in ensuring the LLM judge is optimally sound, and that includes tweaking the prompt (e.g instructing the model to output the given fact that supports its verdict, kinda forcing it to subtly reason before deciding), also examining the extracted entities with the aid of Claude to ascertain the instruction-following of the choosen LLM model. It is generally better to use a stronger and different model-family LLM as a judge, and also some models tend to be better at instruction-following than others, so that is an important consideration. I also iterated on the entity properties given to the judge as context, so through understanding of the properties of the dataset one is working with is typically important in ensuring a sophisticated graph quality judgement. After these changes, the measurement improved with issue of leniency on multi-clause facts still persisting

Ablation is important: after every change, the graph coverage is re-ran as to measure how each changes improves or worsen the judges performance on the graph quality to ascertain what changes are actually helpful in my specific setup.


Based on the graph coverage result, a lot of iteration was done for the graph extraction prompt. graph_coverage.py collects the graph triples and entity properties extracted from that question's evidence documents. And based on the result from that, the 40/110 was the best that was acheieved based on few iterations conducted. This meant for 40 facts, the graph contained  everything needed, and for the other 70 somethinh was missing or wrong. Obviosly this is not an ideal result, hence in real production pipelines, more iteration is necessary.


### GraphRAG Retriever and Answering

Retriver was created based on index from chunk_embeddings from the graph, and then based on the top_k=3 the chunk text and graph facts were passed to the llm as context to generate an answer for each query. I observed that the combination of the graph facts and the chunk text really helped the LLM in answering the questions right especially for the multi-hop type of questions which are the kind graphRAG are most suitabled for as ascertained earlier. Most investigation and iteration will be carried out to determine potential rooms for improvements. 