# sentinel-embed-chat (local)

Kurzanleitung:

1. Baue das Image:

```bash
cd sentinel/sentinel-embed-chat/app
docker build -t sentinel-embed-chat:latest .
```

2. Starte Qdrant (siehe sentinel/qdrant/docker-compose.yml) und setze `OPENAI_API_KEY` als ENV.

3. Ingest Beispiel:

```bash
docker run --rm -e OPENAI_API_KEY="$OPENAI_API_KEY" -e QDRANT_URL="http://host.docker.internal:6333" sentinel-embed-chat:latest python sentinel_agent.py ingest "DevOps Grundlagen"
```

4. Starte interaktiven Chat:

```bash
docker run --rm -it -e OPENAI_API_KEY="$OPENAI_API_KEY" -e QDRANT_URL="http://host.docker.internal:6333" sentinel-embed-chat:latest
```

Sicherheits-Hinweis: Blockwörter werden erkannt und geblockt.
