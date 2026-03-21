# sentinel-alerts-api

Kurzanleitung:

1. Baue das Docker Image:

```bash
cd sentinel/sentinel-alerts-api/app
docker build -t sentinel-alerts-api:latest .
```

2. Starte den Container gegen Qdrant:

```bash
docker run --rm -p 8080:8080 -e OPENAI_API_KEY="$OPENAI_API_KEY" -e QDRANT_URL="http://host.docker.internal:6333" sentinel-alerts-api:latest
```

3. Test:

```bash
curl -s http://localhost:8080/health
curl -s -X POST http://localhost:8080/analyze -H "Content-Type: application/json" -d '{"logline":"NodeNotReady detected"}' | jq
```
