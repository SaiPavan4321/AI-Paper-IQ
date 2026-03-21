import re
import string
import spacy
from nltk.tokenize import sent_tokenize
try:
    import fitz  # PyMuPDF
except ImportError:
    import subprocess
    subprocess.run(["pip", "install", "pymupdf"], check=True)
    import fitz

nlp = None

def text_preprocessing_pipeline(file_path: str) -> str:
    global nlp

    if nlp is None:
        nlp = spacy.load("en_core_web_sm")

    # Load text
    if file_path.lower().endswith(".pdf"):
        text = ""
        with fitz.open(file_path) as doc:
            for page in doc:
                text += page.get_text("text") + " "
    else:
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()

    # Clean text
    text = text.replace('\xa0', ' ')
    text = re.sub(r'\s+', ' ', text)
    text = text.translate(str.maketrans('', '', string.punctuation))
    text = text.lower().strip()

    sentences = sent_tokenize(text)

    doc = nlp(text)
    entities = [(ent.text, ent.label_) for ent in doc.ents]

    output = (
        "✅ TEXT PREPROCESSING COMPLETED\n\n"
        f"Total Sentences: {len(sentences)}\n\n"
        f"Sample Cleaned Text:\n{text[:1000]}...\n\n"
        f"Named Entities (first 10):\n{entities[:10]}"
    )

    return output
