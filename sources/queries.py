# evidence: one item per fact the answer needs. A nested list holds alternative
# quotes for the same fact (stated in more than one document); any one counts.
# A chunk is relevant if it contains a quote (case and whitespace insensitive).
queries = [
    {
        "id": "Q01",
        "type": "multi_fact",
        "query": "How does GuideFlow decide whether a knowledge article can be used in a customer-facing answer?",
        "ground_truth": ["01_product_and_rag.txt", "04_knowledge_search.txt"],
        "key_evidence": "Approved publication state; metadata eligibility filters before final ranking.",
        "evidence": [["Approved articles may be used for customer-facing answer generation", "In Approved, it can be used for customer-facing answer generation"], ["eligibility is checked before final selection", "applies metadata filters before final ranking"]]
    },
    {
        "id": "Q02",
        "type": "definition",
        "query": "What is the difference between a conversation, a ticket, and an incident in AtlasDesk?",
        "ground_truth": ["01_product_and_rag.txt"],
        "key_evidence": "Definitions of conversation, ticket, incident.",
        "evidence": ["A conversation is the exchange between a customer and the support organization", "A ticket is a tracked work item", "An incident is an operational event"]
    },
    {
        "id": "Q03",
        "type": "narrow_factual",
        "query": "What happens when the third payment attempt fails?",
        "ground_truth": ["02_billing_and_workflows.txt"],
        "key_evidence": "Restricted billing state; existing tickets readable; automation paused.",
        "evidence": ["If the third attempt fails, the workspace enters a restricted billing state", "new automation jobs are paused until the balance is resolved"]
    },
    {
        "id": "Q04",
        "type": "explanation",
        "query": "Why does deactivating a seat not necessarily remove it from the current billing calculation?",
        "ground_truth": ["02_billing_and_workflows.txt", "08_faq_and_glossary.txt"],
        "key_evidence": "Daily billing snapshot; deactivation does not retroactively change a recorded snapshot.",
        "evidence": [["it does not retroactively remove the seat from a snapshot that has already been recorded", "the seat is billed for that day even if it was deactivated afterwards"]]
    },
    {
        "id": "Q05",
        "type": "workflow",
        "query": "What should an agent do when a customer disputes an invoice line item?",
        "ground_truth": ["02_billing_and_workflows.txt", "05_support_and_access.txt"],
        "key_evidence": "Record invoice number; compare line item with billing record; explain or request adjustment.",
        "evidence": [["The agent records the invoice number and billing period", "recording the invoice number and billing period"], "compares the disputed line item with the corresponding billing record"]
    },
    {
        "id": "Q06",
        "type": "distinction",
        "query": "What is the difference between an incident status update and a root-cause statement?",
        "ground_truth": ["03_security_and_retention.txt"],
        "key_evidence": "Early update states known/unknown and avoids speculation; root cause comes after evidence.",
        "evidence": ["It should not speculate about the root cause", "A status update and a root-cause statement are therefore different things"]
    },
    {
        "id": "Q07",
        "type": "cross_document",
        "query": "How long are audit logs retained, and does changing conversation retention change that period?",
        "ground_truth": ["03_security_and_retention.txt", "07_release_notes.txt"],
        "key_evidence": "Audit logs retained 180 days; conversation retention is separate.",
        "evidence": ["The standard audit-log retention period is 180 days", "Changing conversation retention does not change the 180-day audit-log period"]
    },
    {
        "id": "Q08",
        "type": "exception",
        "query": "What happens to a conversation that is past its retention period but is covered by a legal hold?",
        "ground_truth": ["03_security_and_retention.txt"],
        "key_evidence": "Legal hold suspends deletion until release.",
        "evidence": ["it remains protected from deletion until the hold is released"]
    },
    {
        "id": "Q09",
        "type": "conceptual",
        "query": "Why can a higher semantic similarity score still lead to a worse retrieval result?",
        "ground_truth": ["01_product_and_rag.txt", "04_knowledge_search.txt", "06_chunking_benchmark.txt"],
        "key_evidence": "Eligibility filters can exclude a high-scoring passage; similarity is not a direct quality score.",
        "evidence": [["can have a very high semantic similarity score and still be excluded", "Semantic similarity alone therefore does not guarantee that a passage is eligible"], ["similarity scores should not be treated as direct quality scores", "A lower-scoring chunk can contain the complete answer"]]
    },
    {
        "id": "Q10",
        "type": "comparison",
        "query": "How does recursive chunking differ from fixed-size chunking?",
        "ground_truth": ["06_chunking_benchmark.txt"],
        "key_evidence": "Recursive tries structural separators first; fixed cuts by approximate character length.",
        "evidence": ["Recursive chunking tries larger structural boundaries before smaller ones", "Fixed-size chunking divides text into blocks of approximately the same character length"]
    },
    {
        "id": "Q11",
        "type": "mechanism",
        "query": "How does semantic chunking identify a possible topic boundary?",
        "ground_truth": ["06_chunking_benchmark.txt"],
        "key_evidence": "Sentence embeddings; adjacent cosine similarity; large similarity drop.",
        "evidence": ["Adjacent sentence embeddings are compared with cosine similarity", "A large drop in similarity can indicate a topic boundary"]
    },
    {
        "id": "Q12",
        "type": "evaluation",
        "query": "Why should retrieval evaluation use Recall@K or reciprocal rank instead of only comparing similarity scores?",
        "ground_truth": ["06_chunking_benchmark.txt"],
        "key_evidence": "Recall@K and MRR measure whether relevant evidence is retrieved; similarity only measures vector closeness.",
        "evidence": ["Recall@K measures whether relevant evidence appears anywhere in the first K retrieved results", "more informative for comparing retrieval systems than simply averaging similarity scores"]
    },
    {
        "id": "Q13",
        "type": "context",
        "query": "A customer cannot access an account and also disputes a charge. Should the agent use one workflow or two?",
        "ground_truth": ["05_support_and_access.txt", "02_billing_and_workflows.txt"],
        "key_evidence": "One ticket can contain both issues, but access and billing follow separate workflows.",
        "evidence": [["should not assume that one workflow solves both problems", "should not assume that one workflow resolves both"], ["One ticket may contain both issues", "One ticket can contain both issues"]]
    },
    {
        "id": "Q14",
        "type": "workflow_exception",
        "query": "What must happen before an agent promises a customer that a refund or billing adjustment will be made?",
        "ground_truth": ["02_billing_and_workflows.txt"],
        "key_evidence": "Required approval must occur first.",
        "evidence": ["the approval must happen before an agent promises that the requested change will be made"]
    },
    {
        "id": "Q15",
        "type": "narrow_factual",
        "query": "Does moving a user from one team to another automatically remove direct access-group assignments?",
        "ground_truth": ["05_support_and_access.txt"],
        "key_evidence": "Team membership changes, but direct assignments remain.",
        "evidence": ["does not automatically remove direct access-group assignments"]
    },
    {
        "id": "Q16",
        "type": "explanation",
        "query": "Why might two supervisors have different permissions even though they have the same role?",
        "ground_truth": ["05_support_and_access.txt", "01_product_and_rag.txt"],
        "key_evidence": "Effective permissions depend on access groups, not role name alone; custom roles copied at different times diverge.",
        "evidence": ["access is based on effective permissions rather than job title alone", "later changes to the original default role are not propagated to the copy"]
    },
    {
        "id": "Q17",
        "type": "definition",
        "query": "What is the difference between a seat and an automation credit?",
        "ground_truth": ["02_billing_and_workflows.txt", "08_faq_and_glossary.txt"],
        "key_evidence": "Seat is a licensed user; automation credit is usage of selected background jobs.",
        "evidence": [["A seat represents a licensed support user", "Seat: A licensed support user"], ["Automation credits represent usage of selected background jobs", "A unit of background-job usage"]]
    },
    {
        "id": "Q18",
        "type": "reasoning",
        "query": "Why should an employee preserve records instead of deleting suspicious records during a security investigation?",
        "ground_truth": ["03_security_and_retention.txt"],
        "key_evidence": "Deleting evidence makes timeline reconstruction harder.",
        "evidence": ["Removing evidence can make timeline reconstruction more difficult"]
    },
    {
        "id": "Q19",
        "type": "state_transition",
        "query": "What happens when a knowledge article is factually approved but has not yet received supervisor approval?",
        "ground_truth": ["04_knowledge_search.txt"],
        "key_evidence": "It remains in Review and is not published.",
        "evidence": ["It remains in Review until the supervisor approves it"]
    },
    {
        "id": "Q20",
        "type": "benchmark_design",
        "query": "What variables should remain controlled when comparing fixed, recursive, and semantic chunking strategies?",
        "ground_truth": ["06_chunking_benchmark.txt"],
        "key_evidence": "Embedding model, retrieval metric, query set, max chunk size, top-K constant; chunking is the only variable.",
        "evidence": ["keep the embedding model, retrieval metric, query set, maximum chunk size, and top-K constant"]
    },
    {
        "id": "Q21",
        "type": "boundary",
        "query": "Can agents still reply to customers while a workspace is in the restricted billing state, and are automated answers sent?",
        "ground_truth": ["02_billing_and_workflows.txt"],
        "key_evidence": "Agents can still reply; GuideFlow limited to agent-facing drafts.",
        "evidence": ["agents can still reply to existing conversations", "GuideFlow answer generation is limited to agent-facing drafts"]
    },
    {
        "id": "Q22",
        "type": "boundary",
        "query": "After a restricted workspace pays its balance, do the paused automation jobs run again automatically?",
        "ground_truth": ["02_billing_and_workflows.txt"],
        "key_evidence": "Restriction removed within 15 minutes; paused jobs are not replayed automatically.",
        "evidence": ["Paying the outstanding balance removes the restriction within 15 minutes", "Automation jobs that were paused are not replayed automatically"]
    },
    {
        "id": "Q23",
        "type": "exception",
        "query": "Does an Enterprise workspace on invoice billing go through the three-stage failed payment recovery?",
        "ground_truth": ["02_billing_and_workflows.txt"],
        "key_evidence": "Card recovery does not apply; never restricted automatically.",
        "evidence": ["the three-stage card recovery process does not apply", "never placed in the restricted billing state automatically"]
    },
    {
        "id": "Q24",
        "type": "exception",
        "query": "Does an erasure request from an end user override a legal hold?",
        "ground_truth": ["03_security_and_retention.txt"],
        "key_evidence": "Erasure overrides retention but not a legal hold; completed after release.",
        "evidence": ["but they do not override a legal hold", "the erasure is completed after the hold is released"]
    },
    {
        "id": "Q25",
        "type": "exception",
        "query": "Can the account-access workflow recover an account that uses single sign-on?",
        "ground_truth": ["05_support_and_access.txt"],
        "key_evidence": "SSO accounts cannot be recovered; customer contacts their identity provider administrator.",
        "evidence": ["Accounts that use single sign-on cannot be recovered through the account-access workflow"]
    },
    {
        "id": "Q26",
        "type": "exception",
        "query": "Does a legal hold on the parent workspace protect data in its sandbox workspace?",
        "ground_truth": ["09_integrations_and_api.txt"],
        "key_evidence": "Sandbox deleted after 60 days inactivity; parent legal hold does not extend.",
        "evidence": ["a legal hold on the parent does not extend to the sandbox"]
    },
    {
        "id": "Q27",
        "type": "distractor",
        "query": "How many times is a failed webhook delivery retried, and is the webhook disabled afterwards?",
        "ground_truth": ["09_integrations_and_api.txt"],
        "key_evidence": "Five retries with backoff; moved to dead-letter list; not disabled automatically.",
        "evidence": ["Failed deliveries are retried up to five times with exponential backoff", "the webhook is not disabled automatically"]
    },
    {
        "id": "Q28",
        "type": "distractor",
        "query": "Is putting a ticket On Hold the same as placing it under a legal hold?",
        "ground_truth": ["05_support_and_access.txt", "08_faq_and_glossary.txt"],
        "key_evidence": "Ticket hold is unrelated to legal hold; it pauses the resolution timer but does not protect from deletion.",
        "evidence": ["A ticket on hold is unrelated to a legal hold", "does not protect the conversation from deletion"]
    },
    {
        "id": "Q29",
        "type": "distractor",
        "query": "What is the difference between an account credit and an automation credit?",
        "ground_truth": ["02_billing_and_workflows.txt", "08_faq_and_glossary.txt"],
        "key_evidence": "Account credit is monetary and reduces a future invoice; automation credits have no monetary value.",
        "evidence": [["An account credit is a monetary amount", "Credit (account): A monetary amount"], "automation credits have no monetary value"]
    },
    {
        "id": "Q30",
        "type": "distractor",
        "query": "Is the knowledge index snapshot related to the daily billing snapshot?",
        "ground_truth": ["04_knowledge_search.txt", "08_faq_and_glossary.txt"],
        "key_evidence": "They are unrelated.",
        "evidence": ["An index snapshot is unrelated to the daily billing snapshot"]
    },
    {
        "id": "Q31",
        "type": "distractor",
        "query": "What is the difference between a service review and a post-incident review?",
        "ground_truth": ["10_sla_and_escalation.txt"],
        "key_evidence": "Service review is about support performance; post-incident review is about a platform incident.",
        "evidence": ["a service review is about support performance, while a post-incident review is about a platform incident"]
    },
    {
        "id": "Q32",
        "type": "temporal",
        "query": "What is the default GuideFlow minimum relevance threshold, and what was it before?",
        "ground_truth": ["01_product_and_rag.txt", "07_release_notes.txt"],
        "key_evidence": "0.55 now; raised from 0.50.",
        "evidence": ["The default minimum relevance threshold is 0.55", "minimum relevance threshold was raised from 0.50 to 0.55"]
    },
    {
        "id": "Q33",
        "type": "temporal",
        "query": "Are stale knowledge articles excluded from customer-facing retrieval?",
        "ground_truth": ["04_knowledge_search.txt", "07_release_notes.txt"],
        "key_evidence": "No; stale passages get a 0.05 ranking penalty but are not excluded (older 3.6 behavior was replaced).",
        "evidence": [["never excludes them because of staleness alone", "receive a ranking penalty of 0.05 instead of being excluded"]]
    },
    {
        "id": "Q34",
        "type": "temporal",
        "query": "When audit-log retention was increased, were previously deleted audit records restored?",
        "ground_truth": ["07_release_notes.txt"],
        "key_evidence": "Increased from 90 to 180 days; already-deleted records were not restored.",
        "evidence": ["Audit-log retention was increased from 90 days to 180 days", "had already been deleted under the old 90-day rule were not restored"]
    },
    {
        "id": "Q35",
        "type": "narrow_factual",
        "query": "What is the first-response target for an Urgent ticket on the Growth plan?",
        "ground_truth": ["10_sla_and_escalation.txt"],
        "key_evidence": "2 hours on Growth.",
        "evidence": ["Urgent: 1 hour on Enterprise, 2 hours on Growth"]
    },
    {
        "id": "Q36",
        "type": "narrow_factual",
        "query": "How many automation credits does it cost to manually reindex a single knowledge article?",
        "ground_truth": ["04_knowledge_search.txt"],
        "key_evidence": "5 automation credits.",
        "evidence": ["A manual reindex of a single article costs 5 automation credits"]
    },
    {
        "id": "Q37",
        "type": "narrow_factual",
        "query": "Who needs to approve a 500 dollar billing adjustment?",
        "ground_truth": ["02_billing_and_workflows.txt"],
        "key_evidence": "Above 200 and up to 2,000 dollars needs a billing specialist.",
        "evidence": ["Adjustments above 200 dollars and up to 2,000 dollars need a billing specialist"]
    },
    {
        "id": "Q38",
        "type": "narrow_factual",
        "query": "Does deactivating the administrator who created an API key revoke that key?",
        "ground_truth": ["09_integrations_and_api.txt"],
        "key_evidence": "No; keys belong to the workspace.",
        "evidence": ["deactivating that administrator's seat does not revoke the key"]
    },
    {
        "id": "Q39",
        "type": "list_item",
        "query": "What should an agent do if an account is locked after too many failed sign-ins?",
        "ground_truth": ["05_support_and_access.txt"],
        "key_evidence": "Wait for the automatic 30-minute lock or unlock with supervisor approval.",
        "evidence": ["wait for the automatic 30-minute lock to expire or unlock it manually with supervisor approval"]
    },
    {
        "id": "Q40",
        "type": "list_item",
        "query": "How quickly must the first public update be posted for a Severity One incident, and how often after that?",
        "ground_truth": ["03_security_and_retention.txt"],
        "key_evidence": "Within 30 minutes, then every 60 minutes.",
        "evidence": ["first public update within 30 minutes of declaration, then every 60 minutes"]
    },
    {
        "id": "Q41",
        "type": "table",
        "query": "Can a supervisor change retention settings?",
        "ground_truth": ["05_support_and_access.txt"],
        "key_evidence": "No; only administrators.",
        "evidence": [["Change retention settings | no | no | yes", "it does not automatically permit retention or billing configuration"]]
    },
    {
        "id": "Q42",
        "type": "reasoning",
        "query": "Why can raising a ticket's priority to Urgent immediately put it in breach?",
        "ground_truth": ["10_sla_and_escalation.txt"],
        "key_evidence": "Target recalculated from ticket creation time, not the time of the change.",
        "evidence": ["recalculated from the ticket creation time, not from the time of the change"]
    },
    {
        "id": "Q43",
        "type": "reasoning",
        "query": "Why is an article that was approved this morning not yet showing up in GuideFlow answers?",
        "ground_truth": ["04_knowledge_search.txt"],
        "key_evidence": "Not retrievable until the next nightly indexing run unless manually reindexed.",
        "evidence": ["not retrievable by GuideFlow until the next indexing run completes"]
    },
    {
        "id": "Q44",
        "type": "multi_fact",
        "query": "Does an automated GuideFlow answer count as a first response for SLA purposes?",
        "ground_truth": ["10_sla_and_escalation.txt", "05_support_and_access.txt"],
        "key_evidence": "No; first-response time measures human responses only.",
        "evidence": [["An automated GuideFlow answer does not count as a first response", "an automated answer does not stop the first-response timer"]]
    },
    {
        "id": "Q45",
        "type": "reasoning",
        "query": "Why can recursive chunking behave like fixed-size chunking on hard-wrapped text?",
        "ground_truth": ["06_chunking_benchmark.txt"],
        "key_evidence": "Line breaks tried before sentence boundaries split at arbitrary line positions.",
        "evidence": ["will then split at arbitrary line positions, which behaves much like fixed-size chunking"]
    }
]
