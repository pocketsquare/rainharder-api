FROM python:3.13-slim

WORKDIR /app

COPY ./api /app
COPY requirements.txt /app

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "index:app", "--host", "0.0.0.0", "--port", "8000"]