import pandas as pd
import numpy as np

class FeatureCalculator:
    def __init__(self):
        pass
        
    def calculate_features(self, reps_df, props_df, objs_df, rels_df):
        # Calculate derived relationship score
        if not rels_df.empty:
            rels_df['relationship_score'] = rels_df['trust'] * (1 - rels_df['betrayal_prob'])
        
        # Calculate objection weights
        proposal_objections = {}
        if not objs_df.empty and not reps_df.empty:
            merged_objs = objs_df.merge(reps_df[['id', 'influence']], left_on='rep_id', right_on='id', how='left')
            merged_objs['influence'] = merged_objs['influence'].fillna(0)
            merged_objs['objection_weight'] = merged_objs['severity'] * merged_objs['influence']
            
            # Aggregate per proposal
            objection_sum = merged_objs.groupby('proposal_id')['objection_weight'].sum().reset_index()
            proposal_objections = dict(zip(objection_sum['proposal_id'], objection_sum['objection_weight']))
            
        # Calculate viability
        num_reps = len(reps_df)
        max_possible_objection = 1000 * num_reps if num_reps > 0 else 1000
        
        def calculate_viability(row):
            prop_id = row['id']
            priority = row['priority']
            obj_weight = proposal_objections.get(prop_id, 0)
            
            # Controversy: normalized objection weight [0, 1]
            controversy = obj_weight / max_possible_objection if max_possible_objection > 0 else 0
            
            # Layer 2 logic: A high-priority proposal everyone hates is not viable
            return priority * (1 - controversy)
            
        if not props_df.empty:
            props_df['objection_weight'] = props_df['id'].apply(lambda x: proposal_objections.get(x, 0))
            props_df['proposal_viability'] = props_df.apply(calculate_viability, axis=1)

        return reps_df, props_df, objs_df, rels_df
