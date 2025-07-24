def score_headings(lines):
    """
    Simple weighted score. Tune weights if needed.
    """
    scored = []
    for l in lines:
        score = 0
        # bigger fonts -> likely heading
        score += max(0, 10 - l["font_size_rank"]) * 2  # higher rank (1) -> more points
        if l["is_bold"]:
            score += 3
        if l["is_all_caps"]:
            score += 2
        if l["starts_with_numbering"]:
            score += 2
        if l["y_gap_above"] > 8:  # visually separated
            score += 1
        # penalize extremely long lines (>140 chars) -> probably paragraph
        if len(l["text"]) > 140:
            score -= 4
        l["heading_score"] = score
        scored.append(l)

    # threshold adaptively: top X% or score>=something
    # let's keep only lines with score >=5 or top 40 lines (whichever smaller)
    thresh = 5
    candidates = [l for l in scored if l["heading_score"] >= thresh]
    if len(candidates) > 40:
        candidates = sorted(candidates, key=lambda x: x["heading_score"], reverse=True)[:40]

    return candidates
