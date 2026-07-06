# Build context is the repo root, so the shared base requirements can be
# layered under the service's own (see shared/requirements-base.txt).
FROM python:3.12-slim

WORKDIR /srv

COPY shared/requirements-base.txt /deps/shared/requirements-base.txt
COPY services/post-service/requirements.txt /deps/services/post-service/requirements.txt
RUN pip install --no-cache-dir -r /deps/services/post-service/requirements.txt

COPY services/post-service/alembic.ini ./
COPY services/post-service/migrations ./migrations
COPY services/post-service/app ./app

EXPOSE 9002
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 9002"]
