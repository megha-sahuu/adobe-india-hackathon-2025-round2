# Adobe India Hackathon 2025 – “Connecting the Dots”
This repo holds my Round-2 submissions.

## Challenge 1A – PDF Outline Extractor
– Turns any ≤50-page PDF into a JSON outline (Title + H1/H2/H3 with page numbers).
– Pure Python + PyMuPDF, runs fully offline in <10 s/file.

## Challenge 1B – Persona-Driven Document Intelligence
– Given 3-10 PDFs plus a persona & job prompt, it ranks the most relevant sections and paragraphs.
– Uses MiniLM-L6-v2 embeddings + FAISS (≈66 MB total model weight).
– Fits hackathon limits: CPU-only, ≤60 s, no internet.