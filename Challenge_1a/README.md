# Challenge 1a: PDF Processing Solution

## Overview
This project solves the **Round 1A: PDF Processing** challenge from the Adobe India Hackathon 2025. This tool extracts a structured outline (title + section headings) from academic or business PDFs. Headings are inferred from font sizes, positions, and page layout.

## 🚀 Problem Statement

Given an academic or business PDF file, extract:

- Document **title**
- List of headings with:
  - `level` (H1, H2, ...)
  - `text` content
  - `page` number

## 🧠 Approach

1. **Text Extraction**: Uses `pdfminer.six` to extract layout-preserved text and metadata like font size, position, and boldness.
2. **Heuristic Rules**:
   - Title is the largest font on the first page.
   - Headers are inferred by clustering lines with similar font sizes.
   - Multi-line headings are merged.
   - Header levels (H1, H2, ...) are assigned based on font size hierarchy.
   - Footer/header lines are skipped from all but the first page.
3. **Output**: Structured JSON per document, matching a predefined schema.

---

## Libraries Used

| Library           | Purpose                                      |
|------------------|----------------------------------------------|
| `pdfminer.six`    | PDF parsing and layout analysis              |
| `jsonschema`      | Output validation against given schema       |
| `os`, `json`, `collections`, `re` | Standard Python utilities         |

---


## 📦 Folder Structure
├── process_pdfs.py # Main script
├── requirements.txt # Required packages
├── Dockerfile # For containerized execution
├── input/ # Place your PDF files here
├── output/ # Generated JSON files appear here
└── sample_dataset/
└── schema/
└── output_schema.json # JSON schema for output validation


---

## Running the Solution

### Option 1: Local Python

#### 1. Install dependencies

```bash
pip install -r requirements.txt
```
#### 2. Create folders and add PDFs
```bash
mkdir -p input output
# Place your PDFs inside `input/`
```

#### 3. Run the script
```bash
python process_pdfs.py
```
#### Output
JSON files are saved in output/ with the same base filename as input PDFs.

### Option 2: Docker
#### 1. Build Command
```bash
docker build --platform linux/amd64 -t <reponame.someidentifier> .
```
#### For example:
```bash
docker build -t pdf-outline-extractor .
```

#### 2. Run Command
```bash
docker run --rm -v $(pwd)/input:/app/input:ro -v $(pwd)/output/repoidentifier/:/app/output --network none <reponame.someidentifier>
```

#### For example
```bash
docker run --rm \
  -v "$(pwd)/input":/app/input \
  -v "$(pwd)/output":/app/output \
  pdf-outline-extractor
```

### Notes
- First heading is forcibly set as H1.

- Ignores watermarks, footers, and repetitive headers.

- Schema validation is built-in.

- Handles multi-line headings and page breaks.



