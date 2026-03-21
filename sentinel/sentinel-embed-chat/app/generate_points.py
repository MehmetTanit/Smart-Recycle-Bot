import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime, timezone
from openai import OpenAI

ROOT = Path(__file__).resolve().parents[2]  # sentinel/
DATA_FILE = ROOT / 'data' / 'items.json'
OUT_DIR = ROOT / 'output'
OUT_DIR_3A = Path(__file__).resolve().parents[4] / '3_Aufgabe' / 'output'

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
EMBED_MODEL = os.environ.get('EMBED_MODEL', 'text-embedding-3-small')

def _now_iso():
    return datetime.now(timezone.utc).isoformat()

def load_items():
    if not DATA_FILE.exists():
        print(f"Error: data file not found: {DATA_FILE}")
        sys.exit(2)
    return json.loads(DATA_FILE.read_text(encoding='utf-8'))

def embed_texts(client, texts):
    resp = client.embeddings.create(model=EMBED_MODEL, input=texts)
    return [d.embedding for d in resp.data]

def make_points(items):
    client = OpenAI(api_key=OPENAI_API_KEY)
    contents = [it.get('content','') for it in items]
    vectors = embed_texts(client, contents)
    created_at = _now_iso()
    doc_id = f"doc-smart-recycle-{int(time.time())}"
    points = []
    base = int(time.time()*1000)
    for i, (it, vec) in enumerate(zip(items, vectors), start=1):
        pid = base + i
        payload = {
            'title': it.get('title',''),
            'content': it.get('content',''),
            'tags': it.get('tags', []),
            'category': it.get('category',''),
            'source': 'dummy:items',
            'doc_id': doc_id,
            'chunk_id': i,
            'chunk_count': len(items),
            'created_at': created_at,
        }
        points.append({'id': pid, 'vector': vec, 'payload': payload})
    return points

def save_points(points):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_DIR_3A.mkdir(parents=True, exist_ok=True)
    data = {'points': points}
    out1 = OUT_DIR / 'points.json'
    out2 = OUT_DIR_3A / 'points.json'
    out1.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    out2.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"Wrote {len(points)} points to: {out1}")
    print(f"Also wrote copy to: {out2}")

def main():
    if not OPENAI_API_KEY:
        print("Error: OPENAI_API_KEY not set in environment. Set it or create .env with OPENAI_API_KEY.")
        sys.exit(1)
    items = load_items()
    print(f"Loaded {len(items)} items, creating embeddings...")
    points = make_points(items)
    save_points(points)
    print("Done.")

if __name__ == '__main__':
    main()
