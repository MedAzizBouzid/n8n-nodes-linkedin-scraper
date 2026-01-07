FROM python:3.11-slim

WORKDIR /app

# Install system dependencies FIRST (these rarely change)
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Copy ONLY requirements.txt first (for better caching)
COPY requirements.txt .

# Install Python packages (cached unless requirements.txt changes)
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers (cached unless requirements.txt changes)
RUN playwright install --with-deps chromium

# Copy application code LAST (changes most frequently)
COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
