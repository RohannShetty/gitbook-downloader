FROM python:3.12-slim

WORKDIR /app

# Install system deps for lxml and optional PDF export
RUN apt-get update && apt-get install -y --no-install-recommends \
    libxml2-dev libxslt1-dev \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md ./
COPY src/ ./src/

RUN pip install --no-cache-dir -e ".[all]"

# MCP stdio transport — run as subprocess from host
ENTRYPOINT ["gitbook-dl"]
CMD ["--help"]
