# Build context is the repo root, so the shared base requirements can be
# layered under the service's own (see shared/requirements-base.txt).
FROM python:3.12-slim

WORKDIR /srv

COPY shared/requirements-base.txt /deps/shared/requirements-base.txt
COPY services/timeline-service/requirements.txt /deps/services/timeline-service/requirements.txt
RUN pip install --no-cache-dir -r /deps/services/timeline-service/requirements.txt

COPY services/timeline-service/app ./app

EXPOSE 9003
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "9003"]
