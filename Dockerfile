FROM python:3.14-slim AS base

# install curl to download uv via https 
# RUN apt-get update && apt-get install -y build-essential curl
RUN apt-get update && apt-get install --no-install-recommends -y \
    build-essential curl && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install uv
ADD https://astral.sh/uv/install.sh /install.sh
RUN chmod -R 755 /install.sh && /install.sh && rm /install.sh

ENV PATH="/root/.local/bin:${PATH}"

# Setup app workdir
WORKDIR /app

COPY . .

# Install dependencies
RUN uv sync

ENV PATH="/app/.venv/bin:${PATH}"

# ============ PRODUCTION STAGE ============
FROM base AS app

EXPOSE 80

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]

# ============ DEV STAGE ============
FROM base AS dev

EXPOSE 80

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80", "--reload"]

# ============ TEST STAGE ============
FROM base AS test

CMD ["pytest"]