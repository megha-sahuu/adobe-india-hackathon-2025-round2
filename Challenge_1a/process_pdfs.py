# import os
# import json
# from pathlib import Path

# def process_pdfs():
#     # Get input and output directories
#     input_dir = Path("/app/input")
#     output_dir = Path("/app/output")
    
#     # Create output directory if it doesn't exist
#     output_dir.mkdir(parents=True, exist_ok=True)
    
#     # Get all PDF files
#     pdf_files = list(input_dir.glob("*.pdf"))
    
#     for pdf_file in pdf_files:
#         # Create dummy JSON data
#         dummy_data = {
#             "title": "Understanding AI",
#             "outline": [
#                 {
#                     "level": "H1",
#                     "text": "Introduction",
#                     "page": 1
#                 },
#                 {
#                     "level": "H2",
#                     "text": "What is AI?",
#                     "page": 2
#                 },
#                 {
#                     "level": "H3",
#                     "text": "History of AI",
#                     "page": 3
#                 }
#             ]
#         }
        
#         # Create output JSON file
#         output_file = output_dir / f"{pdf_file.stem}.json"
#         with open(output_file, "w") as f:
#             json.dump(dummy_data, f, indent=2)
        
#         print(f"Processed {pdf_file.name} -> {output_file.name}")

# if __name__ == "__main__":
#     print("Starting processing pdfs")
#     process_pdfs() 
#     print("completed processing pdfs")

import os
import json
from pathlib import Path
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar, LTTextLineHorizontal

def process_pdfs():
    """
    Main function to process all PDF files in the input directory,
    extract outlines, and save them as JSON files in the output directory.
    """
    # Input and output directories are expected to be mounted by Docker.
    input_dir = Path("/app/input")
    output_dir = Path("/app/output")

    # Ensure the output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    # Process each PDF file found in the input directory
    for pdf_file in input_dir.glob("*.pdf"):
        print(f"Processing PDF: {pdf_file.name}")
        try:
            # Extract outline from the current PDF
            title, outline = extract_pdf_outline(pdf_file)

            # Prepare the output JSON structure
            output_data = {
                "title": title,
                "outline": outline
            }

            # Define the output JSON file path
            output_file_path = output_dir / f"{pdf_file.stem}.json"

            # Save the extracted data to a JSON file
            with open(output_file_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)
            print(f"Successfully processed {pdf_file.name}. Output saved to {output_file_path}")

        except Exception as e:
            print(f"Error processing {pdf_file.name}: {e}")

def extract_pdf_outline(pdf_path):
    """
    Extracts the title and a hierarchical outline (H1, H2, H3) from a PDF.

    Args:
        pdf_path (Path): The path to the PDF file.

    Returns:
        tuple: A tuple containing the document title (str) and a list of
               dictionaries representing the outline.
    """
    document_title = "Untitled Document"
    outline = []
    
    # Store text lines with their properties for later analysis
    all_text_lines = []
    
    # First pass: Extract all text lines with properties and identify potential title
    # Also collect font sizes to determine relative heading levels
    font_sizes = {}
    
    # Store page dimensions to help with y0 positioning for title detection
    page_dimensions = {}

    for page_num, page_layout in enumerate(extract_pages(pdf_path)):
        page_dimensions[page_num + 1] = {"width": page_layout.width, "height": page_layout.height}
        for element in page_layout:
            if isinstance(element, LTTextContainer):
                for text_line in element:
                    if isinstance(text_line, LTTextLineHorizontal):
                        line_text = text_line.get_text().strip()
                        if line_text:
                            # Get font size from the first character if available
                            font_size = None
                            if hasattr(text_line, '_objs') and text_line._objs:
                                for char in text_line._objs:
                                    if isinstance(char, LTChar):
                                        font_size = round(char.size, 2)
                                        break # Take the size of the first char in the line

                            if font_size:
                                font_sizes[font_size] = font_sizes.get(font_size, 0) + 1
                                all_text_lines.append({
                                    "text": line_text,
                                    "font_size": font_size,
                                    "x0": round(text_line.x0, 2),
                                    "y0": round(text_line.y0, 2),
                                    "page": page_num + 1 # Page numbers are 1-indexed
                                })

    # Sort font sizes by frequency and then by value (descending)
    # This helps identify the most prominent font sizes in the document
    sorted_font_sizes = sorted(font_sizes.keys(), key=lambda x: (font_sizes[x], x), reverse=True)

    # Determine relative font size tiers for heading classification
    # This is a simplified approach; a more robust solution might cluster font sizes
    # Ensure there are at least 3 distinct font sizes for H1, H2, H3
    h1_size_threshold = 16.0 # Default fallback
    h2_size_threshold = 14.0 # Default fallback
    h3_size_threshold = 12.0 # Default fallback

    if len(sorted_font_sizes) >= 3:
        # Use the top 3 most frequent (and largest) font sizes
        h1_size_threshold = sorted_font_sizes[0]
        h2_size_threshold = sorted_font_sizes[1]
        h3_size_threshold = sorted_font_sizes[2]
    elif len(sorted_font_sizes) == 2:
        h1_size_threshold = sorted_font_sizes[0]
        h2_size_threshold = sorted_font_sizes[1]
        h3_size_threshold = sorted_font_sizes[1] * 0.9 # Infer H3 slightly smaller than H2
    elif len(sorted_font_sizes) == 1:
        h1_size_threshold = sorted_font_sizes[0]
        h2_size_threshold = sorted_font_sizes[0] * 0.9
        h3_size_threshold = sorted_font_sizes[0] * 0.8
    # If less than 1 font size (empty document), defaults will be used

    # Adjust thresholds to ensure H1 > H2 > H3 strictly
    # This prevents cases where font sizes might be very close
    h1_size_threshold = max(h1_size_threshold, h2_size_threshold + 0.1) if h1_size_threshold <= h2_size_threshold else h1_size_threshold
    h2_size_threshold = max(h2_size_threshold, h3_size_threshold + 0.1) if h2_size_threshold <= h3_size_threshold else h2_size_threshold


    # Second pass: Identify title and headings based on collected data
    
    # Simple title detection: largest text on first page, near top/center
    first_page_lines = [line for line in all_text_lines if line['page'] == 1]
    if first_page_lines:
        # Sort by font size (desc), then by y-position (desc, higher on page first)
        first_page_lines.sort(key=lambda x: (x['font_size'], x['y0']), reverse=True)
        
        # Get the height of the first page to determine "near top"
        first_page_height = page_dimensions.get(1, {}).get("height", 800) # Default to 800 if not found

        # Iterate through top lines to find a suitable title
        for i, line in enumerate(first_page_lines):
            # A very simple check for title: large font, relatively high on page (top 30%)
            # and not too short (like a page number or header)
            if line['font_size'] >= h1_size_threshold and \
               len(line['text']) > 5 and \
               line['y0'] > first_page_height * 0.7: # Top 30% of the page
                document_title = line['text']
                break
            if i > 5: # Check top 6 largest lines for title
                break

    # Process all text lines to identify headings
    # Store candidates temporarily to sort them correctly later
    temp_heading_candidates = []

    for line_data in all_text_lines:
        text = line_data['text']
        font_size = line_data['font_size']
        x0 = line_data['x0']
        page = line_data['page']

        level = None
        
        # Heuristics for heading classification
        # Prioritize font size, then consider indentation (x0) and content patterns
        
        # Check for H1
        if font_size >= h1_size_threshold:
            level = "H1"
        # Check for H2
        elif font_size >= h2_size_threshold:
            level = "H2"
        # Check for H3
        elif font_size >= h3_size_threshold:
            level = "H3"
        
        # Further refine based on indentation and common heading patterns
        # These x0 thresholds are typical for left-aligned text on A4-like pages.
        # They might need tuning for very different document layouts.
        is_potential_heading = False
        if level:
            # Check for common heading characteristics
            # 1. Indentation (usually left-aligned or slightly indented)
            if x0 < 150: # Assuming typical left margin, adjust as needed
                is_potential_heading = True
            
            # 2. Capitalization and numbering patterns
            if text.isupper() and len(text) > 3: # All caps (e.g., SECTION 1)
                is_potential_heading = True
            elif text.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.',
                                  'A.', 'B.', 'C.', 'I.', 'II.', 'III.')): # Numbered/Lettered sections
                is_potential_heading = True
            elif len(text.split()) < 10: # Short lines are more likely headings
                is_potential_heading = True
            
            # Negative heuristic: headings typically don't end with periods unless it's an abbreviation
            if text.endswith('.') and not text.endswith('etc.'): # Simple check
                is_potential_heading = False

            # If it passes initial font size and any of the pattern/indentation checks, add as candidate
            if is_potential_heading:
                # Add to temporary list with all original data for sorting
                temp_heading_candidates.append({
                    "level": level,
                    "text": text,
                    "page": page,
                    "y0": line_data['y0'] # Keep y0 for accurate sorting
                })

    # Sort candidates by page number, then by y0 position (descending, as y0 is from bottom of page)
    temp_heading_candidates.sort(key=lambda x: (x['page'], -x['y0']))

    # Filter for unique headings and build the final outline
    seen_headings = set()
    for item in temp_heading_candidates:
        # Create a unique key for each heading (text + page) to prevent duplicates
        heading_key = (item['text'], item['page'])
        if heading_key not in seen_headings:
            outline.append({
                "level": item['level'],
                "text": item['text'],
                "page": item['page']
            })
            seen_headings.add(heading_key)

    return document_title, outline

if __name__ == "__main__":
    print("Starting PDF outline extraction...")
    process_pdfs()
    print("PDF outline extraction completed.")
