# Use python 3.11 base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements file and install dependencies
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Accept build arguments and set as environment variables
ARG GROQ_API_KEY
ENV GROQ_API_KEY=$GROQ_API_KEY

# Expose port
EXPOSE 8000

# Set environment variables (optional defaults)
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

