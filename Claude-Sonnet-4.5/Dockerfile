FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for tar command
RUN apt-get update && apt-get install -y tar && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY input.py .
COPY input_backup.py .

# Set environment variables (use secure values in production)
ENV THIRD_PARTY_API_KEY="secure_api_key_here"
ENV DB_PASSWORD="secure_db_password_here"
ENV JWT_SECRET="secure_jwt_secret_here"

# Expose Flask default port
EXPOSE 5000

# Run the application
CMD ["python", "input.py"]
