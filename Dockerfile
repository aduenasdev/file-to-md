ARG PYTHON_VERSION=3.12
FROM python:${PYTHON_VERSION}-slim
# Extras a instalar: light | light,docling | all
ARG EXTRAS=light,docling
RUN apt-get update && apt-get install -y --no-install-recommends libgl1 libglib2.0-0 && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY pyproject.toml README.md ./
COPY file_to_md ./file_to_md
RUN pip install --no-cache-dir ".[${EXTRAS}]"
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s CMD python -c "import urllib.request as u; u.urlopen('http://localhost:8000/health')"
CMD ["python", "-m", "file_to_md", "serve", "--host", "0.0.0.0", "--port", "8000"]
