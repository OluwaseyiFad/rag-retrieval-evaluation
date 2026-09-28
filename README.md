
## Comparison between three chunking strategies namely:
- Fixed chunking: Slices text by a fixed number of characters without much consideration for semantic or separator boundaries
- Recursive chunking: Slices text hierarchically with a list of separators and then recursively merge with overlap with consideration for a max number of characters
- Semantic chunking: calculates embedding distances between consecutive sentences to split when a semnatic boundary below set threshold is given.

This is by no means a clean comparison due to a couple of implementation inefficiencies such as:
- No overlap used in semantic chunking while it was used in fixed and recursive chunking
- The chunking did not effectively account for natural breaks such as new para, subsections, sections etc.
- There were no cleaning of irrelevant details.
- Semantic chunking might benefit from experiment different percentile for similarity comparison since the 0.20 might have been too aggrresive thereby producing lower average characters per chunk relative to the other two methods.
- Lose on separator in recursive splitting which may cause breaks in boundaries.
- The max characters used in this evaluation may have favored a particular strategy over another for this particular task

Results based on top_k = 3, considering MRR(how high the first useful chunk ranks):
- When the max_characters were set to 300, semantic strategy wins.
- When the max_characters were set to 500, recursive with overlap strategy won

Overall, these comparison was done for the purpose of understanding how these different chunking strategies work in a RAG implementation. Based on the result of the limited comparison, recursive with overlap stategy is chosen to move forward and additional RAG upgrades shall be applied to it


## Contextual Retrieval Upgrade

What is contextual retrieval? Contextual retrieval is the prepending of a short LLM generated description of what each chunk is about, which is expected to improve retrieval relevance. 

contextual retrieval upgrade will be applied with the recursive with overlap strategy only. 