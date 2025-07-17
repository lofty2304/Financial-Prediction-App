# Use a specific Python base image (Python 3.10 is stable and avoids ImpImporter issue)
FROM python:3.10-slim-buster

# Set the working directory in the container
WORKDIR /app

# Install system dependencies required for 'ta' and other potential packages
# 'build-essential' provides compilers (gcc, g++)
# 'python3-dev' provides Python header files needed for C extensions
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements.txt and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY . .

# Expose the port your Flask app runs on
EXPOSE 5000

# Command to run the Flask application using Gunicorn
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000"]
