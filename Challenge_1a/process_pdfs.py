
"""
process_pdfs.py – Round-1A PDF outline extractor
  • Title → first contiguous block on page-1, largest font
  • Headings → next largest fonts, promoted so first is always H1
  • Multi-line headings merged by same page/level/size (±tol)
"""
from pathlib import Path
from dataclasses import dataclass
from typing import List, Tuple
from collections import defaultdict
import concurrent.futures
import json, jsonschema

import fitz        

INPUT_DIR   = Path("/app/input")
OUTPUT_DIR  = Path("/app/output")
SCHEMA_FILE = Path(__file__).parent / "sample_dataset/schema/output_schema.json"
MAX_PROCS   = 8
SIZE_TOL    = 1       

# DATACLASS
@dataclass
class Line:
    text: str
    size: int        
    y0: float
    page: int        

# 1) EXTRACT LINES
def extract_lines(pdf_path: Path) -> List[Line]:
    doc = fitz.open(pdf_path)
    out: List[Line] = []
    for pno in range(doc.page_count):
        page = doc.load_page(pno)
        ph = page.rect.height
        for blk in page.get_text("dict")["blocks"]:
            for ln in blk.get("lines", []):
                spans = ln.get("spans", [])
                if not spans: continue
                words, pts = [], []
                for sp in spans:
                    t = sp["text"].strip()
                    if t:
                        words.append(t)
                        pts.append(sp["size"])
                if not words: continue
                y0 = ln["bbox"][1]
                # skip headers/footers
                if pno>0 and (y0<40 or ph-y0<40): continue
                # round to integer pts
                size = int(round(max(pts)))
                out.append(Line(text=" ".join(words), size=size, y0=y0, page=pno+1))
    doc.close()
    return out

# 2) EXTRACT TITLE (contiguous on page-1)
def extract_title(lines: List[Line]) -> Tuple[str, List[Line]]:
    page1 = sorted([l for l in lines if l.page==1], key=lambda l:l.y0)
    if not page1:
        return "Untitled Document", lines
    max_sz = max(l.size for l in page1)
    block = []
    for l in page1:
        if l.size==max_sz:
            block.append(l)
        elif block:
            break
    title = " ".join(l.text for l in block)
    remaining = [l for l in lines if l not in block]
    return title, remaining

# 3) MAP SIZES → LEVELS (skip title size)
def size_to_level(lines: List[Line]) -> dict:
    uniq = sorted({l.size for l in lines}, reverse=True)
    top = uniq[:3]
    names = ["H1","H2","H3"]
    return defaultdict(lambda: None, {sz:names[i] for i,sz in enumerate(top)})

# 4) MERGE MULTI-LINE HEADINGS
def merge_headings(items: List[dict]) -> List[dict]:
    merged = []
    for it in items:
        if not merged:
            merged.append(it); continue
        last = merged[-1]
        same_page = it["page"]==last["page"]
        same_level= it["level"]==last["level"]
        size_diff = abs(it["_size"]-last["_size"])<=SIZE_TOL
        same_text = it["text"]==last["text"]
        if same_page and same_level and (size_diff or same_text):
            last["text"] += " "+it["text"]
        else:
            merged.append(it)
    for it in merged:
        it.pop("_size",None)
    return merged

# 5) BUILD OUTLINE + PROMOTE FIRST TO H1
def build_outline(lines: List[Line]) -> dict:
    title, body = extract_title(lines)
    lvl_map = size_to_level(body)
    raw = [{
        "level": lvl_map[l.size],
        "text" : l.text,
        "page" : l.page,
        "_size": l.size
    } for l in sorted(body, key=lambda x:(x.page,x.y0)) if lvl_map[l.size]]
    outline = merge_headings(raw)
    # force first heading to H1
    if outline:
        outline[0]["level"] = "H1"
    return {"title":title, "outline":outline}

# 6) WRITE JSON (schema validated)
with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
    SCHEMA = json.load(f)

def write_json(path: Path, payload: dict):
    jsonschema.validate(payload, SCHEMA)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

# MAIN
def process_pdf(pdf: Path):
    try:
        lines = extract_lines(pdf)
        out   = build_outline(lines)
        write_json(OUTPUT_DIR/f"{pdf.stem}.json", out)
        print(f"[✓] {pdf.name}")
    except Exception as e:
        print(f"[✗] {pdf.name}: {e}")

def main():
    pdfs = sorted(INPUT_DIR.glob("*.pdf"))
    if not pdfs:
        print("No PDFs found in /app/input"); return
    with concurrent.futures.ProcessPoolExecutor(max_workers=min(MAX_PROCS,len(pdfs))) as ex:
        ex.map(process_pdf, pdfs)

if __name__=="__main__":
    main()
