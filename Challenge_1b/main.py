import os
import json
import glob
import sys
from datetime import datetime
from document_parser import parse_pdf_sections
from persona_analyzer import extract_keywords, rank_sections, extract_relevant_sentences
from output_formatter import format_output
from utils import get_processing_timestamp


def main(input_json_path, pdf_dir, output_json_path):
    # Load input
    with open(input_json_path, 'r') as f:
        input_data = json.load(f)

    persona = input_data['persona']['role']
    job = input_data['job_to_be_done']['task']
    document_list = [doc['filename'] for doc in input_data['documents']]

    # Extract keywords from persona and job
    focus_keywords = extract_keywords(persona + ' ' + job)

    # Parse PDFs and extract sections
    all_sections = []
    for doc in document_list:
        pdf_path = os.path.join(pdf_dir, doc)
        sections = parse_pdf_sections(pdf_path)
        for section in sections:
            section['document'] = doc
        all_sections.extend(sections)

    # For each document, select the most relevant section
    top_sections = []
    for doc in document_list:
        doc_sections = [s for s in all_sections if s['document'] == doc]
        if doc_sections:
            ranked = rank_sections(doc_sections, focus_keywords)
            top_sections.append(ranked[0])

    # Rank the selected top sections overall for importance_rank
    top_sections = sorted(top_sections, key=lambda s: -s['score'])

    # Prepare sub-section analysis (refined text)
    subsection_analysis = []
    for sec in top_sections:
        refined_text = extract_relevant_sentences(sec['text'], focus_keywords, max_sentences=5)
        subsection_analysis.append({
            'document': sec['document'],
            'refined_text': refined_text,
            'page_number': sec['page_number']
        })

    # Format output
    output = format_output(
        input_documents=document_list,
        persona=persona,
        job_to_be_done=job,
        processing_timestamp=get_processing_timestamp(),
        extracted_sections=[{
            'document': sec['document'],
            'section_title': sec['section_title'],
            'importance_rank': i+1,
            'page_number': sec['page_number']
        } for i, sec in enumerate(top_sections)],
        subsection_analysis=subsection_analysis
    )

    # Write output
    with open(output_json_path, 'w') as f:
        json.dump(output, f, indent=4)

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print('Usage: python main.py <input_json> <pdf_dir> <output_json>')
        sys.exit(1)
    main(sys.argv[1], sys.argv[2], sys.argv[3]) 