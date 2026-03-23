"""
Data-fetch routes — pull live data from external sources (JWT-protected)
GET /api/fetch/wikipedia?query=<term>&sentences=5
GET /api/fetch/arxiv?query=<term>&max_results=10
GET /api/fetch/news?query=<term>&page_size=10
"""
import requests
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required

fetch_bp = Blueprint("fetch", __name__, url_prefix="/api/fetch")

ARXIV_BASE  = "http://export.arxiv.org/api/query"
WIKI_BASE   = "https://en.wikipedia.org/api/rest_v1/page/summary"
WIKI_SEARCH = "https://en.wikipedia.org/w/api.php"
NEWS_BASE   = "https://newsapi.org/v2/everything"


# ── WIKIPEDIA ─────────────────────────────────────────────────────────────────
@fetch_bp.route("/wikipedia", methods=["GET"])
@jwt_required()
def fetch_wikipedia():
    query    = request.args.get("query", "").strip()
    max_hits = int(request.args.get("max_results", 5))
    if not query:
        return jsonify({"error": "query parameter is required"}), 400

    try:
        # first get page suggestions
        search_resp = requests.get(
            WIKI_SEARCH,
            params={
                "action": "opensearch",
                "search": query,
                "limit":  max_hits,
                "format": "json",
            },
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"},
            timeout=20,
        )
        search_resp.raise_for_status()
        titles, urls = search_resp.json()[1], search_resp.json()[3]

        results = []
        for title, url in zip(titles, urls):
            # get summary for each page
            try:
                r = requests.get(
                    f"{WIKI_BASE}/{requests.utils.quote(title)}",
                    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"},
                    timeout=15,
                )
                if r.status_code == 200:
                    data = r.json()
                    results.append({
                        "title":   data.get("title", title),
                        "summary": data.get("extract", ""),
                        "url":     data.get("content_urls", {}).get("desktop", {}).get("page", url),
                        "image":   (data.get("thumbnail") or {}).get("source", ""),
                    })
            except Exception:
                continue

        return jsonify({"source": "wikipedia", "query": query, "results": results}), 200

    except requests.exceptions.HTTPError as e:
        return jsonify({"error": str(e)}), e.response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── ARXIV ─────────────────────────────────────────────────────────────────────
@fetch_bp.route("/arxiv", methods=["GET"])
@jwt_required()
def fetch_arxiv():
    query       = request.args.get("query", "").strip()
    max_results = int(request.args.get("max_results", 10))
    if not query:
        return jsonify({"error": "query parameter is required"}), 400

    try:
        params = {
            "search_query": f"all:{query}",
            "start":        0,
            "max_results":  max_results,
            "sortBy":       "submittedDate",
            "sortOrder":    "descending",
        }
        r = requests.get(
            ARXIV_BASE, 
            params=params, 
            headers={"User-Agent": "DataVault/1.0 (contact@datavault.com)"},
            timeout=30
        )
        r.raise_for_status()

        # parse Atom XML
        import xml.etree.ElementTree as ET
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        root    = ET.fromstring(r.text)
        entries = root.findall("atom:entry", ns)

        results = []
        for entry in entries:
            authors = []
            for a in entry.findall("atom:author", ns):
                name_el = a.find("atom:name", ns)
                if name_el is not None and name_el.text:
                    authors.append(name_el.text)
            link = ""
            for lnk in entry.findall("atom:link", ns):
                if lnk.get("type") == "text/html":
                    link = lnk.get("href", "")
                    break

            title_el = entry.find("atom:title", ns)
            sum_el   = entry.find("atom:summary", ns)
            pub_el   = entry.find("atom:published", ns)
            id_el    = entry.find("atom:id", ns)

            results.append({
                "title":     (title_el.text or "").strip() if title_el is not None else "Untitled",
                "summary":   (sum_el.text or "").strip() if sum_el is not None else "No summary",
                "authors":   authors,
                "published": (pub_el.text or "")[:10] if pub_el is not None else "Unknown",
                "url":       link,
                "id":        (id_el.text or "").strip() if id_el is not None else "",
            })

        return jsonify({"source": "arxiv", "query": query, "results": results}), 200

    except requests.exceptions.HTTPError as e:
        return jsonify({"error": str(e)}), e.response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── NEWS ──────────────────────────────────────────────────────────────────────
@fetch_bp.route("/news", methods=["GET"])
@jwt_required()
def fetch_news():
    query     = request.args.get("query", "").strip()
    page_size = int(request.args.get("page_size", 10))
    if not query:
        return jsonify({"error": "query parameter is required"}), 400

    api_key = current_app.config.get("NEWS_API_KEY", "")
    if not api_key:
        return jsonify({
            "error": "NEWS_API_KEY not configured. Get a free key at https://newsapi.org"
        }), 503

    try:
        r = requests.get(
            NEWS_BASE,
            params={
                "q":        query,
                "pageSize": page_size,
                "language": "en",
                "sortBy":   "publishedAt",
                "apiKey":   api_key,
            },
            headers={"User-Agent": "DataVault/1.0 (contact@datavault.com)"},
            timeout=25,
        )
        r.raise_for_status()
        data     = r.json()
        articles = data.get("articles", [])

        results = [
            {
                "title":       a.get("title", ""),
                "description": a.get("description", ""),
                "source":      (a.get("source") or {}).get("name", ""),
                "url":         a.get("url", ""),
                "image":       a.get("urlToImage", ""),
                "published_at":a.get("publishedAt", "")[:10],
            }
            for a in articles
            if a.get("title") and "[Removed]" not in a.get("title", "")
        ]

        return jsonify({
            "source":       "news",
            "query":        query,
            "total_results": data.get("totalResults", 0),
            "results":      results,
        }), 200

    except requests.exceptions.HTTPError as e:
        return jsonify({"error": str(e)}), e.response.status_code
    except requests.exceptions.ReadTimeout:
        return jsonify({"error": "Upstream source timed out. The intelligence node is responding slowly."}), 504
    except Exception as e:
        return jsonify({"error": str(e)}), 500
