Comparison between three chunking strategies namely:
- Fixed chunking
- Recursive chunking
- Semantic chunking

This is by no means a clean comparison due to a couple of implementation inefficiencies such as:
- No overlap used in semantic chunking while it was used in fixed and recursive chunking
- The chunking did not effectively account for natural breaks such as new para, subsections, sections etc.
- There were no cleaning of irrelevant details, especially given that the sources were papers that tend to contain details such as citations, numbers, figures etc that might conflate the embeddings.
- Semantic chunking might benefit from experiment different percentile for similarity comparison since the 0.20 might have been too aggrresive thereby producing lower average characters per chunk relative to the other two methods.


Overall, these comparison was done for the purpose of understanding how these different chunking strategies work in a RAG implementation
