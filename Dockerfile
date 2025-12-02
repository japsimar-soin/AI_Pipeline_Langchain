# Use slimmer Python
FROM python:3.10-slim

# Avoid Python writing .pyc files and buffer stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# System deps for some libraries (qdrant client, PyPDF2 etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements early for docker layer caching
COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Expose streamlit port
EXPOSE 8501

# Streamlit config env to allow hosting in a container
ENV STREAMLIT_SERVER_RUN_ON_SAVE=false
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_ENABLE_CORS=false

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
