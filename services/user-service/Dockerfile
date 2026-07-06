# Build context is the repo root, so the shared base requirements can be
# layered under the service's own (see shared/requirements-base.txt).
FROM python:3.12-slim

WORKDIR /srv

COPY shared/requirements-base.txt shared/requirements-dev.txt /deps/shared/
COPY services/user-service/requirements.txt /deps/services/user-service/requirements.txt
RUN pip install --no-cache-dir -r /deps/services/user-service/requirements.txt

COPY services/user-service/alembic.ini ./
COPY services/user-service/migrations ./migrations
COPY services/user-service/app ./app
COPY services/user-service/pytest.ini ./
COPY services/user-service/tests ./tests

EXPOSE 9001
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 9001"]
