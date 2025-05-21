# Use official Python image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements if you have one, else install dependencies directly
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt || true

# Copy the source code
COPY . .

# Set the entrypoint to run the script
ENTRYPOINT ["python", "dockerRun.py"]