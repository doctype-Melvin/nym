FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    libgomp1 \
    libglib2.0-0 \
    libgl1 \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN pip install --no-cache-dir \
    --retries 5 \
    --timeout 300 \
    "de_core_news_lg @ https://github.com/explosion/spacy-models/releases/download/de_core_news_lg-3.8.0/de_core_news_lg-3.8.0-py3-none-any.whl"

COPY ui/ ./ui/
COPY data/refs/ ./data/refs/
COPY assets/fonts/ArialUnicode.ttf /usr/share/fonts/ArialUnicode.ttf

RUN mkdir -p /app/data/vault \
             /app/data/output \
             /app/data/input

RUN mkdir -p /app/.streamlit
COPY assets/streamlit_config.toml /app/.streamlit/config.toml

ENV DB_PATH=/app/data/vault/complyable_vault.db
ENV CSV_PATH=/app/data/refs/dict_seed.csv
ENV FONT_PATH=/usr/share/fonts/ArialUnicode.ttf
ENV TORCH_CPP_LOG_LEVEL=ERROR

RUN python -c "\
from docling.datamodel.pipeline_options import PdfPipelineOptions; \
from docling.document_converter import DocumentConverter, PdfFormatOption; \
from docling.datamodel.base_models import InputFormat; \
opts = PdfPipelineOptions(); \
opts.do_ocr = False; \
opts.do_table_structure = False; \
DocumentConverter(format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=opts)}); \
print('Docling ready')"

EXPOSE 8501

CMD ["streamlit", "run", "/app/ui/main.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true"]
