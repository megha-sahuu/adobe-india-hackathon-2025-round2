import pdfplumber
import re

def parse_pdf_sections(pdf_path):
    sections = []
    section_title = None
    section_text = ''
    section_page = 1
    section_titles = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text() or ''
            lines = text.split('\n')
            for line in lines:
                # Heuristic: Section titles are lines in ALL CAPS or start with a number
                if re.match(r'^[A-Z][A-Z\s\-:]{5,}$', line.strip()) or re.match(r'^[0-9]+[.\)]?\s', line.strip()):
                    if section_title and section_text.strip():
                        sections.append({
                            'section_title': section_title,
                            'text': section_text.strip(),
                            'page_number': section_page
                        })
                    section_title = line.strip()
                    section_text = ''
                    section_page = i + 1
                    section_titles.append(section_title)
                else:
                    section_text += line + ' '
            # End of page: if no new section, continue accumulating
        # Add last section
        if section_title and section_text.strip():
            sections.append({
                'section_title': section_title,
                'text': section_text.strip(),
                'page_number': section_page
            })
    # If no sections found, treat whole doc as one section
    if not sections:
        with pdfplumber.open(pdf_path) as pdf:
            full_text = '\n'.join([p.extract_text() or '' for p in pdf.pages])
        sections = [{
            'section_title': 'Full Document',
            'text': full_text.strip(),
            'page_number': 1
        }]
    return sections 