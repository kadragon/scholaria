# Scholaria Admin Guide (FastAPI + Refine)

This guide explains how to operate the Scholaria administration panel after the migration to FastAPI and the Refine-based UI. It replaces the legacy Django admin workflow.

## Getting Started

1. Deploy the latest stack (`backend`, `frontend`, optional `nginx`) using the production Docker configuration.
2. Open the admin panel at `https://<your-domain>/admin/` (development: `http://localhost:4173/` if using Vite dev server).
3. Authenticate with your administrator credentials created via the Auth API (`POST /api/auth/login`).
4. The Refine UI automatically stores the JWT in local storage and attaches it to subsequent API requests.

## Navigating the Admin Panel

- **Topics**: Create or edit topics, manage descriptions, and assign contexts.
- **Contexts**: Upload Markdown, PDF, or FAQ documents. Processing status, chunk counts, and source previews are shown inline.
- **Bulk Operations**: Trigger embedding regeneration, assign contexts to topics, and refresh system prompts from the “Operations” area.
- **History**: Review user question history for auditing and quality checks.

Each resource can be filtered and sorted. Use the search box in the table header to quickly locate entries.

## Uploading Content

1. Go to **Contexts → New**.
2. Choose the content type (Markdown, PDF, FAQ).
3. Provide metadata (title, description) and upload files or paste text.
4. Submit; the backend enqueues processing tasks and updates the status column.
5. After processing, associate the context with topics using the multi-select control.

## Managing Topics

1. Navigate to **Topics** and click **Create**.
2. Fill in name, description, and optional system prompt overrides.
3. Assign contexts from the available list.
4. Save to persist changes. The RAG endpoint immediately reflects the new configuration.

## Authentication & Roles

- JWTs are issued via `POST /api/auth/login` and validated by the backend through `require_admin` dependency.
- Password policies and hashing use `passlib` with Django-compatible PBKDF2 hashes, ensuring legacy credentials remain valid.
- To add new admins, create a user record in PostgreSQL (`auth_user` table) and set `is_staff=true`, `is_superuser=true`. You can use Alembic migrations or SQL scripts. Roadmap: dedicated admin creation CLI.

## Monitoring & Troubleshooting

- Health endpoint: `GET /health` returns `{"status": "healthy"}`.
- Backend logs: `docker-compose -f docker-compose.prod.yml logs -f backend`.
- Frontend logs: `docker-compose -f docker-compose.prod.yml logs -f frontend`.
- Check Redis and Qdrant containers if embeddings or caching misbehave.
- Use the Refine UI notifications for upload progress and error messages.

## Known Limitations

- Legacy Django admin workflows are deprecated; do not rely on `manage.py` commands.
- Initial admin user creation still requires manual SQL or seed scripts (planned improvement).
- Some archived documentation retains Django references—see docs archive for historical context only.

For additional operational runbooks, consult `docs/DEPLOYMENT.md` and `docs/TESTING_STRATEGY.md`.
