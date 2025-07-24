from collections import defaultdict

def assign_levels(cands):
    if not cands:
        return "", []

    # Title: best score on page 1 (exclude 'table of contents')
    title_line = ""
    best = -1
    for l in cands:
        if l["page"] == 1 and l["heading_score"] > best and "table of contents" not in l["text"].lower():
            best = l["heading_score"]
            title_line = l["text"]

    # group by style (font_size_rank, is_bold, left indent bucket)
    def indent_bucket(val):
        return round(val / 20)  # 20px buckets

    style_groups = defaultdict(list)
    for l in cands:
        key = (l["font_size_rank"], l["is_bold"], indent_bucket(l["left"]))
        style_groups[key].append(l)

    # order groups by avg font_size_rank (ascending), then indent (ascending)
    ordered_styles = sorted(style_groups.items(), key=lambda kv: (
        kv[0][0],  # rank 1 is biggest font
        kv[0][2]   # indent bucket
    ))

    # map top 3 groups to H1/H2/H3
    level_map = {}
    levels = ["H1", "H2", "H3"]
    for i, (k, _) in enumerate(ordered_styles[:3]):
        level_map[k] = levels[i]

    outline = []
    for k, arr in style_groups.items():
        lvl = level_map.get(k, None)
        if not lvl:
            continue
        for l in arr:
            outline.append({"level": lvl, "text": l["text"], "page": l["page"]})

    # keep doc order
    outline.sort(key=lambda x: (x["page"]))
    return title_line, outline
