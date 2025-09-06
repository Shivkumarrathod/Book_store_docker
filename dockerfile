FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production
ENV PORT=5000

WORKDIR /app

# System deps for sqlite / building wheels (kept minimal)
RUN apt-get update && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements, install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Expose port
EXPOSE 5000

# Create instance folder and give permissions
RUN mkdir -p /app/instance

# Default command: use gunicorn for production
CMD ["gunicorn", "app:app", "-b", "0.0.0.0:5000", "--workers", "2", "--threads", "4"]