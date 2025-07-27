import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import string

# Simple keyword extraction: tokenize using regex, remove stopwords/punctuation, return unique words
def extract_keywords(text):
    tokens = re.findall(r'\b\w+\b', text.lower())
    words = [w for w in tokens if w.isalnum() and w not in string.punctuation]
    return list(set(words))

# Rank sections by similarity to focus keywords
def rank_sections(sections, focus_keywords):
    docs = [s['text'] for s in sections]
    focus_str = ' '.join(focus_keywords)
    tfidf = TfidfVectorizer().fit([focus_str] + docs)
    focus_vec = tfidf.transform([focus_str])
    doc_vecs = tfidf.transform(docs)
    sims = cosine_similarity(focus_vec, doc_vecs)[0]
    ranked = sorted([
        {**sections[i], 'score': sims[i]} for i in range(len(sections))
    ], key=lambda x: -x['score'])
    return ranked

def is_generic_sentence(sentence):
    generic_phrases = [
        'introduction', 'this guide', 'in conclusion', 'summary', 'overview',
        'will take you through', 'provides an in-depth', 'comprehensive guide',
        'this section', 'this chapter', 'let us', 'we will', 'the following',
        'aim of this', 'purpose of this', 'in this document', 'in this article',
        'in this paper', 'in this report', 'in this book', 'here are some',
        'known for', 'is renowned for', 'is famous for', 'is home to'
    ]
    s = sentence.lower()
    return any(phrase in s for phrase in generic_phrases) or len(s.split()) < 6

# Extract the most relevant sentences from a section for refined text
def extract_relevant_sentences(section_text, focus_keywords, max_sentences=5):
    # Extract bulleted/numbered/colon-separated lines
    lines = section_text.split('\n')
    bullet_lines = [l.strip() for l in lines if re.match(r'^(\s*[\u2022\-\*\d]+[\.)]?\s+|[A-Za-z ]+:)', l)]
    # Also extract lines with multiple semicolons (for lists like "A: B; C: D;")
    semicolon_lines = [l.strip() for l in lines if l.count(';') >= 2]
    # Combine and deduplicate
    list_lines = list(dict.fromkeys(bullet_lines + semicolon_lines))
    # If we have enough list lines, use them as refined text
    if list_lines:
        refined = ' '.join(list_lines[:max_sentences*2])  # allow more lines for lists
        return refined.strip()
    # Otherwise, fall back to best-matching sentences
    sentences = re.split(r'(?<=[.!?])\s+', section_text)
    filtered = [s for s in sentences if not is_generic_sentence(s)]
    if len(filtered) < max_sentences:
        filtered = sentences  # fallback to all if too few
    focus_str = ' '.join(focus_keywords)
    tfidf = TfidfVectorizer().fit([focus_str] + filtered)
    focus_vec = tfidf.transform([focus_str])
    sent_vecs = tfidf.transform(filtered)
    tfidf_sims = cosine_similarity(focus_vec, sent_vecs)[0]
    def keyword_overlap(s):
        s_words = set(re.findall(r'\b\w+\b', s.lower()))
        return sum(1 for k in focus_keywords if k in s_words)
    scores = []
    for i, s in enumerate(filtered):
        overlap = keyword_overlap(s)
        score = tfidf_sims[i] + 0.2 * overlap
        scores.append((score, i, s))
    top = sorted(scores, key=lambda x: -x[0])[:max_sentences]
    top_indices = sorted([i for _, i, _ in top])
    selected = [filtered[i] for i in top_indices]
    return ' '.join(selected).strip() 