FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    espeak-ng \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY server.py .

# Pre-download the model weights during build to ensure fast startup at runtime
RUN python3 -c "from kokoro import KPipeline; KPipeline(lang_code='a')"

# Expose port 5000
EXPOSE 5000

# Start the server
CMD ["python", "server.py"]
