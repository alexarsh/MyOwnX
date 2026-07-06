# MyOwnX

A Twitter/X-style social network built as Python microservices with a
React frontend, orchestrated by Docker Compose.

> 📄 Docs: [Product Requirements](docs/prd.md) · [High-Level Design](docs/hld.md)

## Quick start

```bash
docker compose up --build
```

Then open **http://localhost:3000** and create an account right on the
landing page (username + password — it's a demo, use throwaway values).

## Architecture at a glance

| Service | Role | Port |
|---|---|---|
| `web` | React SPA + nginx API gateway | 3000 |
| `user-service` | Accounts, JWT auth, profiles, follows | 9001 |
| `post-service` | Posts, replies, likes, search | 9002 |
| `timeline-service` | Timeline & search aggregation | 9003 |
| `postgres` | One container, one logical DB per service | 9432 |

Services talk to each other via HTTP APIs only — each owns its database
and nothing else can touch it. See [docs/hld.md](docs/hld.md) for the
full design, API contracts and decision log.

## Repository layout

```
docs/       PRD and HLD
services/   user-service, post-service, timeline-service
web/        React + Vite SPA, nginx config
shared/     cross-service assets (postgres init, env)
data/       runtime data volumes (gitignored)
```

## Development

Each service is self-contained (own `requirements.txt`, own image);
dependencies shared by all services live in `shared/requirements-base.txt`.
Interactive API docs are available at `http://localhost:900{1,2,3}/docs`
when running.

## Testing

```bash
scripts/run-tests.sh   # pytest per service, in containers, vs dedicated
                       # test DBs (schema dropped after the run)
scripts/e2e.sh         # full user journey in an isolated throwaway stack
                       # (tmpfs postgres, destroyed afterwards)
```

Test data never touches the dev databases.

Migrations are reversible; verify with
`docker compose exec user-service alembic downgrade base && ... upgrade head`.
