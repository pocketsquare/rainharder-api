FROM python:3.13-slim

WORKDIR /app

# Copy FastAPI files
COPY ./api/. /app/

# Copy additional required files
COPY requirements.txt /app/
COPY database.py /app/
COPY .env /app/

# Install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose port 80
EXPOSE 80

# Run FastAPI via Uvicorn
CMD ["uvicorn", "index:app", "--host", "0.0.0.0", "--port", "80"]
