"""
pages/3_NLP_Pipeline.py — Module 2: Data ingestion and NLP pipeline execution.
Supports Wikipedia, ArXiv, CSV, TXT, PDF. Saves results to PostgreSQL.
"""
import streamlit as st
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth.auth_manager import decode_token
from data_pipeline.data_sources import (
    fetch_wikipedia, fetch_arxiv, load_csv, load_txt, load_pdf, get_csv_columns
)
from data_pipeline.triplet_formation import (
    run_pipeline_on_sentences, save_results_to_db, create_dataset_record, form_triplets
)

st.set_page_config(page_title="KnowMap — NLP Pipeline", page_icon="⚙️", layout="wide")

# ── Auth Guard ────────────────────────────────────────────
token = st.session_state.get("jwt_token")
payload = decode_token(token) if token else None
if not payload:
    st.warning("Please log in first.")
    st.switch_page("app.py")
    st.stop()
user_id = payload["user_id"]

# ── Header ────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🧬 KnowMap")
    if st.button("🚪 Logout"):
        st.session_state.clear()
        st.switch_page("app.py")

st.markdown("<h1>⚙️ NLP Pipeline — Data Ingestion & Extraction</h1>", unsafe_allow_html=True)
st.markdown("Select a data source, run the NLP pipeline to extract entities and relational triplets, then save results.")
st.divider()

DOMAINS = ["AI", "Cybersecurity", "Climate", "Business", "General"]

# ────────────────────────────────────────────────────────────────
#  TABS: one per source type
# ────────────────────────────────────────────────────────────────
tab_wiki, tab_arxiv, tab_csv, tab_file, tab_text = st.tabs([
    "🌐 Wikipedia", "📄 ArXiv", "📊 CSV Upload", "📁 TXT / PDF", "✍️ Raw Text"
])

# ── Shared result storage in session ─────────────────────
if "pipeline_results" not in st.session_state:
    st.session_state.pipeline_results = []
if "pipeline_dataset_name" not in st.session_state:
    st.session_state.pipeline_dataset_name = ""

def run_pipeline_ui(sentences, domain, dataset_name, source_type):
    """Run NLP pipeline with progress, store results in session."""
    if not sentences:
        st.error("No sentences found. Try a different topic or file.")
        return
    st.info(f"📝 Found **{len(sentences)}** sentences. Running NLP pipeline…")
    progress = st.progress(0)
    results_container = []

    def cb(cur, tot):
        progress.progress(cur / tot)

    results_container = run_pipeline_on_sentences(sentences, domain, cb)
    progress.progress(1.0)
    st.session_state.pipeline_results = results_container
    st.session_state.pipeline_dataset_name = dataset_name
    st.session_state.pipeline_source_type  = source_type
    st.session_state.pipeline_domain       = domain
    st.success(f"✅ Extracted **{sum(len(r['relations']) for r in results_container)}** relation triplets from **{len(results_container)}** sentences!")

# ── Wikipedia Tab ─────────────────────────────────────────
with tab_wiki:
    col1, col2 = st.columns(2)
    wiki_topic  = col1.text_input("Wikipedia Topic", placeholder="e.g. Ransomware", key="wiki_topic")
    wiki_domain = col2.selectbox("Knowledge Domain", DOMAINS, key="wiki_dom")
    wiki_limit  = st.slider("Max sentences to process", 100, 2000, 500, step=100, key="wiki_lim")
    if st.button("Fetch & Extract", type="primary", key="btn_wiki"):
        with st.spinner(f"Fetching Wikipedia article: '{wiki_topic}'…"):
            sents = fetch_wikipedia(wiki_topic, wiki_limit)
        run_pipeline_ui(sents, wiki_domain, f"Wikipedia:{wiki_topic}", "wikipedia")

# ── ArXiv Tab ─────────────────────────────────────────────
with tab_arxiv:
    col1, col2 = st.columns(2)
    arxiv_query  = col1.text_input("Search query", placeholder="e.g. deep learning IDS", key="arxiv_q")
    arxiv_domain = col2.selectbox("Knowledge Domain", DOMAINS, key="arxiv_dom")
    arxiv_papers = st.slider("Max papers to fetch", 5, 50, 15, key="arxiv_n")
    if st.button("Fetch & Extract", type="primary", key="btn_arxiv"):
        with st.spinner(f"Searching ArXiv: '{arxiv_query}'…"):
            sents = fetch_arxiv(arxiv_query, arxiv_papers)
        run_pipeline_ui(sents, arxiv_domain, f"ArXiv:{arxiv_query}", "arxiv")

# ── CSV Tab ───────────────────────────────────────────────
with tab_csv:
    csv_file = st.file_uploader("Upload CSV file", type=["csv"], key="csv_up")
    if csv_file:
        file_bytes = csv_file.getvalue()
        cols = get_csv_columns(file_bytes)
        col_sel = st.selectbox("Select text column (or 'Auto-combine all')", ["Auto-combine all"] + cols)
        csv_domain = st.selectbox("Knowledge Domain", DOMAINS, key="csv_dom")
        if st.button("Process CSV", type="primary", key="btn_csv"):
            import io
            chosen_col = None if col_sel == "Auto-combine all" else col_sel
            with st.spinner("Reading CSV…"):
                sents = load_csv(io.BytesIO(file_bytes), chosen_col)
            run_pipeline_ui(sents, csv_domain, f"CSV:{csv_file.name}", "csv")

# ── TXT / PDF Tab ─────────────────────────────────────────
with tab_file:
    up_file = st.file_uploader("Upload TXT or PDF", type=["txt", "pdf"], key="file_up")
    if up_file:
        file_domain = st.selectbox("Knowledge Domain", DOMAINS, key="file_dom")
        if st.button("Process File", type="primary", key="btn_file"):
            file_bytes = up_file.getvalue()
            with st.spinner("Extracting text…"):
                if up_file.name.endswith(".pdf"):
                    sents = load_pdf(file_bytes)
                else:
                    sents = load_txt(file_bytes)
            run_pipeline_ui(sents, file_domain, f"File:{up_file.name}", "pdf" if up_file.name.endswith(".pdf") else "txt")

# ── Raw Text Tab ──────────────────────────────────────────
with tab_text:
    raw_text   = st.text_area("Paste or type raw text here:", height=200, key="raw_text")
    raw_domain = st.selectbox("Knowledge Domain", DOMAINS, key="raw_dom")
    if st.button("Extract from Text", type="primary", key="btn_raw"):
        if raw_text.strip():
            result = form_triplets(raw_text.strip(), raw_domain)
            st.session_state.pipeline_results = [result]
            st.session_state.pipeline_dataset_name = "Raw Text Input"
            st.session_state.pipeline_source_type  = "txt"
            st.session_state.pipeline_domain       = raw_domain
            st.success(f"Extracted **{len(result['relations'])}** triplets!")
        else:
            st.error("Please enter some text.")

# ────────────────────────────────────────────────────────────────
#  RESULTS PANEL
# ────────────────────────────────────────────────────────────────
results = st.session_state.get("pipeline_results", [])
if results:
    st.divider()
    st.markdown("## 📊 Extraction Results")

    all_entities  = [e for r in results for e in r.get("entities", [])]
    all_relations = [rel for r in results for rel in r.get("relations", [])]

    mc1, mc2, mc3 = st.columns(3)
    mc1.metric("Sentences Processed", len(results))
    mc2.metric("Entities Found",      len(all_entities))
    mc3.metric("Relation Triplets",   len(all_relations))

    with st.expander("🔍 Preview Sample Triplets (first 50)"):
        sample = all_relations[:50]
        if sample:
            st.table([{
                "Subject (Head)": r.get("head", ""),
                "Relation":       r.get("relation", ""),
                "Object (Tail)":  r.get("tail", ""),
                "Domain":         r.get("domain", ""),
            } for r in sample])
        else:
            st.info("No relations extracted from this text.")

    with st.expander("🏷️ Preview Sample Entities (first 50)"):
        st.table(all_entities[:50])

    st.divider()
    st.markdown("### 💾 Save Results to Database")
    graph_name = st.text_input("Dataset / Graph name to save as:",
                                value=st.session_state.get("pipeline_dataset_name", "My Dataset"))
    if st.button("Save to PostgreSQL", type="primary", use_container_width=True):
        if not graph_name.strip():
            st.error("Please provide a name.")
        else:
            with st.spinner("Saving to database…"):
                ds_id = create_dataset_record(
                    user_id,
                    graph_name,
                    st.session_state.get("pipeline_source_type", "txt"),
                    len(results)
                )
                save_results_to_db(ds_id, results)
                st.session_state["saved_dataset_id"] = ds_id
            st.success(f"✅ Saved **{len(results)}** sentences to dataset ID: {ds_id}")
            st.info("➡️ Now go to **Knowledge Graph** to visualise and save your graph.")
