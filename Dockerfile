# Use Python 3.10-slim-buster as the base image
FROM python:3.10-slim-buster

# Set the working directory to /app
WORKDIR /app

# Install necessary dependencies and chromium
RUN apt-get update \
    && apt-get install -y \
       curl \
       build-essential \
       cmake \
       g++ \
       libssl1.1 \
       libssl-dev \
       python3-dev \
       libc6-dev \
       chromium \
       chromium-driver \
       libnss3 \
       libx11-dev \
       libatk1.0-0 \
       libgtk-3-0 \
       libgbm1 \
       libasound2 \
       procps \
       dpkg-dev \
       bzip2 \
       libncurses6 \
       libpython3-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set the BROWSER_PATH environment variable for Chromium
ENV BROWSER_PATH=/usr/bin/chromium

# Upgrade pip, setuptools, and wheel
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Copy the requirements.txt first to optimize Docker layer caching
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the application files into /app
COPY . /app/

# Expose the port the app will run on
EXPOSE 5006

# Set the entry point for the application
CMD ["python", "app/app.py"]
