import streamlit as st
import pandas as pd
import json
import networkx as nx
import matplotlib.pyplot as plt
from src.data_cleaner import DataCleaner
from src.feature_calc import FeatureCalculator
from src.graph_logic import StrategyEngine

st.set_page_config(page_title="Phantom Consensus", page_icon="🏛️", layout="wide")

st.title("🏛️ Phantom Consensus Engine")
st.markdown("Analyze political data, detect alliances, and avoid strategic traps.")

# Sidebar
st.sidebar.header("Configuration")
st.sidebar.markdown("This simple dashboard runs the Phantom Consensus Engine using your local raw data.")

# Fixed paths to the raw data files
REPS_PATH = r"..\data\raw\representatives.json"
PROPS_PATH = r"..\data\raw\proposals.json"
OBJS_PATH = r"..\data\raw\objections.json"
RELS_PATH = r"..\data\raw\relations.csv"

if st.sidebar.button("Run Consensus Engine", type="primary"):
    with st.spinner("Processing Data and Running Strategic Logic..."):
        try:
            # 1. Clean Data
            cleaner = DataCleaner()
            reps_df, props_df, objs_df, rels_df = cleaner.load_and_clean(
                REPS_PATH, PROPS_PATH, OBJS_PATH, RELS_PATH
            )
            
            # 2. Features
            feature_calc = FeatureCalculator()
            reps_df, props_df, objs_df, rels_df = feature_calc.calculate_features(
                reps_df, props_df, objs_df, rels_df
            )
            
            # 3. Logic & Alliances
            engine = StrategyEngine()
            engine.build_graph(reps_df, rels_df)
            alliances = engine.find_alliances(rels_df)
            
            # 4. Decisions
            output_data = engine.make_decisions(reps_df, props_df, objs_df, rels_df, alliances)
            
            st.success("Analysis Complete! Traps Avoided.")
            
            # Display Metrics
            st.subheader("📊 Engine Metrics")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Representatives", len(reps_df))
            col2.metric("Total Proposals", len(props_df))
            col3.metric("Detected Alliances", len(alliances))
            col4.metric("Selected Proposals", len(output_data['final_agreement']['proposals']))
            
            st.divider()
            
            # Display Results and Graph side-by-side
            col_results, col_graph = st.columns([1, 2])
            
            with col_results:
                st.subheader("📄 Final Agreement")
                st.json(output_data)
                
            with col_graph:
                st.subheader("🤝 Stable Alliance Network")
                st.caption("Bidirectional trust networks free of infiltrators and false friends.")
                
                if len(alliances) > 0:
                    G = nx.Graph()
                    # Add nodes and edges for alliances
                    for i, alliance in enumerate(alliances):
                        for node in alliance:
                            G.add_node(node, group=i)
                        for j in range(len(alliance)):
                            for k in range(j+1, len(alliance)):
                                G.add_edge(alliance[j], alliance[k])
                                
                    fig, ax = plt.subplots(figsize=(8, 6))
                    pos = nx.spring_layout(G, k=0.5, iterations=50)
                    
                    # Draw nodes and edges
                    nx.draw_networkx_nodes(G, pos, node_color='skyblue', node_size=2000, edgecolors='black')
                    nx.draw_networkx_edges(G, pos, edge_color='gray', width=2)
                    nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold')
                    
                    ax.margins(0.2)
                    plt.axis("off")
                    st.pyplot(fig)
                else:
                    st.info("No stable alliances detected based on the strict bidirectional trust rules.")
                    
        except Exception as e:
            st.error(f"An error occurred: {e}")
            st.info("Make sure the raw data files are located in `c:\\Coding\\Hackathons,events,workshops\\code2create\\ps5\\data\\raw\\`")
else:
    st.info("👈 Click **Run Consensus Engine** in the sidebar to begin.")
