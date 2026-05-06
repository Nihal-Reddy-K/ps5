import argparse
import os
import json
from src.data_cleaner import DataCleaner
from src.feature_calc import FeatureCalculator
from src.graph_logic import StrategyEngine

def main():
    parser = argparse.ArgumentParser(description='Phantom Consensus Engine')
    parser.add_argument('--reps', type=str, default='data/representatives.json', help='Path to representatives.json')
    parser.add_argument('--props', type=str, default='data/proposals.json', help='Path to proposals.json')
    parser.add_argument('--objs', type=str, default='data/objections.json', help='Path to objections.json')
    parser.add_argument('--rels', type=str, default='data/relations.csv', help='Path to relations.csv')
    parser.add_argument('--output', type=str, default='output.json', help='Path to output JSON file')
    
    args = parser.parse_args()
    
    print("Initializing Consensus Engine...")
    
    # Check if files exist to avoid silent failures
    for path in [args.reps, args.props, args.objs, args.rels]:
        if not os.path.exists(path):
            print(f"Warning: File not found: {path}")
    
    # 1. Load and clean data (Layer 1)
    print("Phase 1: Ingesting and Cleaning Data (Layer 1: Dirty Data)...")
    cleaner = DataCleaner()
    reps_df, props_df, objs_df, rels_df = cleaner.load_and_clean(
        args.reps, args.props, args.objs, args.rels
    )
    
    print(f"Data Loaded: {len(reps_df)} reps, {len(props_df)} proposals, {len(objs_df)} objections, {len(rels_df)} relations.")
    
    # 2. Feature Engineering (Layer 2)
    print("Phase 2: Feature Engineering (Layer 2)...")
    feature_calc = FeatureCalculator()
    reps_df, props_df, objs_df, rels_df = feature_calc.calculate_features(
        reps_df, props_df, objs_df, rels_df
    )
    
    # 3. Graph Logic & Alliances (Layer 3 & 4)
    print("Phase 3: Network Graph & Alliance Detection...")
    engine = StrategyEngine()
    engine.build_graph(reps_df, rels_df)
    
    # Detect bidirectional alliances avoiding False Friends
    alliances = engine.find_alliances(rels_df)
    print(f"Detected {len(alliances)} valid alliances.")
    
    # 4. Final Decision
    print("Phase 4: Output Generation (Layer 4: Strategic Logic)...")
    output_data = engine.make_decisions(reps_df, props_df, objs_df, rels_df, alliances)
    
    with open(args.output, 'w') as f:
        json.dump(output_data, f, indent=4)
        
    print(f"Results successfully written to {args.output}")

if __name__ == '__main__':
    main()
