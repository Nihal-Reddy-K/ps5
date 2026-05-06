import networkx as nx
import pandas as pd

class StrategyEngine:
    def __init__(self):
        self.graph = nx.DiGraph()
        
    def build_graph(self, reps_df, rels_df):
        if reps_df.empty:
            return
            
        # Add nodes
        for _, row in reps_df.iterrows():
            self.graph.add_node(row['id'], **row.to_dict())
            
        if rels_df.empty:
            return
            
        # Add edges
        for _, row in rels_df.iterrows():
            self.graph.add_edge(row['from'], row['to'], **row.to_dict())
            
    def _is_infiltrator(self, rep_id, reps_df, rels_df):
        # Layer 4 Trap: Faction Infiltrator - Betrays own faction members
        rep_data = reps_df[reps_df['id'] == rep_id]
        if rep_data.empty: return True
        faction = rep_data.iloc[0]['faction']
        
        if pd.isna(faction) or faction is None:
            return False
            
        # Get targets this rep betrays
        rep_rels = rels_df[rels_df['from'] == rep_id]
        if rep_rels.empty: return False
        
        # Merge to get target factions
        target_factions = rep_rels.merge(reps_df[['id', 'faction']], left_on='to', right_on='id')
        own_faction_targets = target_factions[target_factions['faction'] == faction]
        
        if own_faction_targets.empty:
            return False
            
        avg_betrayal = own_faction_targets['betrayal_prob'].mean()
        # High threshold for infiltrator
        return avg_betrayal >= 0.8
        
    def find_alliances(self, rels_df, min_trust=70, max_rivalry=30, max_betrayal=0.3):
        # Layer 4 Trap: False Friend (Bidirectional trust required)
        UG = nx.Graph()
        
        edges_dict = {}
        if not rels_df.empty:
            for _, row in rels_df.iterrows():
                edges_dict[(row['from'], row['to'])] = row

        valid_nodes = set()
        for u, v in edges_dict.keys():
            if (v, u) in edges_dict:
                uv = edges_dict[(u, v)]
                vu = edges_dict[(v, u)]
                
                # Check bidirectional stability
                if (uv['trust'] >= min_trust and vu['trust'] >= min_trust and
                    uv['rivalry'] <= max_rivalry and vu['rivalry'] <= max_rivalry and
                    uv['betrayal_prob'] <= max_betrayal and vu['betrayal_prob'] <= max_betrayal):
                    UG.add_edge(u, v)
                    valid_nodes.add(u)
                    valid_nodes.add(v)
                    
        # Find cliques
        cliques = list(nx.find_cliques(UG))
        
        # Filter and sort cliques
        valid_alliances = [c for c in cliques if len(c) > 1]
        valid_alliances.sort(key=len, reverse=True)
        final_alliances = []
        assigned = set()
        
        for c in valid_alliances:
            disjoint = [node for node in c if node not in assigned]
            if len(disjoint) > 1:
                final_alliances.append(disjoint)
                assigned.update(disjoint)
                
        return final_alliances

    def make_decisions(self, reps_df, props_df, objs_df, rels_df, alliances):
        """Generates the final strategic agreement avoiding traps."""
        
        # 1. Identify valid proposals
        # Avoid Poison Pills (High priority but universally objected to -> negative viability)
        if not props_df.empty:
            # We only consider proposals with viability > threshold
            # Average viability varies, let's take the ones with highest viability
            valid_props = props_df[props_df['proposal_viability'] > 0]
            valid_props = valid_props.sort_values(by='proposal_viability', ascending=False)
            
            selected_proposals = valid_props['id'].tolist()
            
            # Try to pick top 2
            selected_proposals = selected_proposals[:2]
        else:
            selected_proposals = []
            
        # 2. Identify supporters
        supporters = []
        
        # Calculate global betrayal for Trojan Horse detection
        avg_betrayal_per_rep = {}
        if not rels_df.empty:
            avg_betrayal_per_rep = rels_df.groupby('from')['betrayal_prob'].mean().to_dict()
            
        for _, rep in reps_df.iterrows():
            rep_id = rep['id']
            
            # Layer 4 Trap: Trojan Horse
            avg_b = avg_betrayal_per_rep.get(rep_id, 0)
            if avg_b >= 0.85: # High global betrayal
                continue 
                
            # Layer 4 Trap: Faction Infiltrator
            if self._is_infiltrator(rep_id, reps_df, rels_df):
                continue
                
            # Supporter Coherence: Avoid making objectors into supporters
            if not objs_df.empty and len(selected_proposals) > 0:
                rep_objs = objs_df[(objs_df['rep_id'] == rep_id) & (objs_df['proposal_id'].isin(selected_proposals))]
                if not rep_objs.empty and rep_objs['severity'].max() > 5:
                    continue # Strong objector to the agreement
                    
            supporters.append(rep_id)
            
        # Minimum Viable checks (1 proposal, 1 supporter)
        if len(selected_proposals) == 0 and not props_df.empty:
            selected_proposals = [props_df.sort_values(by='priority', ascending=False).iloc[0]['id']]
            
        if len(supporters) == 0 and not reps_df.empty:
            supporters = [reps_df.sort_values(by='influence', ascending=False).iloc[0]['id']]

        return {
            "final_agreement": {
                "proposals": selected_proposals,
                "supporting_reps": supporters
            },
            "alliances": alliances
        }
