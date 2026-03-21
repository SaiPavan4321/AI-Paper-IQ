FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install spaCy model properly
RUN python -m spacy download en_core_web_sm

# Copy all project files
COPY . .
COPY .streamlit /app/.streamlit

# Set environment variables for HF Spaces
ENV STREAMLIT_HOME=/tmp/.streamlit
ENV HF_HOME=/tmp/huggingface
ENV TMPDIR=/tmp
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
ENV STREAMLIT_SERVER_PORT=7860
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

EXPOSE 7860

HEALTHCHECK CMD curl --fail http://localhost:7860/_stcore/health

CMD ["streamlit", "run", "App.py", "--server.port=7860", "--server.address=0.0.0.0"]
