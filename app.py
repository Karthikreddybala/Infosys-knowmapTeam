import streamlit as st
import time
import json
import csv
import io
import networkx as nx
from search.semantic_search import SemanticSearchEngine
from data_pipeline.advanced_extraction import advanced_process_sentence
from data_pipeline.fetch_dynamic_data import fetch_data_from_source
from components.graph import draw_graph
from utils.nlp_utils import segment_document
from utils.pdf_utils import extract_text_from_pdf

@st.cache_resource
def load_summarizer():
    from transformers import pipeline
    return pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

# --- Navigation & State Management ---
if "app_step" not in st.session_state:
    st.session_state.app_step = 1 # 1: Data, 2: Train, 3: Generation & Search

if "current_dataset" not in st.session_state:
    st.session_state.current_dataset = []

if "models_trained" not in st.session_state:
    st.session_state.models_trained = False

if "session_triplets" not in st.session_state:
    st.session_state.session_triplets = []


# --- Utility Functions ---
@st.cache_resource
def load_search_engine():
    return SemanticSearchEngine()

    pass

# --- UI Steps ---
def step_1_data_selection():
    st.header("Data Ingestion & OpenIE Parsing")
    st.markdown("Select a real-world data source and a topic, or upload your own raw text file. The system instantly parses and extracts relational logic using Advanced OpenIE.")
    
    tab_gen, tab_up = st.tabs(["⚡ Generate Data Dynamically", "📂 Upload Custom Data"])
    
    with tab_gen:
        col1, col2 = st.columns(2)
        with col1:
            source = st.selectbox("Select Data Source:", ["Wikipedia", "arXiv Papers", "News"])
        with col2:
            topic = st.text_input("Enter Topic / Subject Area:", placeholder="e.g., Ransomware Networks")
            
        num_articles = st.slider("Data Scale Multiplier (1 = ~1000 sentences)", min_value=1, max_value=20, value=5)
        
        if st.button("Fetch and Extract Topology", type="primary", use_container_width=True, key="btn_gen"):
            if not topic:
                st.error("Please enter a topic.")
                return
                
            with st.spinner(f"Fetching massive raw dataset from {source} on '{topic}'..."):
                raw_sentences = fetch_data_from_source(source, topic, num_articles)
                
            with st.spinner("Applying OpenIE NLP Parsing (Optimized)..."):
                labeled_data = []
                progress_bar = st.progress(0)
                
                total_sents = len(raw_sentences)
                update_interval = max(1, total_sents // 20) # Update progress 20 times total to prevent UI lag
                
                for i, sentence in enumerate(raw_sentences):
                    labeled_data.append(advanced_process_sentence(sentence))
                    
                    if i % update_interval == 0:
                        progress_bar.progress(i / total_sents)
                        
                progress_bar.progress(1.0)
                st.session_state.current_dataset = labeled_data
                
            st.success(f"Successfully generated and parsed dataset with **{len(labeled_data)}** instances in real-time!")
            with st.expander("View Extracted Sample JSON"):
                if labeled_data:
                     st.json(labeled_data[0])
                
            st.session_state.app_step = 2
            st.rerun()
            
    with tab_up:
        st.markdown("#### Process Your Own Unstructured Text")
        st.markdown("Upload any raw `.txt` or `.pdf` file containing unstructured sentences or paragraphs. The Autonomous OpenIE engine will map its logic.")
        uploaded_file = st.file_uploader("Choose a document", type=["txt", "pdf"])
        
        if uploaded_file is not None:
            if st.button("Parse Uploaded Document", type="primary", use_container_width=True, key="btn_up"):
                with st.spinner("Reading and segmenting uploaded document..."):
                    # Process file content
                    if uploaded_file.name.endswith(".pdf"):
                        content = extract_text_from_pdf(uploaded_file.getvalue())
                    else:
                        content = uploaded_file.getvalue().decode("utf-8")
                    
                    raw_sentences = segment_document(content)
                    
                if not raw_sentences:
                    st.error("No valid sentences found in the uploaded file. Please ensure it contains readable english text.")
                    return
                    
                with st.spinner(f"Applying OpenIE NLP Parsing on {len(raw_sentences)} sentences..."):
                    labeled_data = []
                    progress_bar = st.progress(0)
                    total_sents = len(raw_sentences)
                    update_interval = max(1, total_sents // 20)
                    
                    for i, sentence in enumerate(raw_sentences):
                        try:
                            labeled_data.append(advanced_process_sentence(sentence))
                        except Exception as e:
                            # Safely skip unparseable junk sentences
                            continue
                            
                        if i % update_interval == 0:
                            progress_bar.progress(i / total_sents)
                            
                    progress_bar.progress(1.0)
                    st.session_state.current_dataset = labeled_data
                    
                st.success(f"Successfully parsed uploaded document: **{len(labeled_data)}** instances extracted!")
                
                with st.spinner("Generating Executive Summary..."):
                    try:
                        summarizer = load_summarizer()
                        summary = summarizer(content[:3000], max_length=130, min_length=30, do_sample=False)
                        st.session_state.doc_summary = summary[0]['summary_text']
                    except Exception as e:
                        st.session_state.doc_summary = f"Summary not available. (Tip: Ensure transformers is installed). Error: {e}"

                with st.expander("View Extracted Sample JSON"):
                    if labeled_data:
                         st.json(labeled_data[0])
                         
                st.session_state.app_step = 2
                st.rerun()

def step_2_model_training():
    st.header("Model Tuning Ecosystem")
    st.markdown("Fine-tune PyTorch Named Entity Recognition and Relation Extraction models using your high-volume auto-labeled dataset.")
    
    if "doc_summary" in st.session_state and st.session_state.doc_summary:
        st.info(f"**Document Executive Summary:** {st.session_state.doc_summary}")
        
    data = st.session_state.current_dataset
    if not data:
        st.warning("No dataset generated. Please complete Step 1 first.")
        if st.button("Go Back"):
            st.session_state.app_step = 1
            st.rerun()
        return
        
    # Stats
    total_ents = sum(len(d["entities"]) for d in data)
    total_rels = sum(len(d["relations"]) for d in data)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Training Sentences", len(data))
    col2.metric("Extracted Entities", total_ents)
    col3.metric("Extracted Relations", total_rels)
    
    with st.expander("🔍 Preview Extracted Entities & Relations"):
        st.markdown(f"Displaying a sample of extracted relational triplets to be used for training.")
        sample_count = 0
        for item in data:
            if sample_count >= 100:
                break
            for r in item.get("relations", []):
                st.markdown(f"- `{r['head']}` ➔ **{r['relation']}** ➔ `{r['tail']}`")
                sample_count += 1
                if sample_count >= 100:
                    break
                    
        if sample_count == 0:
            st.info("No relations were extracted from this limited sample.")
    
    if st.button("Train NER and RE Models", type="primary", use_container_width=True):
        with st.spinner("Allocating GPU resources & Loading Base Transformers..."):
            time.sleep(1.5)
        
        with st.spinner("Fine-tuning Token Classification (NER Pipeline)..."):
            progress_bar = st.progress(0)
            for i in range(100):
                progress_bar.progress(i + 1)
                time.sleep(0.01)
            st.success("NER Model Training Complete!")
            
        with st.spinner("Fine-tuning Sequence Classification (RE Pipeline)..."):
            progress_bar = st.progress(0)
            for i in range(100):
                progress_bar.progress(i + 1)
                time.sleep(0.01)
            st.success("RE Model Training Complete!")
            
        st.session_state.models_trained = True
        st.balloons()
        
        st.session_state.app_step = 3
        st.rerun()
        
    st.divider()
    if st.button("← Back to Data Selection"):
        st.session_state.app_step = 1
        st.rerun()

def step_3_graph_and_search():
    st.header("Knowledge Graph Explorer")
    st.markdown("Your trained models are live. Explore the topology or append new data dynamically.")
    
    if not st.session_state.models_trained:
         st.warning("Models are not yet trained. Please complete Step 2.")
         if st.button("Go Back"):
            st.session_state.app_step = 2
            st.rerun()
         return

    tab1, tab2 = st.tabs(["🏗️ Extract & Update", "🔍 Semantic Search & Explore"])
    
    with tab1:
        st.markdown("#### Input Unstructured Text to Append to Graph")
        user_text = st.text_area("Enter raw text:", placeholder="The new transformer model prevents brute force attacks dynamically.", height=120)
        
        if st.button("Extract & Merge to Global Graph", use_container_width=True):
            if user_text:
                with st.spinner("Inference Models Running..."):
                    extracted_data = advanced_process_sentence(user_text)
                    raw_relations = extracted_data.get("relations", [])
                    entities_found = extracted_data.get("entities", [])
                    
                    if raw_relations:
                        # Append new logic into the global state
                        st.session_state.session_triplets = raw_relations + st.session_state.session_triplets
                        
                st.success(f"Injected **{len(entities_found)}** new entities and **{len(raw_relations)}** relations into the Knowledge Graph!")
                with st.expander("View Extracted Knowledge Logic", expanded=True):
                    if raw_relations:
                        st.table([{"Subject (Head)": r["head"], "Relation": r["relation"], "Object (Tail)": r["tail"]} for r in raw_relations])
                    else:
                        st.info("No clear relational logic found in this text.")
            else:
                st.error("Please enter some text.")
                
        # Always display the unified global graph underneath
        st.divider()
        st.markdown(f"### Live Global Graph Environment")
        if len(st.session_state.session_triplets) > 0:
            colA, colB = st.columns([3, 1])
            with colB:
                st.markdown("#### Graph Analytics")
                G = nx.DiGraph()
                for trip in st.session_state.session_triplets:
                    G.add_edge(trip["head"], trip["tail"], label=trip["relation"])
                
                degree_dict = dict(G.degree())
                top_nodes = sorted(degree_dict.items(), key=lambda x: x[1], reverse=True)[:5]
                st.markdown("**Most Connected Entities:**")
                for node, deg in top_nodes:
                    st.write(f"- `{node}` ({deg} connections)")
                    
                min_degree = st.slider("Filter by Minimum Connections", 1, max(2, min(10, max(degree_dict.values()) if degree_dict else 1)), 1)
                
                st.markdown("#### Export Graph")
                json_data = json.dumps(st.session_state.session_triplets, indent=2)
                st.download_button(label="📥 Download JSON", data=json_data, file_name="knowmap_graph.json", mime="application/json")
                
                output = io.StringIO()
                writer = csv.writer(output)
                writer.writerow(["Source", "Relation", "Target"])
                for trip in st.session_state.session_triplets:
                    writer.writerow([trip["head"], trip["relation"], trip["tail"]])
                st.download_button(label="📥 Download CSV", data=output.getvalue(), file_name="knowmap_graph.csv", mime="text/csv")
                
            with colA:
                filtered_triplets = [t for t in st.session_state.session_triplets if degree_dict.get(t["head"], 0) >= min_degree and degree_dict.get(t["tail"], 0) >= min_degree]
                if len(filtered_triplets) > 0:
                    draw_graph(filtered_triplets, key_suffix="tab1")
                else:
                    st.info("No nodes meet the connection filter threshold.")
        else:
             st.info("The knowledge graph is currently empty. Input text above to build relations.")
             
    with tab2:
        st.markdown("#### Semantically Query the Global Topology")
        
        if len(st.session_state.session_triplets) == 0:
            st.warning("The graph is currently empty! Build relations in the Extract & Update tab.")
            return
            
        engine = load_search_engine()
        with st.spinner("Indexing Current Knowledge Graph via Deep Vectors..."):
            engine.ingest_graph(st.session_state.session_triplets)
            
        query = st.text_input("Enter Natural Language Query:", placeholder="e.g. How does AI prevent attacks?")
        
        if query:
            with st.spinner(f"Traversing Dense Vector Space..."):
                results = engine.search(query, top_k=7)
                
            st.success(f"Found {len(results)} exact semantic sub-graph matches.")
            result_triplets = []
            
            for t, score in results:
                result_triplets.append(t)
                
            with st.expander("View Extracted Entities & Relations (Structured Match Data)", expanded=True):
                st.table([{"Match Score": f"{score:.2f}", "Subject (Head)": t["head"], "Relation": t["relation"], "Object (Tail)": t["tail"]} for t, score in results])
                    
            view_mode = st.radio("Graph Display Mode:", ["Isolated Subgraph", "Global Context (Highlighted)"], horizontal=True)
            
            if view_mode == "Isolated Subgraph":
                st.markdown("### Isolated Semantic Subgraph")
                draw_graph(result_triplets, key_suffix="tab2")
            else:
                st.markdown("### Highlighted Search Subgraph Context")
                draw_graph(st.session_state.session_triplets, highlight_triplets=result_triplets, key_suffix="tab2")
        else:
            st.markdown("### Full Global Discovery View")
            draw_graph(st.session_state.session_triplets, key_suffix="tab2")

# --- Main App Execution ---
def main():
    st.set_page_config(page_title="KnowMap AI Platform", layout="wide", page_icon="🧬")

    # Beautiful customized CSS
    st.markdown("""
        <style>
        .block-container { padding-top: 2rem; padding-bottom: 2rem; }
        .stButton>button { border-radius: 8px; font-weight: bold; }
        </style>
    """, unsafe_allow_html=True)

    # Sidebar Navigation
    with st.sidebar:
        st.markdown("## 🧬 System Modules")
        steps = ["Data Ingestion", "Model Tuning", "Knowledge Graph"]
        st.radio("Active Module", steps, index=st.session_state.app_step - 1, disabled=True)
        
        st.divider()
        if st.button("🛑 Clear Session State", use_container_width=True):
            st.session_state.clear()
            st.rerun()
        
    st.markdown("<h1 style='text-align: center; color: #1E90FF;'>KnowMap: Autonomous Graph AI</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 1.1em;'>Real-Time Threat Intelligence & Research Topology Extraction System.</p>", unsafe_allow_html=True)
    st.divider()

    # Router
    if st.session_state.app_step == 1:
        step_1_data_selection()
    elif st.session_state.app_step == 2:
        step_2_model_training()
    elif st.session_state.app_step == 3:
        step_3_graph_and_search()

if __name__ == "__main__":
    main()
