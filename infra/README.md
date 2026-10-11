# Infrastructure

- **Local dev:** `docker-compose.yml` at the repo root (PostGIS 16-3.4, Redis,
  MinIO, Django backend, Celery worker, Angular dev server).
- **CI:** `.github/workflows/ci.yml` (backend lint + tests on sqlite-fallback
  *and* real PostGIS, frontend build, schema validation).
- **Milestone M4+:** Kubernetes manifests with Agones for UE5 dedicated-server
  orchestration go here. Nothing yet — do not assume K8s is ready.
