# Persona-Driven Document Intelligence (Challenge 1B)

This solution extracts and prioritizes the most relevant sections from a collection of PDFs based on a specific persona and their job-to-be-done.

## Prerequisites
- Python 3.8+
- pip (Python package manager)
- (Optional) Docker

## 1. Install Dependencies
Navigate to the `Challenge_1b` directory and install dependencies:

```bash
pip install -r requirements.txt
```

## 2. Run the Solution (Python)

```bash
python main.py <input_json> <pdfs_directory> <output_json>
```

**Example:**

```bash
python main.py "Collection 1/challenge1b_input.json" "Collection 1/PDFs" "Collection 1/challenge1b_output_generated.json"
```

- `<input_json>`: Path to the input JSON file (see sample in `Collection 1/challenge1b_input.json`)
- `<pdfs_directory>`: Directory containing the PDF files
- `<output_json>`: Path to write the output JSON

## 3. Run with Docker (Optional)

Build the Docker image:

```bash
docker build -t persona-doc-intel .
```

Run the container (mount your collection directory):

```bash
docker run --rm -v "$PWD/Collection 1":/data persona-doc-intel /data/challenge1b_input.json /data/PDFs /data/challenge1b_output_generated.json
```

```bash
docker run --rm -v "$PWD/Collection 2":/data persona-doc-intel /data/challenge1b_input.json /data/PDFs /data/challenge1b_output_generated.json
```

```bash
docker run --rm -v "$PWD/Collection 3":/data persona-doc-intel /data/challenge1b_input.json /data/PDFs /data/challenge1b_output_generated.json
```

## 4. Output
- The output JSON will be written to the path you specify (see sample in `Collection 1/challenge1b_output_generated.json`).

## 5. Files
- `main.py`: Main pipeline script
- `document_parser.py`: PDF parsing and section extraction
- `persona_analyzer.py`: Persona/job keyword extraction and section ranking
- `output_formatter.py`: Output JSON formatting
- `utils.py`: Utility functions
- `requirements.txt`: Python dependencies
- `Dockerfile`: For containerized execution
- `approach_explanation.md`: Methodology explanation

## 6. Notes
- No internet access is required at runtime.
- All processing is CPU-only and efficient for 3-10 PDFs.
- For questions or issues, check the code comments or contact the author. 