# Evaluator-only design notes

Do not ingest this file. It contains cross-document joins and answer-key information.

## Entity and relationship map

| Project | Target → dependency | Engineering team / lead | Supplier of dependency | Sponsor | Pilot |
|---|---|---|---|---|---|
| Project Harbor | Ledger service → Settlement Router | Payments Engineering / Priya Shah | Cobalt Clearing | Elena Moss | Northstar Clinics |
| Project Beacon | Gatehouse → Session Cache | Identity Engineering / Omar Bell | Sable Trust | Victor Hale | Alder Bank |
| Project Orchard | Beacon Warehouse → Flowline | Data Platform / Mei Chen | Pinebridge Data | Elena Moss | Juniper Freight |
| Project Relay | Dispatch Hub → Noticeboard | Customer Operations / Luis Ortega | Lumen Post | Dana Wu | Solstice Retail |
| Project Compass | Watchtower → Vault Relay | Reliability Engineering / Nora Reed | Sable Trust | Victor Hale | Tern Energy |

Each row's two services share an engineering owner, but the incident reports distinguish consumer impact from the triggering component. This prevents confusing the dependency path with demonstrated root cause.

Aliases: Ledger service = the ledger = LDG; Gatehouse = GH; Beacon Warehouse = BW; Flowline = FL; Dispatch Hub = Dispatch; Vault Relay = VR; Cobalt Clearing = Cobalt; Sable Trust = Sable = ST; Pinebridge Data = Pinebridge; Lumen Post = LP.

Distinct entities: Priya Shah / Priya Nair; Alex Kim / Alex Rivera; Project Beacon / Beacon Warehouse / the facilities occupancy spreadsheet Beacon; Project Harbor / Harbor Operations; Project Relay / Vault Relay; Cobalt Clearing / Cobalt Analytics. Roles and contextual names resolve these without requiring outside knowledge.

## Fact placement

Leadership lives in 01, ownership in 02, runtime paths and most aliases in 03, supplier interfaces in 04, project targets/sponsors in 05, and pilot associations in 06. Contracts in 07–09 state obligations but do not identify project targets or pilots. Individual reviews in 10–14 establish late artifacts and rescheduled milestones without naming sponsors, owning teams, or pilot customers. Incidents in 15–19 establish triggers and customer impact without naming owning teams or their leads. Status in 20 uses incident IDs without duplicating ownership chains. Funding in 21 uses sponsors without duplicating projects. Records 22–25 add role rules, distractors, recovery evidence, and bounded scope.

Do not add a source containing this map or an executive summary of every pattern: that would collapse the intended cross-document work. Recurring themes appear through individual examples; no source enumerates all five causes, all five delivery slips, or all supplier-project paths.

## Multi-hop separation audit

| Query | Required relationship chain | Fact locations |
|---|---|---|
| H01 | March incident → Ledger → Payments → Priya Shah | 15; alias 03; 02; 01 |
| H02 | April incident → Gatehouse → Identity → Omar Bell | 16; alias 03; 02; 01 |
| H03 | June trigger → Flowline → Data Platform → Mei Chen | 17; alias 03; 02; 01 |
| H04 | July trigger → Noticeboard → Customer Operations → Luis Ortega | 18; 02; 01 |
| H05 | August trigger → Vault Relay → Reliability → Nora Reed | 19; alias 03; 02; 01 |
| H06 | Project Harbor → Elena Moss → $40,000 reserve | 05; 21 |
| H07 | June affected system → Project Orchard → Juniper Freight | 17; alias 03; 05; 06 |
| H08 | Late LP artifact → Project Relay → Dana Wu | 13; 05 |
| H09 | Project Beacon → Gatehouse → Identity → Omar Bell | 05; 02; 01 |
| H10 | Pinebridge → Flowline → Beacon Warehouse → Project Orchard | 04; 03; 05 |

No single source document contains a complete H-series answer. H07 intentionally has its terminal customer name in the incident report as well as the pilot register: identifying that name alone is insufficient to prove the asked project association. Required intermediate facts ensure it remains a compositional question. H06 and H08 are simpler two-step joins; H01–05 and H09–10 require three steps. File separation protects these chains even with whole-document chunks, provided chunks never span documents.

## Other question coverage

C01–05 join runtime paths to supplier interfaces; C06 joins two paths through a shared supplier and the project register. C07 spans customer, project, target, dependency, and vendor. C08 distinguishes commercial and engineering Priyas across ownership and delivery records. C09 connects a sponsor and customer through their project. C10 combines a contractual rule with two independently documented artifact delays.

A01–10 all require multiple files: supplier exposure plus slips; customer-to-slip joins; sponsor groupings; incident-to-lead groupings; open-action accountability; reserves by supplier exposure; sponsor-to-customer revised dates; trigger-to-vendor joins; lateness-filtered sponsor/date lists; and exercise-to-owner-to-project-to-customer joins. Complete scope is supplied by 03–06 and 25, rather than inferred from arbitrary search results.

G01–10 cover incident mechanisms, delivery slippage, testing realism, detection, supplier concentration, accountability, remediation progress, evidence quality, customer consequences, and next-quarter priorities. Relevant counterpoints include on-time early Cobalt artifacts, authorized old Sable revisions, non-runtime facilities work, and recovery exercises that do not demonstrate production detection gains.

## Interpretation traps to preserve

- Artifact lateness and pilot movement differ. Harbor: 12 versus 14 days; Beacon: 9 versus 14; Orchard: 14 versus 14; Relay: 6 versus 7; Compass: 11 versus 14.
- Supplier relationship or artifact delay does not establish production root cause. All five reports identify internal changes as triggers.
- September 30 status has five closed gates, five closed fixtures, and five open detection actions. Successful recovery exercises do not close alerts.
- Approved reserves total $145,000 across all projects: Harbor $40,000, Orchard $40,000, Beacon $25,000, Compass $25,000, Relay $15,000. This is neither actual spending nor a measured loss.
- Team lead accountability differs from sponsorship and procurement. Priya Nair is not the Payments lead, and Alex Rivera cannot grant security acceptance.
- INC-084 is a monitoring visibility gap; an application outage is not demonstrated. Pilot affiliation alone also does not demonstrate customer production impact.

These notes document intended structure, not empirical difficulty or a measured advantage. Run both systems to establish those outcomes.
