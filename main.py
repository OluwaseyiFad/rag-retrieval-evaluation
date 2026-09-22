from sentence_transformers import SentenceTransformer
from transformers import pipeline
import numpy as np
import faiss



embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
doc_embeddings = embedding_model.encode(documents)
doc_embeddings = np