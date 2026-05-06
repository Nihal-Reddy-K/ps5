# Phantom Consensus

## Team Information
- **Team Name**: ByteUs
- **Year**: 1st
- **All-Female Team**: No

## Architecture Overview

#### Describe your approach here. Keep it short and clear.

- **Data Cleaning:** We built a robust pipeline using `pandas` to normalize IDs (lowercased and stripped), defensively cast strings to integers with bounds clipping (e.g., `influence` 0-100), and gracefully skip corrupted CSV rows. We also enforced referential integrity by purging "Ghost" objections referencing non-existent representatives.
- **Alliance Detection:** We modeled politicians as a graph using `networkx`. To avoid "False Friends", we only established edges where trust was explicitly high and bidirectional. We then used clique detection to find mutual alliances, while proactively isolating "Faction Infiltrators" who showed high betrayal probabilities against their own faction members.
- **Proposal Prioritization:** We engineered a `proposal_viability` metric. We first calculated an `objection_weight` by multiplying objection severity by the objector's influence. We normalized this to determine controversy, setting `proposal_viability = priority * (1 - controversy)`.
- **Consensus Strategy:** We selected the highest-scoring viable proposals, strictly avoiding "Poison Pills" (zero viability). For our supporters list, we selected representatives lacking severe objections to the chosen bills, explicitly excluding "Trojan Horses" (reps with high global average betrayal probabilities) to ensure lasting stability.

**Note:** Please do not change the format or spelling of anything in this README. The fields are extracted using a script, so any changes to the structure or formatting may break the extraction process.
