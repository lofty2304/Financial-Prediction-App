# Use a specific Python base image (Python 3.10 is stable and avoids ImpImporter issue)
FROM python:3.10-slim-buster

# Set the working directory in the container
WORKDIR /app

# Install system dependencies required for 'ta' and other potential packages
# 'build-essential' provides compilers (gcc, g++)
# 'python3-dev' provides Python header files needed for C extensions
# Implementing a retry mechanism for apt-get update to handle transient network issues
RUN for i in $(seq 1 5); do \
    apt-get update --fix-missing && break || sleep 5; \
done && \
    apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev && \
    apt-get clean && \
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
