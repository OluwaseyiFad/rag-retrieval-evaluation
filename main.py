import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from semantic_chunking import semantic_chunk_text
from fixed_chunking import fixed_size_chunk_text
from recursive_chunking import recursive_chunk_text
from pathlib import Path
from process_pdf import extract_pdf


source_folder = Path("sources")

all_documents = []

for txt_path in source_folder.glob("*.txt"):
    text = txt_path.read_text(encoding="utf-8")
    all_documents.append({
            "text": text,
            "source": txt_path.name
    })

model = SentenceTransformer("all-MiniLM-L6-V2")


def create_index(chunks, model):
    texts = [ chunk["text"] for chunk in chunks]
    embeddings = model.encode(texts, normalize_embeddings=True, convert_to_numpy=True)
    embeddings = embeddings.astype("float32")
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension) # initialize with vector dimension
    index.add(embeddings)
    return index



# For fixed, recursive, and semantic chunking
def generate_chunks(chunk_func):
    all_chunks = []
    for document in all_documents:
        chunks = chunk_func(
            document["text"]
        )
        for chunk_number, chunk in enumerate(chunks):
            all_chunks.append({
                "text": chunk,
                "source": document["source"],
                "chunk": chunk_number
            })
    return all_chunks


# Retrieval
def retrieve(query, index, chunks, model, top_k=3):
    query_embedding = model.encode([query], normalize_embeddings=True, convert_to_numpy=True)
    query_embedding = query_embedding.astype("float32")
    scores, indices = index.search(query_embedding, top_k)
    results = []
    for score, idx in zip(scores[0], indices[0]):
        chunk = chunks[idx]
        results.append({
            "score": float(score),
            "text": chunk["text"],
            "source": chunk["source"],
            "chunk": chunk["chunk"]
        })
        
    return results


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
        print(f"Text:\n{result['text'][:1000]}")

        
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
        f.write(f"\nText:\n{result['text'][:1000]}")


fixed_chunks = generate_chunks(fixed_size_chunk_text)
recursive_chunks = generate_chunks(recursive_chunk_text)
semantic_chunks = generate_chunks(semantic_chunk_text)

fixed_index = create_index(fixed_chunks, model)
recursive_index = create_index(recursive_chunks, model)
semantic_index = create_index(semantic_chunks, model)

queries = [
    {
        "id": "Q01",
        "type": "multi_fact",
        "query": "How does GuideFlow decide whether a knowledge article can be used in a customer-facing answer?",
        "ground_truth": ["01_product_and_rag.txt", "04_knowledge_search.txt"],
        "key_evidence": "Approved publication state; metadata eligibility filters before final ranking."
    },
    {
        "id": "Q02",
        "type": "definition",
        "query": "What is the difference between a conversation, a ticket, and an incident in AtlasDesk?",
        "ground_truth": ["01_product_and_rag.txt"],
        "key_evidence": "Definitions of conversation, ticket, incident."
    },
    {
        "id": "Q03",
        "type": "narrow_factual",
        "query": "What happens when the third payment attempt fails?",
        "ground_truth": ["02_billing_and_workflows.txt"],
        "key_evidence": "Restricted billing state; existing tickets readable; automation paused."
    },
    {
        "id": "Q04",
        "type": "explanation",
        "query": "Why does deactivating a seat not necessarily remove it from the current billing calculation?",
        "ground_truth": ["02_billing_and_workflows.txt", "08_faq_and_glossary.txt"],
        "key_evidence": "Daily billing snapshot; deactivation does not retroactively change a recorded snapshot."
    },
    {
        "id": "Q05",
        "type": "workflow",
        "query": "What should an agent do when a customer disputes an invoice line item?",
        "ground_truth": ["02_billing_and_workflows.txt", "05_support_and_access.txt"],
        "key_evidence": "Record invoice number; compare line item with billing record; explain or request adjustment."
    },
    {
        "id": "Q06",
        "type": "distinction",
        "query": "What is the difference between an incident status update and a root-cause statement?",
        "ground_truth": ["03_security_and_retention.txt"],
        "key_evidence": "Early update states known/unknown and avoids speculation; root cause comes after evidence."
    },
    {
        "id": "Q07",
        "type": "cross_document",
        "query": "How long are audit logs retained, and does changing conversation retention change that period?",
        "ground_truth": ["03_security_and_retention.txt", "07_release_notes.txt"],
        "key_evidence": "Audit logs retained 180 days; conversation retention is separate."
    },
    {
        "id": "Q08",
        "type": "exception",
        "query": "What happens to a conversation that is past its retention period but is covered by a legal hold?",
        "ground_truth": ["03_security_and_retention.txt"],
        "key_evidence": "Legal hold suspends deletion until release."
    },
    {
        "id": "Q09",
        "type": "conceptual",
        "query": "Why can a higher semantic similarity score still lead to a worse retrieval result?",
        "ground_truth": ["01_product_and_rag.txt", "04_knowledge_search.txt", "06_chunking_benchmark.txt"],
        "key_evidence": "Eligibility filters can exclude a high-scoring passage; similarity is not a direct quality score."
    },
    {
        "id": "Q10",
        "type": "comparison",
        "query": "How does recursive chunking differ from fixed-size chunking?",
        "ground_truth": ["06_chunking_benchmark.txt"],
        "key_evidence": "Recursive tries structural separators first; fixed cuts by approximate character length."
    },
    {
        "id": "Q11",
        "type": "mechanism",
        "query": "How does semantic chunking identify a possible topic boundary?",
        "ground_truth": ["06_chunking_benchmark.txt"],
        "key_evidence": "Sentence embeddings; adjacent cosine similarity; large similarity drop."
    },
    {
        "id": "Q12",
        "type": "evaluation",
        "query": "Why should retrieval evaluation use Recall@K or reciprocal rank instead of only comparing similarity scores?",
        "ground_truth": ["06_chunking_benchmark.txt"],
        "key_evidence": "Recall@K and MRR measure whether relevant evidence is retrieved; similarity only measures vector closeness."
    },
    {
        "id": "Q13",
        "type": "context",
        "query": "A customer cannot access an account and also disputes a charge. Should the agent use one workflow or two?",
        "ground_truth": ["05_support_and_access.txt", "02_billing_and_workflows.txt"],
        "key_evidence": "One ticket can contain both issues, but access and billing follow separate workflows."
    },
    {
        "id": "Q14",
        "type": "workflow_exception",
        "query": "What must happen before an agent promises a customer that a refund or billing adjustment will be made?",
        "ground_truth": ["02_billing_and_workflows.txt"],
        "key_evidence": "Required approval must occur first."
    },
    {
        "id": "Q15",
        "type": "narrow_factual",
        "query": "Does moving a user from one team to another automatically remove direct access-group assignments?",
        "ground_truth": ["05_support_and_access.txt"],
        "key_evidence": "Team membership changes, but direct assignments remain."
    },
    {
        "id": "Q16",
        "type": "explanation",
        "query": "Why might two supervisors have different permissions even though they have the same role?",
        "ground_truth": ["05_support_and_access.txt", "01_product_and_rag.txt"],
        "key_evidence": "Effective permissions depend on access groups, not role name alone; custom roles copied at different times diverge."
    },
    {
        "id": "Q17",
        "type": "definition",
        "query": "What is the difference between a seat and an automation credit?",
        "ground_truth": ["02_billing_and_workflows.txt", "08_faq_and_glossary.txt"],
        "key_evidence": "Seat is a licensed user; automation credit is usage of selected background jobs."
    },
    {
        "id": "Q18",
        "type": "reasoning",
        "query": "Why should an employee preserve records instead of deleting suspicious records during a security investigation?",
        "ground_truth": ["03_security_and_retention.txt"],
        "key_evidence": "Deleting evidence makes timeline reconstruction harder."
    },
    {
        "id": "Q19",
        "type": "state_transition",
        "query": "What happens when a knowledge article is factually approved but has not yet received supervisor approval?",
        "ground_truth": ["04_knowledge_search.txt"],
        "key_evidence": "It remains in Review and is not published."
    },
    {
        "id": "Q20",
        "type": "benchmark_design",
        "query": "What variables should remain controlled when comparing fixed, recursive, and semantic chunking strategies?",
        "ground_truth": ["06_chunking_benchmark.txt"],
        "key_evidence": "Embedding model, retrieval metric, query set, max chunk size, top-K constant; chunking is the only variable."
    },
    {
        "id": "Q21",
        "type": "boundary",
        "query": "Can agents still reply to customers while a workspace is in the restricted billing state, and are automated answers sent?",
        "ground_truth": ["02_billing_and_workflows.txt"],
        "key_evidence": "Agents can still reply; GuideFlow limited to agent-facing drafts."
    },
    {
        "id": "Q22",
        "type": "boundary",
        "query": "After a restricted workspace pays its balance, do the paused automation jobs run again automatically?",
        "ground_truth": ["02_billing_and_workflows.txt"],
        "key_evidence": "Restriction removed within 15 minutes; paused jobs are not replayed automatically."
    },
    {
        "id": "Q23",
        "type": "exception",
        "query": "Does an Enterprise workspace on invoice billing go through the three-stage failed payment recovery?",
        "ground_truth": ["02_billing_and_workflows.txt"],
        "key_evidence": "Card recovery does not apply; never restricted automatically."
    },
    {
        "id": "Q24",
        "type": "exception",
        "query": "Does an erasure request from an end user override a legal hold?",
        "ground_truth": ["03_security_and_retention.txt"],
        "key_evidence": "Erasure overrides retention but not a legal hold; completed after release."
    },
    {
        "id": "Q25",
        "type": "exception",
        "query": "Can the account-access workflow recover an account that uses single sign-on?",
        "ground_truth": ["05_support_and_access.txt"],
        "key_evidence": "SSO accounts cannot be recovered; customer contacts their identity provider administrator."
    },
    {
        "id": "Q26",
        "type": "exception",
        "query": "Does a legal hold on the parent workspace protect data in its sandbox workspace?",
        "ground_truth": ["09_integrations_and_api.txt"],
        "key_evidence": "Sandbox deleted after 60 days inactivity; parent legal hold does not extend."
    },
    {
        "id": "Q27",
        "type": "distractor",
        "query": "How many times is a failed webhook delivery retried, and is the webhook disabled afterwards?",
        "ground_truth": ["09_integrations_and_api.txt"],
        "key_evidence": "Five retries with backoff; moved to dead-letter list; not disabled automatically."
    },
    {
        "id": "Q28",
        "type": "distractor",
        "query": "Is putting a ticket On Hold the same as placing it under a legal hold?",
        "ground_truth": ["05_support_and_access.txt", "08_faq_and_glossary.txt"],
        "key_evidence": "Ticket hold is unrelated to legal hold; it pauses the resolution timer but does not protect from deletion."
    },
    {
        "id": "Q29",
        "type": "distractor",
        "query": "What is the difference between an account credit and an automation credit?",
        "ground_truth": ["02_billing_and_workflows.txt", "08_faq_and_glossary.txt"],
        "key_evidence": "Account credit is monetary and reduces a future invoice; automation credits have no monetary value."
    },
    {
        "id": "Q30",
        "type": "distractor",
        "query": "Is the knowledge index snapshot related to the daily billing snapshot?",
        "ground_truth": ["04_knowledge_search.txt", "08_faq_and_glossary.txt"],
        "key_evidence": "They are unrelated."
    },
    {
        "id": "Q31",
        "type": "distractor",
        "query": "What is the difference between a service review and a post-incident review?",
        "ground_truth": ["10_sla_and_escalation.txt"],
        "key_evidence": "Service review is about support performance; post-incident review is about a platform incident."
    },
    {
        "id": "Q32",
        "type": "temporal",
        "query": "What is the default GuideFlow minimum relevance threshold, and what was it before?",
        "ground_truth": ["01_product_and_rag.txt", "07_release_notes.txt"],
        "key_evidence": "0.55 now; raised from 0.50."
    },
    {
        "id": "Q33",
        "type": "temporal",
        "query": "Are stale knowledge articles excluded from customer-facing retrieval?",
        "ground_truth": ["04_knowledge_search.txt", "07_release_notes.txt"],
        "key_evidence": "No; stale passages get a 0.05 ranking penalty but are not excluded (older 3.6 behavior was replaced)."
    },
    {
        "id": "Q34",
        "type": "temporal",
        "query": "When audit-log retention was increased, were previously deleted audit records restored?",
        "ground_truth": ["07_release_notes.txt"],
        "key_evidence": "Increased from 90 to 180 days; already-deleted records were not restored."
    },
    {
        "id": "Q35",
        "type": "narrow_factual",
        "query": "What is the first-response target for an Urgent ticket on the Growth plan?",
        "ground_truth": ["10_sla_and_escalation.txt"],
        "key_evidence": "2 hours on Growth."
    },
    {
        "id": "Q36",
        "type": "narrow_factual",
        "query": "How many automation credits does it cost to manually reindex a single knowledge article?",
        "ground_truth": ["04_knowledge_search.txt"],
        "key_evidence": "5 automation credits."
    },
    {
        "id": "Q37",
        "type": "narrow_factual",
        "query": "Who needs to approve a 500 dollar billing adjustment?",
        "ground_truth": ["02_billing_and_workflows.txt"],
        "key_evidence": "Above 200 and up to 2,000 dollars needs a billing specialist."
    },
    {
        "id": "Q38",
        "type": "narrow_factual",
        "query": "Does deactivating the administrator who created an API key revoke that key?",
        "ground_truth": ["09_integrations_and_api.txt"],
        "key_evidence": "No; keys belong to the workspace."
    },
    {
        "id": "Q39",
        "type": "list_item",
        "query": "What should an agent do if an account is locked after too many failed sign-ins?",
        "ground_truth": ["05_support_and_access.txt"],
        "key_evidence": "Wait for the automatic 30-minute lock or unlock with supervisor approval."
    },
    {
        "id": "Q40",
        "type": "list_item",
        "query": "How quickly must the first public update be posted for a Severity One incident, and how often after that?",
        "ground_truth": ["03_security_and_retention.txt"],
        "key_evidence": "Within 30 minutes, then every 60 minutes."
    },
    {
        "id": "Q41",
        "type": "table",
        "query": "Can a supervisor change retention settings?",
        "ground_truth": ["05_support_and_access.txt"],
        "key_evidence": "No; only administrators."
    },
    {
        "id": "Q42",
        "type": "reasoning",
        "query": "Why can raising a ticket's priority to Urgent immediately put it in breach?",
        "ground_truth": ["10_sla_and_escalation.txt"],
        "key_evidence": "Target recalculated from ticket creation time, not the time of the change."
    },
    {
        "id": "Q43",
        "type": "reasoning",
        "query": "Why is an article that was approved this morning not yet showing up in GuideFlow answers?",
        "ground_truth": ["04_knowledge_search.txt"],
        "key_evidence": "Not retrievable until the next nightly indexing run unless manually reindexed."
    },
    {
        "id": "Q44",
        "type": "multi_fact",
        "query": "Does an automated GuideFlow answer count as a first response for SLA purposes?",
        "ground_truth": ["10_sla_and_escalation.txt", "05_support_and_access.txt"],
        "key_evidence": "No; first-response time measures human responses only."
    },
    {
        "id": "Q45",
        "type": "reasoning",
        "query": "Why can recursive chunking behave like fixed-size chunking on hard-wrapped text?",
        "ground_truth": ["06_chunking_benchmark.txt"],
        "key_evidence": "Line breaks tried before sentence boundaries split at arbitrary line positions."
    }
]


# Examinining the chunks for each strategies
# Ensure suitability for comparison
# print("Fixed chunks: ", len(fixed_chunks))
# print("Recursive chunks: ", len(recursive_chunks))
# print("Semantic chunks: ", len(semantic_chunks))

# def average_chunk_size(chunks):
#     return sum(len(c["text"]) for c in chunks) / len(chunks)

# print("Fixed avg:", average_chunk_size(fixed_chunks))
# print("Recursive avg:", average_chunk_size(recursive_chunks))
# print("Semantic avg:", average_chunk_size(semantic_chunks))


with open("result.txt", "w", encoding="utf-8") as f:
    for query in queries:
        fixed_results = retrieve(query["query"], fixed_index, fixed_chunks, model, top_k=3)
        recursive_results = retrieve(query["query"], recursive_index, recursive_chunks, model, top_k=3)
        semantic_results = retrieve(query["query"], semantic_index, semantic_chunks, model, top_k=3)
        f.write(f"\nquery: {query["query"]}")
        write_results("Fixed", fixed_results, f)
        write_results("Recursive", recursive_results, f)
        write_results("Semantic", semantic_results, f)
        f.write("\n\n\n\n")