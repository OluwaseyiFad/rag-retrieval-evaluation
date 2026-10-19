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