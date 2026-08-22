FROM python:3.12-slim

WORKDIR /app

# Install system deps for lxml and optional PDF export
RUN apt-get update && apt-get install -y --no-install-recommends \
    libxml2-dev libxslt1-dev \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md ./
COPY src/ ./src/

# Regular (non-editable) install — images should not depend on live source mounts.
RUN pip install --no-cache-dir .

# MCP stdio transport — run as subprocess from host
ENTRYPOINT ["gitbook-dl"]
CMD ["--help"]
