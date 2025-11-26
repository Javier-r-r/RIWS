from typing import Optional, List, Dict, Any
import os
import json
from pathlib import Path
import sys

# Ensure the repository root is on sys.path so sibling packages like index_tools
# can be imported when running uvicorn from the `api/` directory.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from elasticsearch import Elasticsearch

app = FastAPI(title="Scuffers Search API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ES_HOST = os.environ.get("ES_HOST", "http://localhost:9200")
INDEX = os.environ.get("ES_INDEX", "scuffers_products")

es = Elasticsearch(hosts=[ES_HOST])


def es_available() -> bool:
    try:
        return es.ping()
    except Exception:
        return False


def build_es_body(q: Optional[str], min_price: Optional[float], max_price: Optional[float], size: Optional[str], color: Optional[str], page: int, per_page: int, sort: Optional[str]) -> Dict[str, Any]:
    must = []
    filters = []

    if q:
        must.append({
            "multi_match": {
                "query": q,
                "fields": ["title^3", "title.autocomplete", "description", "sku"],
                "type": "best_fields",
            }
        })
    else:
        must.append({"match_all": {}})

    if min_price is not None or max_price is not None:
        rng = {}
        if min_price is not None:
            rng["gte"] = min_price
        if max_price is not None:
            rng["lte"] = max_price
        filters.append({"range": {"price": rng}})

    if size:
        filters.append({"term": {"sizes": size}})

    if color:
        # color is stored as keyword, lowercase
        filters.append({"term": {"color": color.lower()}})

    body = {
        "query": {"bool": {"must": must, "filter": filters}},
        "from": (page - 1) * per_page,
        "size": per_page,
        "aggs": {
            "sizes": {"terms": {"field": "sizes"}},
            "price_stats": {"stats": {"field": "price"}},
            "colors": {"terms": {"field": "color"}}
        },
    }

    if sort == "price_asc":
        body["sort"] = [{"price": {"order": "asc"}}]
    elif sort == "price_desc":
        body["sort"] = [{"price": {"order": "desc"}}]

    return body


def load_json_fallback() -> List[Dict[str, Any]]:
    p = Path(__file__).resolve().parents[1] / "scuffers_output.json"
    if not p.exists():
        return []
    try:
        with p.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


from index_tools.color_utils import infer_color_from_url


def fallback_search(docs: List[Dict[str, Any]], q: Optional[str], min_price: Optional[float], max_price: Optional[float], size: Optional[str], color: Optional[str], page: int, per_page: int, sort: Optional[str]) -> Dict[str, Any]:
    def matches_text(item: Dict[str, Any], qstr: str) -> bool:
        ql = qstr.lower()
        for f in ("title", "description", "sku"):
            v = item.get(f) or ""
            if isinstance(v, list):
                v = " ".join(v)
            if isinstance(v, (int, float)):
                v = str(v)
            if ql in str(v).lower():
                return True
        return False

    filtered = []
    for item in docs:
        if q and not matches_text(item, q):
            continue
        # color filter: try item['color'] first, otherwise infer from URL
        if color:
            item_color = (item.get('color') or '').lower()
            if not item_color or item_color == 'unknown':
                item_color = infer_color_from_url(item.get('url') or '').lower()
            if item_color != color.lower():
                continue
        price = item.get("price")
        try:
            price_val = float(price) if price is not None else None
        except Exception:
            price_val = None
        if min_price is not None and (price_val is None or price_val < min_price):
            continue
        if max_price is not None and (price_val is None or price_val > max_price):
            continue
        if size:
            sizes = item.get("sizes") or []
            if isinstance(sizes, str):
                sizes = [s.strip() for s in sizes.split(",") if s.strip()]
            if size not in sizes:
                continue
        filtered.append(item)

    total = len(filtered)

    if sort == "price_asc":
        filtered.sort(key=lambda d: (float(d.get("price") or 0) if d.get("price") is not None else float("inf")))
    elif sort == "price_desc":
        filtered.sort(key=lambda d: (float(d.get("price") or 0) if d.get("price") is not None else -float("inf")), reverse=True)

    start = (page - 1) * per_page
    end = start + per_page
    hits = filtered[start:end]

    sizes_count: Dict[str, int] = {}
    prices = []
    for d in filtered:
        for s in (d.get("sizes") or []):
            sizes_count[s] = sizes_count.get(s, 0) + 1
        try:
            pval = float(d.get("price"))
            prices.append(pval)
        except Exception:
            pass

    # color aggregation over filtered docs
    colors_count: Dict[str, int] = {}
    for d in filtered:
        c = (d.get('color') or '').lower()
        if not c or c == 'unknown':
            c = infer_color_from_url(d.get('url') or '').lower()
        colors_count[c] = colors_count.get(c, 0) + 1

    aggs: Dict[str, Any] = {}
    aggs["sizes"] = {"buckets": [{"key": k, "doc_count": v} for k, v in sizes_count.items()]}
    aggs["colors"] = {"buckets": [{"key": k, "doc_count": v} for k, v in colors_count.items()]}
    if prices:
        aggs["price_stats"] = {"min": min(prices), "max": max(prices), "avg": sum(prices) / len(prices), "count": len(prices)}
    else:
        aggs["price_stats"] = {"min": None, "max": None, "avg": None, "count": 0}

    return {"total": total, "hits": hits, "aggs": aggs}


@app.get("/search")
def search(
    q: Optional[str] = Query(None),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    size: Optional[str] = Query(None),
    color: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    sort: Optional[str] = Query(None),
):
    if es_available():
        body = build_es_body(q, min_price, max_price, size, color, page, per_page, sort)
        try:
            resp = es.search(index=INDEX, body=body)
            hits = [h["_source"] for h in resp["hits"]["hits"]]
            total = resp["hits"]["total"]["value"] if isinstance(resp["hits"]["total"], dict) else resp["hits"]["total"]
            aggs = resp.get("aggregations", {})
            return {"total": total, "page": page, "per_page": per_page, "hits": hits, "aggregations": aggs, "es": True}
        except Exception as e:
            docs = load_json_fallback()
            res = fallback_search(docs, q, min_price, max_price, size, color, page, per_page, sort)
            return {"total": res["total"], "page": page, "per_page": per_page, "hits": res["hits"], "aggregations": res["aggs"], "es": False, "error": str(e)}
    else:
        docs = load_json_fallback()
        res = fallback_search(docs, q, min_price, max_price, size, color, page, per_page, sort)
        return {"total": res["total"], "page": page, "per_page": per_page, "hits": res["hits"], "aggregations": res["aggs"], "es": False}
