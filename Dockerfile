FROM python:slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

FROM builder
WORKDIR /app
CMD ["python", "main.py"]