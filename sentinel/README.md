# Sentinel — setup for secrets and local run

This folder contains templates and helpers to safely manage your OpenAI API key for the Sentinel project.

Important: NEVER commit your real API key to git. Use `.env` locally (gitignored) and provide secrets to Kubernetes with the helper script.

1) Create a local `.env` from the template:

```bash
cd sentinel
cp .env.example .env
# Edit .env and set OPENAI_API_KEY to your private key
```

2) Prevent accidental commit

`.gitignore` in this folder already ignores `.env`. Ensure your root `.gitignore` also excludes any local secret files.

3) Create Kubernetes Secret

Use the helper script to create/update the `secret-openai` in your cluster (default namespace):

```bash
cd sentinel
chmod +x scripts/create_k8s_secret.sh
./scripts/create_k8s_secret.sh default
```

4) Verify

```bash
kubectl get secret secret-openai -n default -o yaml
# decode locally (do not paste public):
kubectl get secret secret-openai -n default -o jsonpath="{.data.OPENAI_API_KEY}" | base64 --decode && echo
```

5) Usage

- Docker run: `-e OPENAI_API_KEY="$OPENAI_API_KEY"` or `--env-file .env`.
- Docker Compose: use `.env` in compose folder (do NOT commit `.env`).
- Kubernetes: Deployments provided reference `envFrom: secretRef: { name: secret-openai }`.
