"""
Graph routes — build knowledge graphs from vault datasets using NetworkX + PyVis
POST /api/graph/build
GET  /api/graph/list
"""
import os
import json
import pandas as pd

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.extensions import db
from backend.models import Dataset, User

graph_bp = Blueprint("graph", __name__, url_prefix="/api/graph")


def _get_user(uid_str):
    return db.session.get(User, int(uid_str))


def _load_dataset_df(ds: Dataset) -> pd.DataFrame:
    """Load a Dataset record into a DataFrame."""
    fpath = os.path.join(current_app.config["UPLOAD_FOLDER"], ds.stored_name)
    ext = os.path.splitext(ds.stored_name)[1].lower()
    if ext == ".csv":
        return pd.read_csv(fpath)
    elif ext == ".json":
        return pd.read_json(fpath)
    elif ext in (".xls", ".xlsx"):
        return pd.read_excel(fpath)
    else:  # txt, own, etc.
        with open(fpath, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
        return pd.DataFrame({"text_content": lines})


def _build_graph_html(nodes, edges, title="FUSION GRAPH — Knowledge Network"):
    """Return a self-contained HTML string with a D3 / vanilla JS force graph."""
    nodes_json = json.dumps(nodes[:300])  # cap at 300 for performance
    edges_json = json.dumps(edges[:500])

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body {{ margin:0; background:#050a05; overflow:hidden; font-family:'Share Tech Mono',monospace; }}
  svg {{ width:100%; height:100vh; }}
  .node circle {{ stroke:#00ff41; stroke-width:2px; fill:#001a00; cursor:pointer; }}
  .node circle:hover {{ fill:#00ff4130; }}
  .node text {{ fill:#00ff41; font-size:10px; pointer-events:none; }}
  .link {{ stroke:#00ff4140; stroke-width:1px; }}
  .tooltip {{
    position:absolute; background:#000f00; border:1px solid #00ff4160;
    color:#00ff41; padding:6px 10px; font-size:11px; border-radius:2px;
    pointer-events:none; display:none; max-width:220px;
  }}
  #info {{ position:absolute; top:10px; right:10px; color:#00ff4180; font-size:11px; letter-spacing:1px; }}
</style>
</head>
<body>
<div id="info">NODES: {len(nodes)} &nbsp;|&nbsp; EDGES: {len(edges)}</div>
<div class="tooltip" id="tooltip"></div>
<svg id="graph"></svg>
<script src="https://d3js.org/d3.v7.min.js"></script>
<script>
const nodes = {nodes_json};
const links = {edges_json};

const svg  = d3.select("#graph");
const W    = window.innerWidth;
const H    = window.innerHeight;
svg.attr("viewBox", [0, 0, W, H]);

const tip = document.getElementById("tooltip");

const sim = d3.forceSimulation(nodes)
  .force("link",   d3.forceLink(links).id(d => d.id).distance(80))
  .force("charge", d3.forceManyBody().strength(-120))
  .force("center", d3.forceCenter(W/2, H/2))
  .force("collision", d3.forceCollide(28));

const link = svg.append("g")
  .selectAll("line")
  .data(links).join("line").attr("class","link");

const node = svg.append("g")
  .selectAll("g")
  .data(nodes).join("g").attr("class","node")
  .call(d3.drag()
    .on("start", (e,d) => {{ if(!e.active) sim.alphaTarget(0.3).restart(); d.fx=d.x; d.fy=d.y; }})
    .on("drag",  (e,d) => {{ d.fx=e.x; d.fy=e.y; }})
    .on("end",   (e,d) => {{ if(!e.active) sim.alphaTarget(0); d.fx=null; d.fy=null; }}));

const colorMap = {{ entity:"#00ff41", keyword:"#00cfff", concept:"#ffd700", default:"#ff6bff" }};

node.append("circle")
  .attr("r", d => d.size || 12)
  .style("fill", d => (colorMap[d.type] || colorMap.default) + "20")
  .style("stroke", d => colorMap[d.type] || colorMap.default)
  .on("mouseover", (e,d) => {{
    tip.style.display="block";
    tip.innerHTML = "<b>" + d.label + "</b><br>Type: " + (d.type||"node") + "<br>Degree: " + (d.degree||0);
  }})
  .on("mousemove", e => {{
    tip.style.left = (e.pageX+12)+"px";
    tip.style.top  = (e.pageY-28)+"px";
  }})
  .on("mouseout", () => tip.style.display="none");

node.append("text")
  .attr("dx", 14).attr("dy", 4)
  .style("fill", d => colorMap[d.type] || colorMap.default)
  .text(d => d.label.substring(0,22));

sim.on("tick", () => {{
  link
    .attr("x1", d=>d.source.x).attr("y1", d=>d.source.y)
    .attr("x2", d=>d.target.x).attr("y2", d=>d.target.y);
  node.attr("transform", d=>`translate(${{d.x}},${{d.y}})`);
}});
</script>
</body>
</html>"""
    return html


# ── BUILD ──────────────────────────────────────────────────────────────────────
@graph_bp.route("/build", methods=["POST"])
@jwt_required()
def build_graph():
    user = _get_user(get_jwt_identity())
    if not user:
        return jsonify({"error": "User not found"}), 404

    data       = request.get_json(silent=True) or {}
    dataset_id = data.get("dataset_id")
    keywords   = [k.lower().strip() for k in data.get("keywords", []) if k.strip()]
    max_nodes  = min(int(data.get("max_nodes", 80)), 300)

    ds = db.session.get(Dataset, dataset_id)
    if not ds or ds.user_id != user.id:
        return jsonify({"error": "Dataset not found"}), 404

    # ── Load data ──────────────────────────────────────────────────────────────
    try:
        df = _load_dataset_df(ds)
    except Exception as e:
        return jsonify({"error": f"Cannot load dataset: {e}"}), 422

    # ── Extract candidate terms ────────────────────────────────────────────────
    # Combine all text columns into one big string pool
    text_pool = []
    for col in df.columns:
        if df[col].dtype == object:
            text_pool.extend(df[col].dropna().astype(str).tolist())
        else:
            # numeric column — use the column NAME as a concept
            text_pool.append(col)

    # Tokenize to words
    import re
    all_words = []
    for chunk in text_pool[:2000]:   # cap input for speed
        words = re.findall(r"[A-Za-z][a-z]{2,}", chunk)
        all_words.extend([w.lower() for w in words])

    # Frequency count
    from collections import Counter
    STOPWORDS = {
        "the","and","for","are","was","were","has","have","with","this","that","from","they",
        "will","can","not","but","all","its","more","been","their","which","when","what",
        "also","then","than","into","out","our","had","about","your","use","used","other",
        "data","type","none","true","false","null","nan","http","https","com","www"
    }
    freq = Counter(w for w in all_words if w not in STOPWORDS and len(w) > 3)

    # Top terms become nodes
    top_terms = [word for word, _ in freq.most_common(max_nodes)]

    # If keywords provided, prioritise any that appear
    if keywords:
        kw_in = [k for k in keywords if k in freq]
        top_terms = list(dict.fromkeys(kw_in + top_terms))[:max_nodes]

    if not top_terms:
        return jsonify({"error": "No terms extracted from dataset. Try a text-heavy file."}), 422

    # ── Build nodes ────────────────────────────────────────────────────────────
    # Assign categories based on term patterns
    CYBER_TERMS  = {"malware","phishing","ransomware","exploit","vulnerability","attack","intrusion",
                    "breach","threat","virus","worm","trojan","backdoor","payload","injection","zero","day"}
    AI_TERMS     = {"model","neural","learning","training","classification","prediction","algorithm",
                    "feature","embedding","token","transformer","bert","gpt","accuracy"}
    NET_TERMS    = {"network","packet","protocol","traffic","firewall","router","port","https","tcp",
                    "udp","ip","dns","ssl","tls","certificate","endpoint"}

    def _type(word):
        if word in CYBER_TERMS: return "entity"
        if word in AI_TERMS:    return "keyword"
        if word in NET_TERMS:   return "concept"
        return "default"

    nodes = []
    for i, term in enumerate(top_terms):
        nodes.append({
            "id":     i,
            "label":  term,
            "type":   _type(term),
            "size":   max(8, min(24, freq.get(term, 1) // 2 + 8)),
            "degree": 0
        })
    term_idx = {t: i for i, t in enumerate(top_terms)}

    # ── Build edges by co-occurrence within sentences ──────────────────────────
    edges = []
    edge_set = set()
    for chunk in text_pool[:500]:
        words_in_chunk = list(set(
            re.findall(r"[A-Za-z][a-z]{2,}", chunk.lower())
        ))
        present = [w for w in words_in_chunk if w in term_idx]
        for a_idx in range(len(present)):
            for b_idx in range(a_idx + 1, min(a_idx + 4, len(present))):
                a, b = present[a_idx], present[b_idx]
                key  = tuple(sorted([a, b]))
                if key not in edge_set and len(edges) < 500:
                    edge_set.add(key)
                    ai, bi = term_idx[a], term_idx[b]
                    edges.append({"source": ai, "target": bi, "weight": 1})
                    nodes[ai]["degree"] = nodes[ai].get("degree", 0) + 1
                    nodes[bi]["degree"] = nodes[bi].get("degree", 0) + 1

    # ── Generate HTML graph ────────────────────────────────────────────────────
    html = _build_graph_html(nodes, edges, title=ds.original_name)

    return jsonify({
        "nodes":       nodes,
        "edges":       edges,
        "html":        html,
        "node_count":  len(nodes),
        "edge_count":  len(edges),
        "dataset":     ds.original_name,
    }), 200


# ── LIST saved graphs ──────────────────────────────────────────────────────────
@graph_bp.route("/list", methods=["GET"])
@jwt_required()
def list_graphs():
    user = _get_user(get_jwt_identity())
    if not user:
        return jsonify({"error": "User not found"}), 404
    profile = user.profile
    if not profile:
        return jsonify({"graphs": []}), 200
    try:
        graphs = json.loads(profile.saved_graphs or "[]")
    except Exception:
        graphs = []
    return jsonify({"graphs": graphs}), 200
