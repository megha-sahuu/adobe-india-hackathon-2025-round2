import fitz  # PyMuPDF

def extract_lines(pdf_path):
    doc = fitz.open(pdf_path)
    all_lines = []
    for pno, page in enumerate(doc, start=1):
        blocks = page.get_text("dict")["blocks"]
        for b in blocks:
            if "lines" not in b:
                continue
            for l in b["lines"]:
                span_texts = []
                sizes = []
                fonts = []
                flags = []
                for s in l["spans"]:
                    text = s["text"].strip()
                    if not text:
                        continue
                    span_texts.append(text)
                    sizes.append(s["size"])
                    fonts.append(s["font"])
                    flags.append(s["flags"])  # bit flags: bold/italic etc.
                if not span_texts:
                    continue
                merged = " ".join(span_texts).strip()
                if not merged:
                    continue
                avg_size = sum(sizes) / len(sizes)
                left = min(s["bbox"][0] for s in l["spans"])
                top = min(s["bbox"][1] for s in l["spans"])
                # save one line per text line
                all_lines.append({
                    "text": merged,
                    "page": pno,
                    "font_size": avg_size,
                    "font_names": list(set(fonts)),
                    "flags": flags,  # list of ints
                    "left": left,
                    "top": top
                })
    doc.close()
    return all_lines
