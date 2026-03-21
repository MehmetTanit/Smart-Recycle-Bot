import os
import json
from typing import Dict, List
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY","")
QDRANT_URL     = os.environ.get("QDRANT_URL","http://qdrant:6333")
COLLECTION     = os.environ.get("QDRANT_COLLECTION","recycle_docs")
EMBED_MODEL    = os.environ.get("EMBED_MODEL","text-embedding-3-small")
MIN_SCORE      = float(os.environ.get("MIN_SCORE","0.7"))
TOP_K          = int(os.environ.get("TOP_K","5"))

BIN_LABELS: Dict[str, str] = {
    "glass": "Glascontainer",
    "plastic": "Gelber Sack / Wertstoff",
    "bio": "Biotonne",
    "paper": "Papiertonne",
    "metal": "Wertstoffhof / Metallsammlung",
    "hazard": "Schadstoffsammlung",
    "residual": "Restmüll",
    "textile": "Kleiderspende",
    "electronic_waste": "Elektroschrott-Sammelstelle",
}

DUMMY_ITEMS = [
    {"title": "Glasflasche", "content": "Leere Glasflasche für Wasser mit Etikett.", "tags": ["glas", "flasche"], "category": "glass"},
    {"title": "Plastiktüte", "content": "Dünne Plastiktüte vom Einkauf, leicht verschmutzt.", "tags": ["plastik", "tüte"], "category": "plastic"},
    {"title": "Bananenschale", "content": "Organischer Küchenabfall, kompostierbar.", "tags": ["bio", "obst"], "category": "bio"},
    {"title": "Alte Zeitung", "content": "Trockene Zeitung ohne starke Verschmutzung.", "tags": ["papier", "zeitung"], "category": "paper"},
    {"title": "AA-Batterie", "content": "Leere Batterie mit Schadstoffen.", "tags": ["batterie", "problemstoff"], "category": "hazard"},
    {"title": "Konservendose", "content": "Leere Dose aus Metall.", "tags": ["metall", "dose"], "category": "metal"},
    {"title": "Altes Handy", "content": "Defektes Smartphone mit Akku.", "tags": ["elektronik", "gerät"], "category": "electronic_waste"},
    {"title": "Styroporverpackung", "content": "Leichte Verpackung aus Styropor.", "tags": ["styropor", "verpackung"], "category": "residual"},
]

app = FastAPI(title="recycle-api", version="1.0")

class ClassifyRequest(BaseModel):
    item: str

def ensure_collection():
    r = requests.get(f"{QDRANT_URL}/collections/{COLLECTION}", timeout=10)
    if r.status_code == 200:
        return
    body = {"vectors": {"size": 1536, "distance": "Cosine"}}
    create = requests.put(
        f"{QDRANT_URL}/collections/{COLLECTION}",
        headers={"Content-Type": "application/json"},
        data=json.dumps(body),
        timeout=30,
    )
    if create.status_code >= 400:
        raise HTTPException(502, f"Collection-Create fehlgeschlagen: {create.status_code} {create.text}")

def embed_text(client: OpenAI, text: str):
    r = client.embeddings.create(model=EMBED_MODEL, input=[text])
    return r.data[0].embedding

def qdrant_search(vec):
    body = {"vector": vec, "limit": TOP_K, "with_payload": True, "with_vector": False}
    r = requests.post(f"{QDRANT_URL}/collections/{COLLECTION}/points/search",
                      headers={"Content-Type":"application/json"},
                      data=json.dumps(body), timeout=60)
    if r.status_code >= 400:
        raise HTTPException(502, f"Qdrant-Fehler: {r.status_code} {r.text}")
    return r.json().get("result", [])

def upsert_points(points: List[dict]):
    r = requests.put(
        f"{QDRANT_URL}/collections/{COLLECTION}/points?wait=true",
        headers={"Content-Type": "application/json"},
        data=json.dumps({"points": points}),
        timeout=60,
    )
    if r.status_code >= 400:
        raise HTTPException(502, f"Upsert-Fehler: {r.status_code} {r.text}")

def seed_dummy_data_if_needed(client: OpenAI):
    count_resp = requests.post(
        f"{QDRANT_URL}/collections/{COLLECTION}/points/count",
        headers={"Content-Type": "application/json"},
        data=json.dumps({"exact": True}),
        timeout=30,
    )
    if count_resp.status_code >= 400:
        raise HTTPException(502, f"Count-Fehler: {count_resp.status_code} {count_resp.text}")

    count = (count_resp.json().get("result") or {}).get("count", 0)
    if count > 0:
        return

    texts = [f"{it['title']}. {it['content']}" for it in DUMMY_ITEMS]
    vectors = client.embeddings.create(model=EMBED_MODEL, input=texts).data
    points = []
    for idx, (it, vec) in enumerate(zip(DUMMY_ITEMS, vectors), start=1):
        points.append(
            {
                "id": idx,
                "vector": vec.embedding,
                "payload": {
                    "title": it["title"],
                    "content": it["content"],
                    "tags": it["tags"],
                    "category": it["category"],
                    "source": "dummy:smart-recycle",
                },
            }
        )
    upsert_points(points)

@app.get("/health")
def health():
    return {"status":"ok", "service": "recycle-api"}

@app.post("/classify")
def classify(req: ClassifyRequest):
    if not OPENAI_API_KEY:
        raise HTTPException(500, "OPENAI_API_KEY fehlt")

    client = OpenAI(api_key=OPENAI_API_KEY)
    ensure_collection()
    seed_dummy_data_if_needed(client)

    vec = embed_text(client, req.item)
    hits = qdrant_search(vec)
    max_score = hits[0]["score"] if hits else 0.0
    if not hits or max_score < MIN_SCORE:
        return {
            "result": "unknown",
            "bin": None,
            "confidence": round(max_score, 4),
            "message": "Ich weiß es nicht sicher auf Basis der vorhandenen Dummy-Daten.",
        }

    top = hits[0]
    payload = top.get("payload", {}) or {}
    category = payload.get("category", "residual")
    return {
        "result": "classified",
        "item": req.item,
        "category": category,
        "bin": BIN_LABELS.get(category, "Restmüll"),
        "confidence": round(top.get("score", 0.0), 4),
        "matched_example": payload.get("title", ""),
    }
