# MyOwnX — Product Requirements Document

**Version:** 1.0 · **Date:** 2026-07-06 · **Status:** Approved

## 1. Overview

MyOwnX is a Twitter/X-style social network built as a portfolio-grade demo:
a set of Python microservices behind a modern single-page web app. It
demonstrates product thinking, service architecture, and disciplined
engineering (small files, migrations, tests, CI) within a ~2.5 hour build.

## 2. Goals

- Let people share short posts and follow other people.
- Deliver a fast, modern, unique-looking UI.
- Demonstrate clean microservice boundaries (API-only communication).
- Keep the system easy to run locally with a single `docker compose up`.

### Non-goals (out of scope)

- Direct messages, notifications, media uploads (images/video).
- Retweets/quotes, hashtags, trending topics.
- Email verification, password reset, OAuth social login.
- Horizontal scaling, multi-region, real message queues.

## 3. Users & personas

| Persona | Need |
|---|---|
| **Visitor** | Sign up quickly and see what the product is. |
| **Member** | Post thoughts, follow interesting people, read a timeline. |
| **Reader** | Browse profiles and search content without friction. |

## 4. Functional requirements

### 4.1 Accounts & auth
- **FR-1** Sign up with username, display name, password.
- **FR-2** Log in and receive a JWT access token.
- **FR-3** All write actions require authentication.

### 4.2 Posts
- **FR-4** Create a post of up to 280 characters.
- **FR-5** Reply to a post; replies form a single-level thread view.
- **FR-6** Delete my own post.
- **FR-7** Like / unlike a post; like counts visible to everyone.

### 4.3 Social graph
- **FR-8** Follow / unfollow a user.
- **FR-9** See follower / following counts on profiles.

### 4.4 Timeline & discovery
- **FR-10** Home timeline: recent posts from people I follow (plus my own),
  newest first, paginated.
- **FR-11** Profile page: a user's posts, newest first.
- **FR-12** Search posts by keyword and users by username/display name.

## 5. Non-functional requirements

- **NFR-1 Performance:** timeline and search respond in < 200 ms locally;
  pagination everywhere; no N+1 calls between services (batch endpoints).
- **NFR-2 Architecture:** each service owns its data; inter-service
  communication is HTTP APIs only — no shared volumes or shared tables.
- **NFR-3 Migrations:** every schema change is a reversible Alembic
  migration (upgrade + downgrade).
- **NFR-4 Code quality:** Python files ≤ 200 lines, functions ≤ 100 lines,
  JS files ≤ 100 lines; consistent lowercase-kebab-case file/folder names.
- **NFR-5 Operability:** `docker compose up` starts everything; health
  endpoints on every service; CI runs lint + tests on every push.
- **NFR-6 Security:** passwords hashed (bcrypt), JWT-based sessions,
  services validate tokens without calling auth on every request.

## 6. Key product decisions

| Decision | Choice | Why |
|---|---|---|
| Backend framework | FastAPI | Async performance, Pydantic validation, free OpenAPI docs |
| Frontend | React + Vite | Component model, fast dev server, small focused files |
| Data store | PostgreSQL — one container, one logical DB per service | Enforces API-only rule physically; independent, reversible migrations per service; light on local resources |
| Auth | JWT (shared public verification) | Stateless; services verify locally → no auth bottleneck |
| Post length | 280 chars | Classic constraint; keeps UI and storage simple |

## 7. Success criteria

- A new user can sign up, post, follow someone, and see a mixed timeline
  in under one minute.
- `docker compose up` + seed script → working demo with sample data.
- CI is green: lint, tests, and file-size limits all pass.
