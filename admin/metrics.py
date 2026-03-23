"""
admin/metrics.py — Graph quality metrics and pipeline statistics.
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import networkx as nx
from db.connection import run_query


def get_pipeline_stats(user_id: int) -> dict:
    """Return counts: datasets, sentences processed, triplets formed."""
    datasets = run_query(
        "SELECT COUNT(*) AS cnt, COALESCE(SUM(row_count),0) AS rows FROM datasets WHERE user_id=%s",
        (user_id,)
    )
    sentences = run_query(
        """SELECT COUNT(ps.id) AS cnt
           FROM processed_sentences ps
           JOIN datasets d ON ps.dataset_id = d.id
           WHERE d.user_id=%s""",
        (user_id,)
    )
    graphs = run_query(
        "SELECT COUNT(*) AS cnt FROM graphs WHERE user_id=%s", (user_id,)
    )
    triplets = run_query(
        """SELECT COUNT(t.id) AS cnt
           FROM triplets t
           JOIN graphs g ON t.graph_id = g.id
           WHERE g.user_id=%s""",
        (user_id,)
    )
    return {
        "datasets":  datasets[0]["cnt"]  if datasets  else 0,
        "sentences": sentences[0]["cnt"] if sentences else 0,
        "graphs":    graphs[0]["cnt"]    if graphs    else 0,
        "triplets":  triplets[0]["cnt"]  if triplets  else 0,
    }


def get_graph_metrics(graph_id: int) -> dict:
    """Connectivity and coverage metrics for a specific saved graph."""
    rows = run_query(
        "SELECT head, relation, tail, domain FROM triplets WHERE graph_id=%s",
        (graph_id,)
    )
    if not rows:
        return {"nodes": 0, "edges": 0, "density": 0, "avg_degree": 0,
                "domain_counts": {}, "coverage_pct": 0}

    G = nx.DiGraph()
    domain_counts: dict[str, int] = {}
    for r in rows:
        G.add_edge(r["head"], r["tail"], relation=r["relation"])
        d = r.get("domain", "General")
        domain_counts[d] = domain_counts.get(d, 0) + 1

    n = G.number_of_nodes()
    e = G.number_of_edges()
    avg_deg = round(sum(dict(G.degree()).values()) / n, 2) if n else 0
    max_possible = n * (n - 1)
    coverage_pct = round(100 * e / max_possible, 2) if max_possible else 0

    return {
        "nodes": n,
        "edges": e,
        "density": round(nx.density(G), 4),
        "avg_degree": avg_deg,
        "domain_counts": domain_counts,
        "coverage_pct": coverage_pct,
    }


def get_all_users() -> list[dict]:
    """List all users (admin use)."""
    return run_query(
        "SELECT id, username, email, role, created_at FROM users ORDER BY created_at DESC"
    )


def get_all_datasets() -> list[dict]:
    """List all datasets across all users (admin use)."""
    return run_query(
        """SELECT d.id, d.name, d.source_type, d.row_count, d.created_at,
                  u.username
           FROM datasets d
           JOIN users u ON d.user_id = u.id
           ORDER BY d.created_at DESC"""
    )


def log_admin_action(user_id: int, action: str, details: str = ""):
    """Write an admin action to the log table."""
    from db.connection import run_insert
    run_insert(
        "INSERT INTO admin_logs (user_id, action, details) VALUES (%s,%s,%s)",
        (user_id, action, details)
    )


def get_admin_logs(limit: int = 50) -> list[dict]:
    """Fetch recent admin log entries."""
    return run_query(
        """SELECT al.id, u.username, al.action, al.details, al.created_at
           FROM admin_logs al LEFT JOIN users u ON al.user_id = u.id
           ORDER BY al.created_at DESC LIMIT %s""",
        (limit,)
    )
