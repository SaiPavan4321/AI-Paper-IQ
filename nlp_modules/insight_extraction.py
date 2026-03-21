import re
import spacy
import subprocess
import numpy as np
from nltk.tokenize import sent_tokenize
from sentence_transformers import SentenceTransformer
from transformers import T5Tokenizer, T5ForConditionalGeneration
from sklearn.metrics.pairwise import cosine_similarity
from nlp_modules.document_ingestion import run_document_ingestion

embedder = None
nlp = None
tokenizer = None
model = None

def insight_extraction_pipeline(pdf_path: str) -> dict:
    global embedder, nlp, tokenizer, model

    if embedder is None:
        embedder = SentenceTransformer("all-MiniLM-L6-v2")
    if nlp is None:
    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
        nlp = spacy.load("en_core_web_sm")
    if tokenizer is None or model is None:
        tokenizer = T5Tokenizer.from_pretrained("t5-small", legacy=False)
        model = T5ForConditionalGeneration.from_pretrained("t5-small")

    text = run_document_ingestion(pdf_path)
    if not text or "Error" in text:
        return {"insights": [], "summary": "", "keywords": []}

    sentences = sent_tokenize(re.sub(r"\s+", " ", text))
    sentences = [s for s in sentences if len(s.split()) >= 6][:100]

    keywords_seed = [
        "results", "conclusion", "we propose", "we found",
        "performance", "accuracy", "significant"
    ]

    keyword_vec = embedder.encode(keywords_seed).mean(axis=0)
    sentence_vecs = embedder.encode(sentences)

    scores = cosine_similarity([keyword_vec], sentence_vecs)[0]
    top_idx = np.argsort(scores)[-5:][::-1]
    top_sentences = [sentences[i] for i in top_idx]

    combined = " ".join(top_sentences)

    input_ids = tokenizer.encode(
        "summarize: " + combined,
        return_tensors="pt",
        max_length=512,
        truncation=True
    )
    summary_ids = model.generate(
        input_ids,
        max_length=120,
        min_length=40,
        num_beams=4
    )
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)

    doc = nlp(combined)
    extracted_keywords = set()
    for chunk in doc.noun_chunks:
        if len(chunk.text.split()) > 1:
            extracted_keywords.add(chunk.text.lower())
    for ent in doc.ents:
        extracted_keywords.add(ent.text.lower())

    return {
        "insights": top_sentences,
        "summary": summary,
        #"keywords": list(extracted_keywords)
    }
