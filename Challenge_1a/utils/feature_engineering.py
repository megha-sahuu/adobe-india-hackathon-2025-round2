import re
from statistics import median

_NUM_PAT = re.compile(r"^(\d+(\.\d+)*|[A-Z]\.|[IVXLCDM]+\.)\s+")  # 1., 1.2., A., II.

def add_features(lines):
    if not lines:
        return lines

    # global font-size ranks
    sizes = [round(l["font_size"], 1) for l in lines]
    unique_sorted = sorted(set(sizes), reverse=True)
    size_rank_map = {s: i for i, s in enumerate(unique_sorted, start=1)}

    # page medians
    by_page = {}
    for l in lines:
        by_page.setdefault(l["page"], []).append(l)

    # y_gap above: difference between this line's top and previous line top on same page
    for page, arr in by_page.items():
        arr.sort(key=lambda x: x["top"])
        prev_top = None
        for l in arr:
            l["y_gap_above"] = (l["top"] - prev_top) if prev_top is not None else 9999
            prev_top = l["top"]

    # decorate
    for l in lines:
        l["font_size_rank"] = size_rank_map[round(l["font_size"], 1)]
        l["is_all_caps"] = l["text"].isupper() and len(l["text"]) > 3
        l["starts_with_numbering"] = bool(_NUM_PAT.match(l["text"]))
        # Bold flag: in PyMuPDF flags bit 2 means bold (mask 2)
        l["is_bold"] = any((f & 2) != 0 for f in l["flags"])
    return lines
