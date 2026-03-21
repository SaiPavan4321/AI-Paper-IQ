import re
import PyPDF2
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# ---------------- GLOBAL CACHE ----------------
tokenizer = None
model = None

# -----------------------------------------------
# MODEL LOADER
# -----------------------------------------------
def load_model():
    global tokenizer, model
    if tokenizer is None or model is None:
        model_name = "facebook/bart-large-cnn"
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSeq2SeqLM.from_pretrained(model_name)


# -----------------------------------------------
# PDF TEXT EXTRACTION
# Handles any PDF — resume, textbook, paper, etc.
# -----------------------------------------------
def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        reader = PyPDF2.PdfReader(pdf_path)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + " "
    except Exception:
        return ""
    return text.strip()


# -----------------------------------------------
# TEXT CLEANING
# Works for any document type
# -----------------------------------------------
def clean_text(text):
    # Remove URLs
    text = re.sub(r'http\S+|www\S+', '', text)
    # Remove email addresses
    text = re.sub(r'\S+@\S+', '', text)
    # Remove page numbers like "Page 1 of 10" or standalone numbers
    text = re.sub(r'\bPage\s+\d+\s*(of\s*\d+)?\b', '', text, flags=re.IGNORECASE)
    # Remove repeated words (e.g. "the the" → "the")
    text = re.sub(r'\b(\w+)( \1\b)+', r'\1', text, flags=re.IGNORECASE)
    # Remove excessive whitespace and newlines
    text = re.sub(r'\s+', ' ', text)
    # Remove special/garbage characters but keep sentence punctuation
    text = re.sub(r'[^\w\s\.\,\!\?\-\(\)\:\;\'\"]+', ' ', text)
    return text.strip()


# -----------------------------------------------
# DOCUMENT TYPE DETECTOR
# Detects what kind of document the PDF is
# -----------------------------------------------
def detect_document_type(text):
    text_lower = text.lower()

    research_keywords = ["abstract", "introduction", "methodology",
                         "conclusion", "references", "proposed", "experiment",
                         "dataset", "accuracy", "performance", "results"]
    textbook_keywords = ["chapter", "section", "exercise", "definition",
                         "theorem", "figure", "table", "example", "solution",
                         "learning objectives", "summary"]
    resume_keywords = ["career objective", "education", "skills",
                       "internship", "certifications", "projects",
                       "cgpa", "experience", "achievements"]
    legal_keywords = ["whereas", "hereinafter", "clause", "agreement",
                      "terms and conditions", "party", "jurisdiction",
                      "liability", "indemnify"]
    news_keywords = ["reported", "according to", "said", "told reporters",
                     "announced", "published", "press release"]

    scores = {
        "research_paper": sum(1 for k in research_keywords if k in text_lower),
        "textbook": sum(1 for k in textbook_keywords if k in text_lower),
        "resume": sum(1 for k in resume_keywords if k in text_lower),
        "legal": sum(1 for k in legal_keywords if k in text_lower),
        "news_article": sum(1 for k in news_keywords if k in text_lower),
    }

    doc_type = max(scores, key=scores.get)
    # If no strong signal, treat as general document
    if scores[doc_type] < 2:
        return "general"
    return doc_type


# -----------------------------------------------
# SMART CHUNKING
# Splits text into overlapping chunks for better
# context preservation across any document length
# -----------------------------------------------
def chunk_text(text, chunk_size=400, overlap=50):
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = words[i:i + chunk_size]
        chunks.append(" ".join(chunk))
        i += chunk_size - overlap  # Overlap for context continuity
    return chunks


# -----------------------------------------------
# SINGLE CHUNK SUMMARIZER
# -----------------------------------------------
def summarize_chunk(chunk, max_len=130, min_len=50, beams=4):
    inputs = tokenizer.encode(
        chunk,
        return_tensors="pt",
        max_length=512,
        truncation=True
    )
    summary_ids = model.generate(
        inputs,
        max_length=max_len,
        min_length=min_len,
        num_beams=beams,
        length_penalty=2.0,
        no_repeat_ngram_size=3,
        early_stopping=True
    )
    return tokenizer.decode(summary_ids[0], skip_special_tokens=True)


# -----------------------------------------------
# DOC-TYPE AWARE SUMMARY PARAMETERS
# Different documents need different summary styles
# -----------------------------------------------
def get_summary_params(doc_type, word_count):
    params = {
        "research_paper": {
            "max_length": 200,
            "min_length": 100,
            "num_beams": 5,
            "length_penalty": 2.0,
            "chunk_size": 400,
        },
        "textbook": {
            "max_length": 250,
            "min_length": 120,
            "num_beams": 4,
            "length_penalty": 2.5,
            "chunk_size": 450,
        },
        "resume": {
            "max_length": 160,
            "min_length": 80,
            "num_beams": 6,
            "length_penalty": 2.0,
            "chunk_size": 350,
        },
        "legal": {
            "max_length": 220,
            "min_length": 100,
            "num_beams": 4,
            "length_penalty": 2.5,
            "chunk_size": 400,
        },
        "news_article": {
            "max_length": 150,
            "min_length": 60,
            "num_beams": 4,
            "length_penalty": 1.5,
            "chunk_size": 350,
        },
        "general": {
            "max_length": 180,
            "min_length": 80,
            "num_beams": 4,
            "length_penalty": 2.0,
            "chunk_size": 400,
        },
    }
    return params.get(doc_type, params["general"])


# -----------------------------------------------
# POST PROCESSING
# Cleans up the final summary output
# -----------------------------------------------
def post_process_summary(summary):
    # Fix repeated words
    summary = re.sub(r'\b(\w+)( \1\b)+', r'\1', summary, flags=re.IGNORECASE)
    # Fix spacing around punctuation
    summary = re.sub(r'\s([,\.\!\?])', r'\1', summary)
    # Ensure first letter is capitalized
    summary = summary.strip()
    if summary:
        summary = summary[0].upper() + summary[1:]
    # Remove trailing incomplete sentence fragments
    if summary and not summary[-1] in '.!?':
        last_period = max(summary.rfind('.'), summary.rfind('!'), summary.rfind('?'))
        if last_period > len(summary) * 0.6:
            summary = summary[:last_period + 1]
    return summary


# -----------------------------------------------
# MAIN PIPELINE
# Handles ANY PDF — short or long, any type
# -----------------------------------------------
def ai_summarization_pipeline(pdf_path):
    load_model()

    # Step 1: Extract raw text
    raw_text = extract_text_from_pdf(pdf_path)
    if not raw_text:
        return "No readable text found in the PDF. Please ensure the PDF contains selectable text."

    # Step 2: Clean text
    text = clean_text(raw_text)
    word_count = len(text.split())

    if word_count < 20:
        return "The document contains too little text to summarize."

    # Step 3: Detect document type
    doc_type = detect_document_type(text)
    params = get_summary_params(doc_type, word_count)

    # Step 4: Summarize based on document length

    # ---- VERY SHORT DOCUMENT (< 300 words) ----
    if word_count < 300:
        summary = summarize_chunk(
            text,
            max_len=params["max_length"],
            min_len=params["min_length"],
            beams=params["num_beams"]
        )

    # ---- MEDIUM DOCUMENT (300 - 800 words) ----
    elif word_count < 800:
        inputs = tokenizer.encode(
            text,
            return_tensors="pt",
            max_length=512,
            truncation=True
        )
        summary_ids = model.generate(
            inputs,
            max_length=params["max_length"],
            min_length=params["min_length"],
            num_beams=params["num_beams"],
            length_penalty=params["length_penalty"],
            no_repeat_ngram_size=3,
            early_stopping=True
        )
        summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)

    # ---- LONG DOCUMENT (800+ words) — Chunk + Merge ----
    else:
        chunks = chunk_text(text, chunk_size=params["chunk_size"])
        chunk_summaries = []

        for chunk in chunks:
            if len(chunk.split()) < 30:
                continue
            chunk_summary = summarize_chunk(
                chunk,
                max_len=params["max_length"],
                min_len=min(40, params["min_length"]),
                beams=params["num_beams"]
            )
            chunk_summaries.append(chunk_summary)

        # Merge all chunk summaries
        merged = clean_text(" ".join(chunk_summaries))

        # Final global summary over merged summaries
        inputs = tokenizer.encode(
            merged,
            return_tensors="pt",
            max_length=512,
            truncation=True
        )
        final_ids = model.generate(
            inputs,
            max_length=params["max_length"],
            min_length=params["min_length"],
            num_beams=params["num_beams"],
            length_penalty=params["length_penalty"],
            no_repeat_ngram_size=3,
            early_stopping=True
        )
        summary = tokenizer.decode(final_ids[0], skip_special_tokens=True)

    # Step 5: Post-process and return
    summary = post_process_summary(summary)

    # Step 6: Add document type label to output
    type_labels = {
        "research_paper": "📄 Research Paper",
        "textbook": "📚 Textbook / Academic",
        "resume": "👤 Resume / CV",
        "legal": "⚖️ Legal Document",
        "news_article": "📰 News / Article",
        "general": "📋 General Document"
    }
    label = type_labels.get(doc_type, "📋 General Document")

    return f"**Document Type Detected: {label}**\n\n{summary}"
