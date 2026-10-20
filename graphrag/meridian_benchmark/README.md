# Meridian Harbor GraphRAG benchmark

A fictional engineering portfolio designed to compare answer quality from baseline RAG and GraphRAG. All people, companies, customers, events, and amounts are synthetic. The observation window is January 1–September 30, 2026. This is a deliberately constructed challenge set, not evidence of general superiority for either approach.

## Contents and ingestion boundary

- `sources/`: 25 short, independently authored-style plaintext records. Ingest only these files, preserving file identities and document boundaries.
- `queries.json`: 50 questions, exactly 10 each of `single_hop`, `multi_hop`, `connection`, `aggregation`, and `global_theme`.
- `DESIGN.md`: evaluator-only entity map, fact-chain audit, and question coverage notes.

Keep this README, DESIGN.md, queries, expected facts, and reference points out of all retrieval indexes, extraction inputs, community summaries, and answering context. The question text is the only query-file field supplied to the answering system. Do not concatenate different source documents into a chunk. A chunker may split documents or overlap within a document; each multi-hop question still requires facts from multiple files even if a whole document is one chunk. Generated contextual descriptions may introduce cross-document information; record any such enrichment as part of the system being compared.

No implementation, evaluator, or pipeline modification is included. Existing AtlasDesk sources and Python queries are unchanged. These JSON records require a future answer-level evaluator; the existing quote-matching chunk-recall evaluator is not directly compatible.

## Reading the answer key

For the 40 factual questions, `expected_facts` are propositions the final answer must express, not literal strings to match. Semantically equivalent wording, aliases resolved to canonical entities, and equivalent date/amount formats count. Each array item is a scoring unit; when an item contains several clauses, all its clauses must be correct to pass that unit. This deliberately makes paired list entries and full relationship paths stricter than isolated name recall.

`evidence_documents` are an evaluator's sufficient supporting file set, with names relative to `sources/`. They are not chunks and are not necessarily the only valid supporting documents. An answer may cite other records that entail the same facts. Negative conclusions are limited to the collection's explicitly bounded registers and scope. Do not assume an absent edge is universally impossible.

Multi-hop questions explicitly request intermediate links. `hop_count` counts the relationship steps being asked about, not the number of files: an alias lookup may require an additional file. A terminal name alone does not pass all hops. Connection questions similarly require the path, including direct versus indirect dependence. For aggregation questions, `expected_set` identifies the exact entity or pairing set for an additional completeness check; descriptive clauses and numeric values are still scored using `expected_facts`. Ignore ordering, penalize missing and extra members, and resolve aliases consistently.

For the 10 global questions, `reference_points` are grounded calibration examples with source files. They are neither an exhaustive answer nor a single required wording. Reward additional supported insights and reasonable recommendations explicitly labeled as recommendations. Do not turn these points into a rigid reference-answer match.

## Suggested evaluation protocol (instructions only)

Use the same source files, answering model, answer-length limit, citation requirement, and question texts for both systems. State each system's retrieval/summary budgets and local/global routing in advance. Record actual answering context tokens; equal model choice alone does not equalize evidence budget. Freeze the corpus and question set before comparing results. Use a different development set for tuning, or disclose that this small public set was used for development.

For factual questions, have a judge assess every expected-fact unit against the final answer and supporting sources: yes or no, with a short rationale. An omitted or contradicted fact fails. Report macro average fact coverage and the proportion of answers with every required unit correct, separately for each factual type. For `multi_hop`, the latter is the all-hops-correct rate. Also report contradictions or unsupported additions, because fact coverage alone can reward an answer that includes the right facts amid false claims. For aggregation, additionally report exact-set accuracy and set precision/recall.

For global questions, compare anonymized answers head to head, with the judge given the question and corpus. Judge comprehensiveness (coverage of relevant themes), diversity (distinct supported perspectives rather than repetition), and empowerment (useful explanation and evidence-grounded decision support). Evaluate grounding separately; invented causal links or measurements should not earn credit. Allow ties. Reverse A/B order and reconcile disagreements; report per-dimension wins/ties/losses and judge agreement. These are benchmark instructions inspired by common GraphRAG evaluation dimensions, not a claim of exact replication of any published experiment.

Report all five types separately, including the 10-question single-hop control group. Ten questions per type offer limited statistical precision; global prompts intentionally overlap in themes, so do not present 50 questions as 50 independent observations. Report per-query results and uncertainty if drawing comparative conclusions. Do not pre-label GraphRAG as the winner.

Record indexing calls, input/output tokens, monetary cost using the actual model prices at run time, elapsed indexing time, and query cost/latency for both methods. Include extraction, alias merging, community summaries, and any query-time traversal/summarization in GraphRAG accounting. Distinguish one-time indexing from recurring query cost. Evaluate final answers rather than treating graph descriptions as retrieved chunks. Chunk recall may remain a separate baseline diagnostic but is not a shared answer-quality metric.

## Deliberate limits

The documents are short so they can be inspected manually. Cross-document structure, aliases, and completeness tasks create the difficulty; total volume does not simulate a large enterprise archive. Many records share a repeated organizational pattern, and a strong baseline with enough evidence budget may answer them well. The set includes neither unanswerable questions nor a temporal ownership-change challenge. It tests compositional retrieval, entity resolution, aggregation, and corpus synthesis within a stable, closed fictional scope.
