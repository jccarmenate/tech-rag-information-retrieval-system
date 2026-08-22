FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml ./
COPY app ./app

# sentence-transformers pulls in torch (a large wheel); a generous timeout
# avoids spurious failures on slower connections during image builds.
ENV PIP_DEFAULT_TIMEOUT=200
RUN pip install --no-cache-dir -e .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
