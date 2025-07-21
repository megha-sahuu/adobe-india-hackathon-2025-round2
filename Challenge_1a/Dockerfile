FROM --platform=linux/amd64 python:3.10-slim-bookworm

WORKDIR /app

COPY requirements.txt .

# Install the Python dependencies listed in requirements.txt.
# --no-cache-dir ensures that pip does not store downloaded packages,
# keeping the image size smaller.
RUN pip install --no-cache-dir -r requirements.txt

# Copy the processing script
COPY process_pdfs.py .

# Run the script
CMD ["python3", "process_pdfs.py"] 