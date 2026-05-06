import json
import pandas as pd
import numpy as np

def normalize_id(id_val):
    if pd.isna(id_val):
        return None
    return str(id_val).strip().lower()

def safe_int(val, default=0, min_val=None, max_val=None):
    if pd.isna(val) or val is None:
        return default
    try:
        val = int(float(val)) # float() first to handle strings like "85.0"
        if min_val is not None:
            val = max(min_val, val)
        if max_val is not None:
            val = min(max_val, val)
        return val
    except (ValueError, TypeError):
        return default

def safe_float(val, default=0.0, min_val=None, max_val=None):
    if pd.isna(val) or val is None:
        return default
    try:
        val = float(val)
        if min_val is not None:
            val = max(min_val, val)
        if max_val is not None:
            val = min(max_val, val)
        return val
    except (ValueError, TypeError):
        return default

class DataCleaner:
    def __init__(self):
        pass
        
    def load_and_clean(self, reps_path, props_path, objs_path, rels_path):
        reps_df = self._clean_representatives(reps_path)
        
        # We need the valid rep IDs for ghost busting
        valid_rep_ids = set(reps_df['id']) if not reps_df.empty else set()
        
        props_df = self._clean_proposals(props_path, valid_rep_ids)
        valid_prop_ids = set(props_df['id']) if not props_df.empty else set()
        
        objs_df = self._clean_objections(objs_path, valid_rep_ids, valid_prop_ids)
        rels_df = self._clean_relations(rels_path, valid_rep_ids)
        
        return reps_df, props_df, objs_df, rels_df

    def _clean_representatives(self, path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            df = pd.DataFrame(data)
        except Exception as e:
            print(f"Error loading {path}: {e}")
            return pd.DataFrame(columns=['id', 'name', 'faction', 'influence'])

        if df.empty:
            return df
            
        # Normalize ID
        if 'id' in df.columns:
            df['id'] = df['id'].apply(normalize_id)
            # Remove rows with null IDs
            df = df.dropna(subset=['id'])
            # Deduplicate by keeping the last occurrence
            df = df.drop_duplicates(subset=['id'], keep='last')
            
        if 'influence' in df.columns:
            df['influence'] = df['influence'].apply(lambda x: safe_int(x, default=0, min_val=0, max_val=100))
            
        return df

    def _clean_proposals(self, path, valid_rep_ids):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            df = pd.DataFrame(data)
        except Exception as e:
            print(f"Error loading {path}: {e}")
            return pd.DataFrame(columns=['id', 'title', 'sponsor', 'priority'])

        if df.empty:
            return df

        if 'id' in df.columns:
            df['id'] = df['id'].apply(normalize_id)
            df = df.dropna(subset=['id'])
            df = df.drop_duplicates(subset=['id'], keep='last')
            
        if 'sponsor' in df.columns:
            df['sponsor'] = df['sponsor'].apply(normalize_id)
            # Ghost Busting: exclude proposals where sponsor doesn't exist
            if valid_rep_ids:
                df = df[df['sponsor'].isin(valid_rep_ids)]
                
        if 'priority' in df.columns:
            df['priority'] = df['priority'].apply(lambda x: safe_int(x, default=1, min_val=1, max_val=10))
            
        return df

    def _clean_objections(self, path, valid_rep_ids, valid_prop_ids):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            df = pd.DataFrame(data)
        except Exception as e:
            print(f"Error loading {path}: {e}")
            return pd.DataFrame(columns=['rep_id', 'proposal_id', 'severity'])

        if df.empty:
            return df

        if 'rep_id' in df.columns:
            df['rep_id'] = df['rep_id'].apply(normalize_id)
            
        if 'proposal_id' in df.columns:
            df['proposal_id'] = df['proposal_id'].apply(normalize_id)
            
        # Ghost Busting
        if valid_rep_ids and 'rep_id' in df.columns:
            df = df[df['rep_id'].isin(valid_rep_ids)]
        if valid_prop_ids and 'proposal_id' in df.columns:
            df = df[df['proposal_id'].isin(valid_prop_ids)]
            
        if 'severity' in df.columns:
            df['severity'] = df['severity'].apply(lambda x: safe_int(x, default=1, min_val=1, max_val=10))
            
        return df

    def _clean_relations(self, path, valid_rep_ids):
        try:
            # on_bad_lines='skip' will gracefully handle corrupted CSV lines
            df = pd.read_csv(path, on_bad_lines='skip')
        except Exception as e:
            print(f"Error loading {path}: {e}")
            return pd.DataFrame(columns=['from', 'to', 'trust', 'rivalry', 'betrayal_prob'])

        if df.empty:
            return df

        if 'from' in df.columns:
            df['from'] = df['from'].apply(normalize_id)
        if 'to' in df.columns:
            df['to'] = df['to'].apply(normalize_id)
            
        # Ghost Busting
        if valid_rep_ids:
            if 'from' in df.columns:
                df = df[df['from'].isin(valid_rep_ids)]
            if 'to' in df.columns:
                df = df[df['to'].isin(valid_rep_ids)]
                
        if 'trust' in df.columns:
            df['trust'] = df['trust'].apply(lambda x: safe_int(x, default=0, min_val=0, max_val=100))
        if 'rivalry' in df.columns:
            df['rivalry'] = df['rivalry'].apply(lambda x: safe_int(x, default=0, min_val=0, max_val=100))
        if 'betrayal_prob' in df.columns:
            df['betrayal_prob'] = df['betrayal_prob'].apply(lambda x: safe_float(x, default=0.0, min_val=0.0, max_val=1.0))

        return df
