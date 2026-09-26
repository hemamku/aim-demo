# Deployment Steps

## Security Note (read first)
Your `.env` file contains a live `WEAVIATE_API_KEY` in plaintext. If this file was ever committed to git or shared, rotate the key in the Weaviate Cloud console immediately, and ensure `.env` is listed in `.gitignore`. Never bake secrets into images or pass them with `--set-env-vars` on Cloud Run — use `--set-secrets` with Secret Manager (shown below).

---

## 1. Deploy the Phoenix observability server (phoenix-demo/)

Uses `phoenix-demo/Dockerfile`, which runs `phoenix-demo/phoenix_server.py`.

```powershell
$PROJECT_ID = "upsproj"
$REGION = "us-central1"

# One-time: allow Cloud Build's default SA to build/push and read build sources
$BUILD_SA = "1044850812012-compute@developer.gserviceaccount.com"
gcloud projects add-iam-policy-binding $PROJECT_ID `
  --member="serviceAccount:$BUILD_SA" --role="roles/run.builder"
gcloud storage buckets add-iam-policy-binding `
  "gs://run-sources-$PROJECT_ID-$REGION" `
  --member="serviceAccount:$BUILD_SA" --role="roles/storage.objectViewer"

# Build + deploy from source
gcloud run deploy phoenix-demo `
  --source .\phoenix-demo `
  --region $REGION `
  --allow-unauthenticated `
  --memory 2Gi `
  --min-instances 1 `
  --max-instances 1
```

Note the returned service URL (e.g. `https://phoenix-demo-xxxxx-uc.a.run.app`). You'll point the RAG app's tracing at `<that-url>/v1/traces`.

---

## 2. Deploy the Vertex RAG agent (Streamlit app + vertex_rag_agent.py)

The root `Dockerfile` runs `streamlit_app.py`, which imports and calls the ADK agent in `vertex_rag_agent.py`.

### a. Store secrets in Secret Manager (once)
```powershell
"SmQ2T2k1K1BXbEJqbHB6QV9ZYzBxd2hacnBCcGRTb2VqZVBpUlRIbFVGS2p4MitzMUFldVVUZE1FcElZPV92MjAw" | gcloud secrets create weaviate-api-key --data-file=-
```

### b. Grant the Cloud Run runtime service account access to the secret
```powershell
$PROJECT_NUMBER = (gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
gcloud secrets add-iam-policy-binding weaviate-api-key `
  --member="serviceAccount:$PROJECT_NUMBER-compute@developer.gserviceaccount.com" `
  --role="roles/secretmanager.secretAccessor"
```

### c. Grant Vertex AI access to that same runtime service account
```powershell
gcloud projects add-iam-policy-binding $PROJECT_ID `
  --member="serviceAccount:$PROJECT_NUMBER-compute@developer.gserviceaccount.com" `
  --role="roles/aiplatform.user"
```

### d. Deploy
```powershell
gcloud run deploy vertex-rag-agent `
  --source . `
  --region $REGION `
  --allow-unauthenticated `
  --memory 2Gi `
  --cpu 2 `
  --timeout 300 `
  --set-env-vars "GOOGLE_CLOUD_PROJECT=$PROJECT_ID,GOOGLE_CLOUD_LOCATION=$REGION,GOOGLE_GENAI_USE_VERTEXAI=true,WEAVIATE_URL=https://ihjvkr8tziluzqsixfra.c0.eu-central-1.aws.weaviate.cloud" `
  --set-secrets "WEAVIATE_API_KEY=weaviate-api-key:latest"
```

`--source .` uses the same Cloud Build/Cloud Run source-deploy flow as the Phoenix service, applying the root `Dockerfile`, which listens on `$PORT` (8080) as Cloud Run expects.

### e. (Optional) Wire up tracing to the Phoenix Cloud Run URL
Set the OTLP endpoint env var read by `observability.py` to:
```
https://phoenix-demo-xxxxx-uc.a.run.app/v1/traces
```
instead of `localhost:6006`, so traces from the deployed RAG app land in the deployed Phoenix dashboard.

---

## Local reference commands (from .env)

```powershell
$env:GOOGLE_CLOUD_PROJECT="upsproj"
$env:GOOGLE_CLOUD_LOCATION="us-central1"
$env:GOOGLE_GENAI_USE_VERTEXAI="true"
$env:WEAVIATE_API_KEY = "<your-weaviate-api-key>"
$env:WEAVIATE_URL = "https://ihjvkr8tziluzqsixfra.c0.eu-central-1.aws.weaviate.cloud"

pip install "sentence-transformers==3.4.1"
pip install "huggingface_hub==0.36.2" --force-reinstall --no-deps
python -c "from huggingface_hub import snapshot_download; print(snapshot_download('sentence-transformers/all-MiniLM-L6-v2', local_dir='models/all-MiniLM-L6-v2'))"

$env:PYTHONPATH="C:\Users\HEMA\OneDrive\Documents\RAG_deployment"
python weaviate_ingest.py --docs-dir docs --collection document_knowledge --weaviate-url $env:WEAVIATE_URL --weaviate-api-key $env:WEAVIATE_API_KEY
```
