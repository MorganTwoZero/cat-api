FROM python:3.10-slim as requirements-stage
WORKDIR /tmp
RUN pip install pdm
COPY ./pyproject.toml ./pdm.lock* /tmp/
RUN pdm export -f requirements -o requirements.txt --without-hashes
FROM python:3.10-slim
WORKDIR /app
COPY --from=requirements-stage /tmp/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt
COPY ./src /app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
