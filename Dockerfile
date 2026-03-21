FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    gcc \
    g++ \
    libmupdf-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first
COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir pymupdf==1.23.8 && \
    pip install --no-cache-dir -r requirements.txt

# Download spaCy model
RUN python -m spacy download en_core_web_sm

# Download NLTK data
RUN python -c "\
import nltk; \
nltk.download('punkt'); \
nltk.download('punkt_tab'); \
nltk.download('stopwords'); \
nltk.download('wordnet'); \
nltk.download('averaged_perceptron_tagger'); \
nltk.download('maxent_ne_chunker'); \
nltk.download('words'); \
nltk.download('omw-1.4'); \
"
# Copy all project files
COPY . .

# Environment variables
ENV STREAMLIT_HOME=/tmp/.streamlit
ENV HF_HOME=/tmp/huggingface
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
ENV STREAMLIT_SERVER_PORT=7860
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_MAX_UPLOAD_SIZE=200
ENV STREAMLIT_SERVER_ENABLE_STATIC_SERVING=true
ENV TMPDIR=/tmp

EXPOSE 7860

HEALTHCHECK CMD curl --fail http://localhost:7860/_stcore/health

CMD ["streamlit", "run", "App.py", "--server.port=7860", "--server.address=0.0.0.0"]
