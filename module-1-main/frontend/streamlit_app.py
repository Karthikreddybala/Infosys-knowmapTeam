import os, time, base64, json, io
import requests
import pandas as pd
import streamlit as st

API_BASE = os.getenv("API_BASE", "http://localhost:5000/api")

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Fusion Graph | AI Cybersecurity",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Inject CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Orbitron:wght@400;700;900&display=swap');

/* Base */
html, body, [class*="css"] {
    font-family: 'Share Tech Mono', monospace !important;
    background: #050a05 !important;
    color: #c8ffc8 !important;
}
.stApp { background: #050a05 !important; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #030703 !important;
    border-right: 1px solid #00ff4140 !important;
}
section[data-testid="stSidebar"] * { color: #c8ffc8 !important; font-family: 'Share Tech Mono', monospace !important; }

/* Purge tech-labels */
span[data-testid="stHeaderActionElements"],
[data-testid="stSidebarCollapseButton"] span,
[data-testid="stSidebarCollapseButton"] p {
    font-size: 0 !important;
    color: transparent !important;
}

/* Buttons */
.stButton > button {
    background: #001a00 !important;
    color: #00ff41 !important;
    border: 1px solid #00ff4180 !important;
    border-radius: 2px !important;
    font-family: 'Share Tech Mono', monospace !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    background: #00ff4115 !important;
    border-color: #00ff41 !important;
    box-shadow: 0 0 12px #00ff4140 !important;
}

/* Inputs */
.stTextInput input, .stTextArea textarea, .stSelectbox select {
    background: #000f00 !important;
    color: #00ff41 !important;
    border: 1px solid #00ff4150 !important;
    border-radius: 2px !important;
    font-family: 'Share Tech Mono', monospace !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: #00ff41 !important;
    box-shadow: 0 0 8px #00ff4130 !important;
}

/* Metrics */
[data-testid="stMetric"] {
    background: #000f00 !important;
    border: 1px solid #00ff4130 !important;
    border-radius: 4px !important;
    padding: 12px !important;
}
[data-testid="stMetricValue"] { color: #00ff41 !important; font-family: 'Orbitron', monospace !important; }
[data-testid="stMetricLabel"] { color: #00ff4180 !important; }

/* File uploader */
[data-testid="stFileUploadDropzone"] {
    background: #000f00 !important;
    border: 2px dashed #00ff4150 !important;
    border-radius: 4px !important;
}

/* Expander */
[data-testid="stExpander"] {
    background: #000f00 !important;
    border: 1px solid #00ff4130 !important;
    border-radius: 4px !important;
}

/* Alerts */
div.stSuccess { background: #001a00 !important; color: #00ff41 !important; border-left: 4px solid #00ff41 !important; border-radius: 2px !important; }
div.stError   { background: #1a0000 !important; color: #ff4141 !important; border-left: 4px solid #ff4141 !important; border-radius: 2px !important; }
div.stWarning { background: #1a1100 !important; color: #ffd700 !important; border-left: 4px solid #ffd700 !important; border-radius: 2px !important; }
div.stInfo    { background: #00101a !important; color: #00cfff !important; border-left: 4px solid #00cfff !important; border-radius: 2px !important; }

/* Headings */
h1, h2, h3 {
    font-family: 'Orbitron', monospace !important;
    color: #00ff41 !important;
    letter-spacing: 3px !important;
    text-transform: uppercase !important;
    text-shadow: 0 0 15px #00ff4160 !important;
    background: none !important;
    -webkit-text-fill-color: #00ff41 !important;
}

/* Table / DataFrame */
[data-testid="stDataFrame"] { border: 1px solid #00ff4130 !important; }
thead th { background: #001a00 !important; color: #00ff41 !important; font-family: 'Share Tech Mono', monospace !important; }

/* Download button */
.stDownloadButton > button {
    background: #001a00 !important;
    color: #00ff41 !important;
    border: 1px solid #00ff4170 !important;
    font-family: 'Share Tech Mono', monospace !important;
    text-transform: uppercase !important;
    border-radius: 2px !important;
}

/* Radio */
[role="radiogroup"] label { color: #c8ffc8 !important; font-family: 'Share Tech Mono', monospace !important; }

/* Divider */
hr { border-color: #00ff4125 !important; }

/* Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #050a05; }
::-webkit-scrollbar-thumb { background: #00ff4140; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ── Helpers ────────────────────────────────────────────────────────────────────
def hdr(text, sub=""):
    sub_html = f"<div style='color:#00ff4170;font-size:12px;letter-spacing:2px;margin-top:2px;'>{sub}</div>" if sub else ""
    st.markdown(f"""
    <div style='padding:18px 0 12px 0;border-bottom:1px solid #00ff4125;margin-bottom:20px;'>
      <span style='font-family:Orbitron,monospace;font-size:22px;color:#00ff41;
        letter-spacing:4px;text-transform:uppercase;text-shadow:0 0 15px #00ff4160;'>{text}</span>
      {sub_html}
    </div>""", unsafe_allow_html=True)

def card_row(cols_data):
    """cols_data = list of (icon, title, value, color)"""
    cols = st.columns(len(cols_data))
    for col, (icon, title, val, clr) in zip(cols, cols_data):
        with col:
            st.markdown(f"""
            <div style='background:#000f00;border:1px solid {clr}40;border-top:2px solid {clr};
              border-radius:4px;padding:16px;text-align:center;'>
              <div style='font-size:28px;'>{icon}</div>
              <div style='color:{clr}90;font-size:11px;letter-spacing:2px;text-transform:uppercase;margin:6px 0 4px;'>{title}</div>
              <div style='color:{clr};font-size:18px;font-family:Orbitron,monospace;font-weight:700;'>{val}</div>
            </div>""", unsafe_allow_html=True)

def feature_card(icon, title, body, color="#00ff41"):
    st.markdown(f"""
    <div style='background:#000f00;border:1px solid {color}30;border-left:3px solid {color};
      border-radius:4px;padding:18px;margin-bottom:10px;'>
      <div style='font-size:24px;margin-bottom:8px;'>{icon}</div>
      <div style='color:{color};font-family:Orbitron,monospace;font-size:12px;letter-spacing:2px;
        text-transform:uppercase;margin-bottom:8px;'>{title}</div>
      <div style='color:#c8ffc8;font-size:13px;line-height:1.6;'>{body}</div>
    </div>""", unsafe_allow_html=True)

def tag(text, color="#00ff41"):
    return f"<span style='background:{color}20;border:1px solid {color}60;color:{color};font-size:11px;padding:2px 8px;border-radius:2px;margin:2px;display:inline-block;'>{text}</span>"

# ── Session state ──────────────────────────────────────────────────────────────
# Check for token in URL (passed from Next.js login)
query_params = st.query_params
url_token = query_params.get("token")

# Default values
initial_logged_in = True if url_token else False
initial_token = url_token if url_token else None
# Use a mock user if no token, otherwise we'll try to fetch or wait
initial_user = {"username": "SECURE_ADMIN", "role": "admin"}

for k, v in [("logged_in", initial_logged_in or True), ("token", initial_token), ("user", initial_user), ("page", "upload")]:
    if k not in st.session_state or st.session_state[k] is None:
        st.session_state[k] = v
# Force user to be a dict if it somehow isn't
if not isinstance(st.session_state.user, dict):
    st.session_state.user = initial_user

# If we have a token but no proper user info, we could fetch it here
if st.session_state.token and st.session_state.user.get("username") == "SECURE_ADMIN":
    try:
        # Attempt to get real user info from token
        r = requests.get(f"{API_BASE}/auth/profile", headers={"Authorization": f"Bearer {st.session_state.token}"}, timeout=5)
        if r.status_code == 200:
            st.session_state.user = r.json()
            st.session_state.logged_in = True
    except:
        pass

class MockResp:
    def __init__(self, status_code, json_data=None, content=b""):
        self.status_code = status_code
        self.json_data = json_data or {}
        self.content = content
    def json(self): return self.json_data

def api(method, path, **kwargs):
    headers = kwargs.pop("headers", {})
    if st.session_state.token:
        headers["Authorization"] = f"Bearer {st.session_state.token}"
    try:
        return requests.request(method, f"{API_BASE}{path}", timeout=60, headers=headers, **kwargs)
    except requests.exceptions.ReadTimeout:
        return MockResp(504, {"error": "TIMEOUT"})
    except requests.exceptions.ConnectionError:
        return MockResp(0, {"error": "OFFLINE"})
    except Exception as e:
        return MockResp(500, {"error": str(e)})

def show_err(resp):
    if resp is None:
        st.error("❌ Unexpected communication failure with backend.")
        return
        
    status = resp.status_code
    try:
        data = resp.json()
        err_msg = data.get('error', f'Server error {status}')
    except:
        err_msg = f"Server error {status}"

    if status == 0 or err_msg == "OFFLINE":
        st.error("❌ Cannot reach Fusion-Core — is the backend server running on port 5000?")
    elif status == 401:
        st.error("🔑 Session Unauthorized — Please login via the Portal (http://localhost:3000) to obtain a security token.")
    elif status == 504 or err_msg == "TIMEOUT":
        st.error("⏳ Intelligence Node Timeout — The upstream source is responding too slowly. Try a more specific query.")
    else:
        st.error(f"❌ {err_msg}")

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    # Header with 3-dot menu
    st.markdown("""
    <div style='display:flex;justify-content:space-between;align-items:flex-start;'>
      <div style='color:#00ff4140;'>⬡</div>
      <div style='color:#00ff4140;font-size:18px;line-height:1;margin-top:-2px;'>⋮</div>
    </div>
    <div style='padding:8px 0 16px;border-bottom:1px solid #00ff4125;margin-bottom:12px;'>
      <div style='font-family:Orbitron,monospace;color:#00ff41;font-size:18px;letter-spacing:4px;
        text-shadow:0 0 20px #00ff4180;'>FUSION GRAPH</div>
      <div style='color:#00ff4160;font-size:10px;letter-spacing:2px;margin-top:4px;'>AI CYBERSECURITY PLATFORM</div>
      <div style='margin-top:12px;display:flex;gap:12px;font-size:10px;color:#00ff4180;'>
        <span>🟢 ONLINE</span><span>🔒 AES-256</span><span>⚡ API LIVE</span>
      </div>
    </div>""", unsafe_allow_html=True)

    if st.session_state.logged_in:
        user = st.session_state.user
        st.markdown(f"""
        <div style='background:#000f00;border:1px solid #00ff4130;border-radius:4px;
          padding:12px;margin-bottom:14px;'>
          <div style='color:#00ff41;font-size:13px;'>👤 {user.get('username', 'SECURE_ADMIN').upper()}</div>
          <div style='color:#00ff4160;font-size:10px;letter-spacing:1px;margin-top:3px;'>
            CLEARANCE: {user.get('role','user').upper()}
          </div>
        </div>""", unsafe_allow_html=True)

        st.markdown("<div style='color:#00ff4170;font-size:10px;letter-spacing:2px;margin-bottom:8px;'>◈ NAVIGATION</div>", unsafe_allow_html=True)

        pages = [
            ("📡", "Upload Data",        "upload"),
            ("📦", "Data Vault",         "vault"),
            ("🔄", "Format Converter",   "convert"),
            ("🌐", "Fetch External Data","fetch"),
            ("👤", "Profile",            "profile"),
        ]
        for icon, label, key in pages:
            active = st.session_state.page == key
            btn_style = "border-color:#00ff41 !important;background:#00ff4115 !important;" if active else ""
            if st.button(f"{icon}  {label}", key=f"nav_{key}", use_container_width=True):
                st.session_state.page = key
                st.rerun()

        st.divider()
        if st.button("⏻  LOGOUT", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.token = None
            st.session_state.user = None
            # Redirect back to Next.js portal
            st.markdown('<meta http-equiv="refresh" content="0;URL=\'http://localhost:3000\'" />', unsafe_allow_html=True)
            st.rerun()

    else:
        st.warning("⚠️ Session expired. Please login via the Secure Portal.")
        if st.button("→ PORTAL LOGIN"):
            st.markdown('<meta http-equiv="refresh" content="0;URL=\'http://localhost:3000\'" />', unsafe_allow_html=True)
            st.rerun()
        st.stop()

# ALL CODE BELOW IS THE MAIN DASHBOARD
# (Removed the auth UI block entirely)

# ══════════════════════════════════════════════════════════════════════════════
# LOGGED IN — TOP BAR
# ══════════════════════════════════════════════════════════════════════════════
user = st.session_state.user
st.markdown(f"""
<div style='display:flex;align-items:center;justify-content:space-between;
  padding:10px 0 14px;border-bottom:1px solid #00ff4125;margin-bottom:24px;'>
  <div>
    <span style='font-family:Orbitron,monospace;font-size:20px;color:#00ff41;
      letter-spacing:4px;text-shadow:0 0 15px #00ff4160;'>⬡ FUSION GRAPH</span>
    <span style='color:#00ff4150;font-size:11px;font-family:Share Tech Mono,monospace;
      letter-spacing:2px;margin-left:14px;'>AI CYBERSECURITY PLATFORM</span>
  </div>
  <div style='display:flex;gap:16px;color:#00ff4180;font-size:11px;'>
    <span>🟢 SECURE</span><span>🔒 AES-256</span><span>👤 {user.get('username', 'SECURE_ADMIN').upper()}</span>
  </div>
</div>""", unsafe_allow_html=True)

page = st.session_state.page

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: UPLOAD DATA
# ══════════════════════════════════════════════════════════════════════════════
if page == "upload":
    hdr("📡 Upload Data", "Ingest datasets into the Fusion Graph Vault")

    # Feature cards
    c1, c2, c3 = st.columns(3)
    with c1:
        feature_card("🛡️", "Threat Detection", "Advanced malware & phishing detection using multiple security databases. Automatic tagging on upload.")
    with c2:
        feature_card("⚡", "Real-Time Analysis", "Lightning-fast dataset ingestion with automatic schema detection and column profiling.", "#00cfff")
    with c3:
        feature_card("👁️", "Deep Inspection", "SSL certificates, DNS records, geolocation tagging and full metadata extraction.", "#ffd700")

    st.divider()

    # Supported formats info
    st.markdown("""
    <div style='background:#000f00;border:1px solid #00ff4130;border-radius:4px;padding:14px;margin-bottom:18px;'>
      <span style='color:#00ff4180;font-size:11px;letter-spacing:2px;'>SUPPORTED FORMATS: </span>
      """ + " ".join([tag(f) for f in ["CSV", "JSON", "TXT", "PARQUET", "XLSX"]]) + """
    </div>""", unsafe_allow_html=True)

    uploaded = st.file_uploader(
        "DROP DATASET FILE HERE",
        type=["csv", "json", "txt", "parquet", "xlsx"],
        help="Supports CSV, JSON, TXT, Parquet and Excel files",
        key="uploader_main"
    )

    if uploaded:
        st.markdown("<br>", unsafe_allow_html=True)
        # Preview
        try:
            fname = uploaded.name
            ext = fname.rsplit(".", 1)[-1].lower()
            if ext == "csv":
                df = pd.read_csv(uploaded)
            elif ext == "json":
                df = pd.read_json(uploaded)
            elif ext in ("xls", "xlsx"):
                df = pd.read_excel(uploaded)
            elif ext == "txt":
                content = uploaded.read().decode("utf-8", errors="replace")
                df = pd.DataFrame({"text_content": content.splitlines()})
                uploaded.seek(0)
            else:
                df = pd.read_parquet(uploaded)

            card_row([
                ("📄", "File Name",  fname,           "#00ff41"),
                ("📊", "Rows",       f"{len(df):,}",  "#00cfff"),
                ("📋", "Columns",    str(df.shape[1]), "#ffd700"),
                ("💾", "Format",     ext.upper(),     "#ff6bff"),
            ])
            st.markdown("<br>", unsafe_allow_html=True)

            st.markdown("<div style='color:#00ff4180;font-size:11px;letter-spacing:2px;margin-bottom:6px;'>DATA PREVIEW (first 5 rows):</div>", unsafe_allow_html=True)
            st.dataframe(df.head(5), use_container_width=True)

            st.markdown("<div style='color:#00ff4180;font-size:11px;letter-spacing:2px;margin:12px 0 6px;'>COLUMN SCHEMA:</div>", unsafe_allow_html=True)
            schema_df = pd.DataFrame({
                "Column": df.columns,
                "Type": [str(dt) for dt in df.dtypes],
                "Non-Null": df.count().values,
                "Null %": [f"{df[c].isna().mean()*100:.1f}%" for c in df.columns],
                "Sample": [str(df[c].dropna().iloc[0]) if df[c].dropna().shape[0] > 0 else "N/A" for c in df.columns]
            })
            st.dataframe(schema_df, use_container_width=True, hide_index=True)

        except Exception as e:
            st.warning(f"⚠️ Preview failed: {e}")
            df = None

        st.markdown("<br>", unsafe_allow_html=True)
        col_a, col_b = st.columns(2)
        with col_a:
            dataset_name = st.text_input("DATASET NAME (optional)", placeholder="e.g., network_logs_2024")
        with col_b:
            dataset_desc = st.text_input("DESCRIPTION (optional)", placeholder="e.g., Firewall event data")

        if st.button("⬡  TRANSMIT TO VAULT", use_container_width=True):
            uploaded.seek(0)
            with st.spinner("Encrypting and transmitting..."):
                resp = api("POST", "/datasets/upload",
                           files={"file": (uploaded.name, uploaded.read(), "application/octet-stream")})
            if resp and resp.status_code == 201:
                st.success(f"✅ Dataset '{uploaded.name}' successfully secured in the Vault!")
            else:
                show_err(resp)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: VAULT
# ══════════════════════════════════════════════════════════════════════════════
elif page == "vault":
    hdr("📦 Data Vault", "All encrypted datasets stored in Fusion Graph")

    resp = api("GET", "/datasets/")
    if resp and resp.status_code == 200:
        datasets = resp.json().get("datasets", [])
    else:
        datasets = []
        if resp:
            show_err(resp)

    if not datasets:
        st.markdown("""
        <div style='text-align:center;padding:60px 0;border:2px dashed #00ff4130;border-radius:4px;'>
          <div style='font-size:48px;'>🗃️</div>
          <div style='color:#00ff4160;font-size:14px;letter-spacing:2px;margin-top:12px;'>VAULT IS EMPTY</div>
          <div style='color:#00ff4140;font-size:12px;margin-top:6px;'>Upload datasets via the 📡 Upload Data page</div>
        </div>""", unsafe_allow_html=True)
    else:
        card_row([
            ("📦", "Total Datasets", str(len(datasets)), "#00ff41"),
            ("📊", "Total Rows", f"{sum(d.get('row_count',0) for d in datasets):,}", "#00cfff"),
            ("🗂️", "Formats", str(len(set(d.get('file_type','?') for d in datasets))), "#ffd700"),
        ])
        st.markdown("<br>", unsafe_allow_html=True)

        # Search
        search = st.text_input("🔍  SEARCH VAULT", placeholder="filter by name...")
        filtered = [d for d in datasets if search.lower() in d.get('original_name','').lower()] if search else datasets

        for ds in filtered:
            fname = ds.get('original_name', 'Unknown')
            ftype = ds.get('file_type', '?').upper()
            rows  = ds.get('row_count', 0)
            cols  = ds.get('column_count', 0)
            ds_id = ds.get('id')

            with st.expander(f"📁  {fname}   ·  {ftype}  ·  {rows:,} rows × {cols} cols"):
                ca, cb, cc, cd = st.columns(4)
                ca.metric("ROWS",     f"{rows:,}")
                cb.metric("COLUMNS",  str(cols))
                cc.metric("TYPE",     ftype)
                cd.metric("ID",       str(ds_id))

                btn1, btn2, btn3 = st.columns(3)
                with btn1:
                    if st.button("📥 Download", key=f"dl_{ds_id}", use_container_width=True):
                        dl = api("GET", f"/datasets/{ds_id}/download")
                        if dl and dl.status_code == 200:
                            st.download_button("⬇  Save File", data=dl.content, file_name=fname, key=f"save_{ds_id}", use_container_width=True)
                        else:
                            show_err(dl)
                with btn2:
                    if st.button("🔄 Convert", key=f"cnv_nav_{ds_id}", use_container_width=True):
                        st.session_state.page = "convert"
                        st.rerun()
                with btn3:
                    if st.button("🗑️ Delete", key=f"del_{ds_id}", use_container_width=True):
                        dr = api("DELETE", f"/datasets/{ds_id}")
                        if dr and dr.status_code == 200:
                            st.success("Deleted from Vault")
                            st.rerun()
                        else:
                            show_err(dr)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: FORMAT CONVERTER
# ══════════════════════════════════════════════════════════════════════════════
elif page == "convert":
    hdr("🔄 Format Converter", "Transcode datasets between CSV, JSON, XLSX, Parquet, TXT and more")

    c1, c2 = st.columns(2)
    with c1:
        feature_card("📄 → 🔵", "CSV → JSON",   "Convert tabular CSV data into structured JSON records for API ingestion.")
        feature_card("📄 → 📗", "CSV → Excel",  "Export CSV data as formatted Excel spreadsheet (.xlsx).", "#00cfff")
    with c2:
        feature_card("🔵 → 📄", "JSON → CSV",   "Flatten JSON records into flat CSV format.", "#ffd700")
        feature_card("📗 → 📄", "Excel → CSV",  "Extract Excel sheets into portable CSV files.", "#ff6bff")

    st.divider()

    mode = st.radio("SELECT SOURCE", ["📁 Upload Local File", "📦 Select from Data Vault"], horizontal=True)
    
    df = None
    conv_file = None
    name, ext = "dataset", ""

    if mode == "📁 Upload Local File":
        conv_file = st.file_uploader(
            "SELECT FILE TO CONVERT",
            type=["csv", "json", "xlsx", "xls", "txt", "parquet"],
            key="conv_uploader"
        )
    else:
        with st.spinner("Accessing Vault..."):
            resp = api("GET", "/datasets/")
            datasets = (resp.json().get("datasets", []) if resp and resp.status_code == 200 else [])
        if not datasets:
            st.warning("⚠️ Vault is currently empty. Upload data first via the 📡 Upload Data page.")
        else:
            ds_names = {f"{d['original_name']} ({d['file_type'].upper()})": d for d in datasets}
            choice = st.selectbox("SELECT DATASET FROM VAULT", ["-- select --"] + list(ds_names.keys()))
            if choice != "-- select --":
                ds = ds_names[choice]
                ds_id = ds["id"]
                with st.spinner("Retrieving from secure storage..."):
                    dl = api("GET", f"/datasets/{ds_id}/download")
                if dl and dl.status_code == 200:
                    name, ext = os.path.splitext(ds['original_name'])
                    ext = ext.lower().lstrip(".")
                    conv_file = io.BytesIO(dl.content)
                    conv_file.name = ds['original_name']
                else:
                    show_err(dl)

    if conv_file:
        try:
            if not hasattr(conv_file, "name"): 
                conv_file.name = f"{name}.{ext}" if ext else name
            
            fname = conv_file.name
            name, ext = os.path.splitext(fname)
            ext = ext.lower().lstrip(".")

            if ext == "csv":
                df = pd.read_csv(conv_file)
            elif ext == "json":
                df = pd.read_json(conv_file)
            elif ext in ("xls", "xlsx"):
                df = pd.read_excel(conv_file)
            elif ext == "txt":
                # Handle bytes vs string
                try: content = conv_file.read().decode("utf-8", errors="replace")
                except: content = str(conv_file.read())
                df = pd.DataFrame({"line": content.splitlines()})
            elif ext == "parquet":
                df = pd.read_parquet(conv_file)
            else:
                df = None

            if df is not None:
                card_row([
                    ("📥", "Source",  ext.upper(),      "#00ff41"),
                    ("📊", "Rows",    f"{len(df):,}",   "#00cfff"),
                    ("📋", "Columns", str(df.shape[1]), "#ffd700"),
                ])
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("<div style='color:#00ff4180;font-size:11px;letter-spacing:2px;margin-bottom:6px;'>PREVIEW (5 rows):</div>", unsafe_allow_html=True)
                st.dataframe(df.head(5), use_container_width=True)

                st.markdown("<br>", unsafe_allow_html=True)
                out_fmt = st.selectbox(
                    "OUTPUT FORMAT",
                    [f for f in ["CSV", "JSON", "Excel (XLSX)", "Parquet", "TXT (lines)"] if f.lower().replace(" (xlsx)","").replace(" (lines)","") != ext]
                )

                if st.button("⬡  CONVERT NOW", use_container_width=True):
                    with st.spinner("Converting..."):
                        if out_fmt == "CSV":
                            data = df.to_csv(index=False).encode("utf-8")
                            mime, fn = "text/csv", f"{name}.csv"
                        elif out_fmt == "JSON":
                            data = df.to_json(orient="records", indent=2).encode("utf-8")
                            mime, fn = "application/json", f"{name}.json"
                        elif out_fmt == "Excel (XLSX)":
                            buf = io.BytesIO()
                            df.to_excel(buf, index=False)
                            data, mime, fn = buf.getvalue(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", f"{name}.xlsx"
                        elif out_fmt == "Parquet":
                            buf = io.BytesIO()
                            df.to_parquet(buf, index=False)
                            data, mime, fn = buf.getvalue(), "application/octet-stream", f"{name}.parquet"
                        else:
                            data = "\n".join(df.astype(str).apply(lambda r: "\t".join(r), axis=1)).encode("utf-8")
                            mime, fn = "text/plain", f"{name}.txt"

                    st.success(f"✅ Converted to {out_fmt}!")
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        st.download_button(
                            label=f"⬇  DOWNLOAD {out_fmt}",
                            data=data, file_name=fn, mime=mime,
                            use_container_width=True
                        )
                    with c2:
                        if st.button("📤  SAVE TO VAULT", use_container_width=True):
                            with st.spinner("Transmitting to Vault..."):
                                resp = api("POST", "/datasets/upload",
                                           files={"file": (fn, data, mime)})
                            if resp and resp.status_code == 201:
                                st.success("🚀 Secured in Data Vault!")
                            else:
                                show_err(resp)
        except Exception as e:
            st.error(f"❌ Conversion failed: {e}")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: FETCH EXTERNAL DATA
# ══════════════════════════════════════════════════════════════════════════════
elif page == "fetch":
    hdr("🌐 Fetch External Data", "Intercept live intelligence from Clearweb nodes")

    c1, c2, c3 = st.columns(3)
    with c1:
        feature_card("🔍", "Wikipedia", "Search and extract structured knowledge articles from Wikipedia as datasets.", "#00ff41")
    with c2:
        feature_card("📄", "ArXiv Research", "Download and parse cutting-edge AI and cybersecurity research papers.", "#00cfff")
    with c3:
        feature_card("📡", "News Feed", "Intercept live news streams on cybersecurity events and threat intelligence.", "#ffd700")

    st.divider()

    src_label = st.radio(
        "SELECT INTEL NODE",
        ["🔍 Wikipedia", "📄 ArXiv Papers", "📡 News Stream"],
        horizontal=True
    )
    src_map = {"🔍 Wikipedia": "wikipedia", "📄 ArXiv Papers": "arxiv", "📡 News Stream": "news"}
    src = src_map[src_label]

    q = st.text_input("SEARCH QUERY", placeholder="e.g., ransomware attack, zero-day exploit, AI security...")
    st.caption("💡 Suggested: AI Security · Malware Analysis · Quantum Cryptography · Network Intrusion · Phishing")

    cc1, cc2 = st.columns([3, 1])
    with cc2:
        max_res = st.number_input("MAX RESULTS", min_value=1, max_value=20, value=5)

    if st.button("⬡  INITIATE FETCH", use_container_width=True):
        if not q.strip():
            st.warning("⚠️ Enter a search query first.")
        else:
            if src == "news":
                fetch_url = f"/fetch/news?query={q}&page_size={max_res}"
            else:
                fetch_url = f"/fetch/{src}?query={q}&max_results={max_res}"
            with st.spinner(f"Fetching from {src.upper()} node..."):
                resp = api("GET", fetch_url)
            if resp and resp.status_code == 200:
                results = resp.json().get("results", [])
                if not results:
                    st.warning("⚠️ No results found. Try a different query.")
                else:
                    st.success(f"✅ {len(results)} records retrieved from {src.upper()}")
                    st.markdown("<br>", unsafe_allow_html=True)

                    # Build preview DF
                    rows = []
                    for item in results:
                        rows.append({
                            "Title": item.get("title", ""),
                            "Summary": (item.get("summary") or item.get("description") or "")[:120] + "...",
                            "URL": item.get("url") or item.get("id") or ""
                        })
                    preview_df = pd.DataFrame(rows)
                    st.dataframe(preview_df, use_container_width=True, hide_index=True)

                    # Detailed cards
                    for i, item in enumerate(results):
                        with st.expander(f"📰 {item.get('title','Unknown')}"):
                            content = item.get("summary") or item.get("description") or ""
                            st.write(content)
                            url = item.get("url") or item.get("id")
                            if url:
                                st.markdown(f"🔗 [View Full Article]({url})")

                    st.divider()
                    # Save to vault
                    if st.button("💾 SAVE ALL TO VAULT", use_container_width=True):
                        all_content = "\n\n".join([
                            f"=== {r.get('title','')} ===\n{r.get('summary') or r.get('description','')}"
                            for r in results
                        ])
                        save_resp = api("POST", "/datasets/save-text",
                                       json={"content": all_content, "filename": f"{src}_{q[:20]}.txt"})
                        if save_resp and save_resp.status_code in (200, 201):
                            st.success("✅ Saved to Vault!")
                        else:
                            # fallback: offer download
                            st.download_button(
                                "⬇  Download as TXT",
                                data=all_content.encode("utf-8"),
                                file_name=f"{src}_{q[:20]}.txt",
                                mime="text/plain",
                                use_container_width=True
                            )
            else:
                show_err(resp)

# PAGE: PROFILE
# ══════════════════════════════════════════════════════════════════════════════
elif page == "profile":
    hdr("👤 User Profile", "Manage your Fusion Graph operative profile")

    resp = api("GET", "/auth/profile")
    profile = (resp.json().get("profile", {}) if resp and resp.status_code == 200 else {})

    col_a, col_b = st.columns([1, 2])
    with col_a:
        st.markdown(f"""
        <div style='background:#000f00;border:1px solid #00ff4140;border-radius:4px;padding:24px;text-align:center;'>
          <div style='font-size:56px;'>👤</div>
          <div style='color:#00ff41;font-family:Orbitron,monospace;font-size:16px;margin-top:10px;letter-spacing:2px;'>
            {user.get('username', 'SECURE_ADMIN').upper()}
          </div>
          <div style='color:#00ff4160;font-size:11px;margin-top:4px;'>
            {user.get('email','N/A')}
          </div>
          <div style='margin-top:12px;'>
            <span style='background:#00ff4120;border:1px solid #00ff4150;color:#00ff41;font-size:10px;
              padding:3px 10px;border-radius:2px;letter-spacing:1px;text-transform:uppercase;'>
              {user.get('role','user')} clearance
            </span>
          </div>
        </div>""", unsafe_allow_html=True)

    with col_b:
        st.markdown("<div style='color:#00ff4180;font-size:11px;letter-spacing:2px;margin-bottom:10px;'>UPDATE INTERESTS</div>", unsafe_allow_html=True)
        current_interests = profile.get("interests", [])
        if isinstance(current_interests, str):
            try:
                current_interests = json.loads(current_interests)
            except Exception:
                current_interests = []

        interest_options = [
            "AI Security", "Malware Analysis", "Threat Intelligence",
            "Network Intrusion", "Cryptography", "Phishing Detection",
            "Zero-Day Exploits", "Forensics", "Quantum Computing",
            "NLP & Text Mining", "Knowledge Graphs", "Data Science"
        ]
        selected = st.multiselect(
            "RESEARCH INTERESTS",
            options=interest_options,
            default=[i for i in current_interests if i in interest_options]
        )

        bio = st.text_area(
            "BIO / NOTES",
            value=profile.get("preferences", ""),
            placeholder="Brief description of your research focus...",
            height=80
        )

        if st.button("💾 SAVE PROFILE", use_container_width=True):
            resp = api("POST", "/auth/profile/interests",
                       json={"interests": selected, "preferences": bio})
            if resp and resp.status_code == 200:
                st.success("✅ Profile updated!")
            else:
                show_err(resp)

    st.divider()
    # Account stats
    vault_resp = api("GET", "/datasets/")
    vault_count = len(vault_resp.json().get("datasets", [])) if vault_resp and vault_resp.status_code == 200 else 0
    card_row([
        ("📦", "Vault Datasets",   str(vault_count),   "#00ff41"),
        ("🕸️", "Graphs Built",    "—",                "#00cfff"),
        ("🌐", "Fetches Done",    "—",                "#ffd700"),
    ])
