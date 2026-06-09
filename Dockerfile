FROM python:3.10-slim

# Set system environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app/src

WORKDIR /app

# Install packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY src/ ./src/

# Expose container port
EXPOSE 8000

# Create and switch to non-privileged system user for container security
RUN useradd -u 8888 appuser && chown -R appuser:appuser /app
USER appuser

# Run FastAPI app
CMD ["python", "-m", "uvicorn", "vectaflow.app:app", "--host", "0.0.0.0", "--port", "8000"]
