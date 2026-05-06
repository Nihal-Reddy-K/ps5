# Phantom Consensus Engine - Strategic Approach

## Architecture Overview
Our solution is modeled as a 4-phase data pipeline leveraging `pandas` for robust ETL (Extract, Transform, Load) and Data Cleaning, and `networkx` for Graph-based Strategic Logic.

The system is separated into three core modules:
1. `data_cleaner.py` (Layer 1: Data Integrity)
2. `feature_calc.py` (Layer 2: Feature Engineering)
3. `graph_logic.py` (Layer 3 & 4: Strategic Logic & Alliance Detection)
4. `consensus_engine.py` (The main orchestrator)

## Phase 1: Robust Data Ingestion (Layer 1)
Real-world political data is noisy. Our engine anticipates and handles dirty inputs gracefully:
* **ID Normalization:** Mixed-case IDs and trailing whitespaces are stripped and lowercased (`normalize_id`), ensuring `REP_001`, `rep_001`, and ` rep_001 ` resolve to the same entity.
* **Type Enforcement & Outlier Clamping:** String-encoded numbers (e.g., `"85"`) are cast to integers. Values out of range (like influence > 100) are clamped to the logical maximum, while nulls/missing values are given safe defaults (0).
* **Referential Integrity (Ghost Busting):** We enforce referential constraints manually. If an objection or proposal references a `rep_id` that does not exist in the cleaned `representatives` dataset, it is purged.
* **Fault Tolerance:** Corrupted CSV rows in `relations.csv` are skipped gracefully using `on_bad_lines='skip'` rather than crashing the system.
* **Deduplication:** When identical proposal IDs exist with conflicting data, we deduplicate by keeping the last valid entry.

## Phase 2: Feature Engineering (Layer 2)
Raw metrics are translated into strategic behavioral insights:
* **Relationship Score:** Calculated as `trust * (1 - betrayal_prob)`. A rep with high trust but high betrayal probability yields a highly penalized, dangerous score.
* **Objection Weight:** We sum the product of `severity` and `objector_influence` for each proposal to measure the true political resistance to a bill.
* **Controversy & Viability:** We establish `controversy` as the normalized objection weight against the maximum possible objection score. `proposal_viability` is then calculated as `priority * (1 - controversy)`. A high-priority bill that everyone hates yields a near-zero viability.

## Phase 3: Graph-Based Alliance Detection (Layer 4)
We model representatives as nodes and relationships as edges in a `networkx` Graph.
* **The "False Friend" Trap:** To detect true alliances, we look exclusively at *bidirectional* edges. If Rep A trusts Rep B, but Rep B does not trust Rep A, the edge is discarded.
* **Clique Detection:** Using `networkx.find_cliques()`, we extract maximal complete subgraphs where every member mutually trusts every other member, ensuring stable alliances free from the "Cascading Betrayal" and "Alliance Hijack" traps.
* **The "Faction Infiltrator" Trap:** We group targets by faction. If a representative has a high average `betrayal_prob` specifically against members of their *own* claimed faction, they are tagged as an Infiltrator and isolated.

## Phase 4: Final Consensus Engine (Layer 4)
* **The "Poison Pill" Trap:** Proposals with extreme priority but universal severe objections have a negative/zero `proposal_viability` and are filtered out entirely. We select the top viable proposals.
* **The "Trojan Horse" Trap:** When selecting supporters, any rep with a critically high global `betrayal_prob` is excluded.
* **Supporter Coherence:** We ensure that no selected supporter holds an objection with a severity > 5 against the chosen proposals.
* **Minimum Viable Validation:** Fallbacks are in place to ensure we always return at least one valid proposal and one valid supporter if all heuristic thresholds filter everything out.

## Extensibility & Limitations
* **Scale:** Graph clique detection can be mathematically intensive ($O(3^{n/3})$ worst case), but works exceptionally well for <= 500 representatives.
* **Metrics:** The viability heuristic is highly defensive. In a scenario where all proposals are highly controversial, the system will conservatively pick the "least bad" option rather than risking a total collapse.
