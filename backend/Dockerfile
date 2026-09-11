FROM python:3.12-slim-bookworm AS dependencies
WORKDIR /build
COPY requirements.lock .
RUN pip install --no-cache-dir --require-hashes --prefix=/install -r requirements.lock

FROM python:3.12-slim-bookworm AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
RUN groupadd --gid 10001 app && useradd --uid 10001 --gid app --no-create-home app
COPY --from=dependencies /install /usr/local
COPY --chown=app:app app ./app
COPY --chown=app:app alembic ./alembic
COPY --chown=app:app alembic.ini pyproject.toml entrypoint.sh ./
USER app
EXPOSE 8000
ENTRYPOINT ["sh", "/app/entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--no-access-log"]

FROM runtime AS development
USER root
COPY requirements-dev.lock .
RUN pip install --no-cache-dir --require-hashes -r requirements-dev.lock
COPY --chown=app:app tests ./tests
USER app
