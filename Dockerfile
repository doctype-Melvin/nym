FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    libgomp1 \
    libglib2.0-0 \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

# Layer 1 — CPU-only torch first, explicitly
RUN pip install --no-cache-dir \
    torch==2.3.1+cpu \
    torchvision==0.18.1+cpu \
    --extra-index-url https://download.pytorch.org/whl/cpu

# Layer 2 — everything else
RUN pip install --no-cache-dir \
    streamlit==1.45.0 \
    pandas \
    "numpy<2" \
    "spacy==3.8.7" \
    fpdf2 \
    python-dotenv \
    st-copy==1.1.2 \
    "openpyxl==3.1.5" \
    docling

# Layer 3 — spaCy German model
RUN pip install --no-cache-dir \
    --retries 5 \
    --timeout 300 \
    "de_core_news_lg @ https://github.com/explosion/spacy-models/releases/download/de_core_news_lg-3.8.0/de_core_news_lg-3.8.0-py3-none-any.whl"

COPY ui/ ./ui/
COPY data/refs/ ./data/refs/
COPY assets/fonts/ArialUnicode.ttf /usr/share/fonts/ArialUnicode.ttf

RUN mkdir -p /app/data/vault \
             /app/data/output \
             /app/data/input \
             /app/.streamlit

COPY assets/streamlit_config.toml /app/.streamlit/config.toml

ENV DB_PATH=/app/data/vault/complyable_vault.db
ENV CSV_PATH=/app/data/refs/dict_seed.csv
ENV FONT_PATH=/usr/share/fonts/ArialUnicode.ttf
ENV TORCH_CPP_LOG_LEVEL=ERROR

EXPOSE 8501
CMD ["streamlit", "run", "/app/ui/main.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true"]