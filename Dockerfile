FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PRICING_PORT=50051 \
    TELEMETRY_PORT=50052

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python tools/generate_contracts.py && python -m pytest -q

RUN useradd --create-home agricorp && chown -R agricorp /app
USER agricorp

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s CMD python -c "import urllib.request,os;urllib.request.urlopen(f'http://localhost:{os.getenv(\"PORT\",\"8501\")}/_stcore/health')"

CMD ["python", "launcher.py"]
