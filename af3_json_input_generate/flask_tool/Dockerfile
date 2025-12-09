FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose the requested port
EXPOSE 19999

# Run with Gunicorn for production-like performance
# 4 workers, binding to 0.0.0.0:19999
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:19999", "app:app"]
