# Use official lightweight Python base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Get missing package sources
RUN apt-get update && apt-get install -y \
    apt-transport-https \
    ca-certificates \
    gnupg \
    && echo "deb http://deb.debian.org/debian bookworm main contrib non-free" >> /etc/apt/sources.list \
    && echo "deb http://deb.debian.org/debian bookworm-updates main contrib non-free" >> /etc/apt/sources.list \
    && echo "deb http://security.debian.org/debian-security bookworm-security main contrib non-free" >> /etc/apt/sources.list


# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libffi-dev \
    libpq-dev \
    libpangocairo-1.0-0 \
    libpangoft2-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libcairo2 \
    libpango-1.0-0 \
    libglib2.0-0 \
    shared-mime-info \
    fonts-liberation \
    libxml2 \
    libxslt1.1 \
    libjpeg62-turbo \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your project files into the container
COPY . .

# Expose port (FastAPI uses 8000 by default)
EXPOSE 8000

# Run the FastAPI app using uvicorn
CMD ["uvicorn", "src.server.rfp_app:app", "--host", "0.0.0.0", "--port", "8000"]
