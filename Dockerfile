FROM python:3.12-slim AS builder

WORKDIR /app

# Install build tools and the package
COPY pyproject.toml README.md LICENSE ./
COPY src/ ./src/
RUN pip install --no-cache-dir .

FROM python:3.12-slim

WORKDIR /app

# Copy installed package from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

ENV NAME NeuroLift-Agent-Solidarity-Kit

CMD ["python", "-c", "from asfdk import FoundationMode; print('ASFDK ready —', FoundationMode.STANDARD.value)"]
