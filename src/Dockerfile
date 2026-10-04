# ---------- Stage 1: builder ----------
    FROM python:3.12-slim AS builder

    WORKDIR /app
    
    RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        && rm -rf /var/lib/apt/lists/*
    
    COPY requirements.txt .
    RUN python -m venv /opt/venv
    ENV PATH="/opt/venv/bin:$PATH"
    RUN pip install --no-cache-dir --upgrade pip \
        && pip install --no-cache-dir -r requirements.txt
    
    # ---------- Stage 2: runtime ----------
    FROM python:3.12-slim
    
    RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq5 \
        && rm -rf /var/lib/apt/lists/* \
        && useradd --create-home --shell /bin/bash appuser
    
    COPY --from=builder /opt/venv /opt/venv
    ENV PATH="/opt/venv/bin:$PATH"
    
    WORKDIR /app
    COPY --chown=appuser:appuser . .
    COPY --chown=appuser:appuser entrypoint.sh /entrypoint.sh
    RUN chmod +x /entrypoint.sh
    
    USER appuser
    
    EXPOSE 8000
    
    ENTRYPOINT ["/entrypoint.sh"]