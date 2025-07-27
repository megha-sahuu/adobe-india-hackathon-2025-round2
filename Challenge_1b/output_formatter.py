def format_output(input_documents, persona, job_to_be_done, processing_timestamp, extracted_sections, subsection_analysis):
    return {
        "metadata": {
            "input_documents": input_documents,
            "persona": persona,
            "job_to_be_done": job_to_be_done,
            "processing_timestamp": processing_timestamp
        },
        "extracted_sections": extracted_sections,
        "subsection_analysis": subsection_analysis
    } 