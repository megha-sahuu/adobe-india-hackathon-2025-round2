FROM --platform=linux/amd64 python:3.10-slim

ENV PIP_NO_CACHE_DIR=1

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY process_pdfs.py .
COPY sample_dataset/schema sample_dataset/schema

CMD ["python", "process_pdfs.py"]
