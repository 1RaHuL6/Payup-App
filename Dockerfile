
FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app


COPY thrift_requirements.txt .


RUN pip install --no-cache-dir -r thrift_requirements.txt


COPY timestamp.thrift .
COPY timestampthrift.py .


EXPOSE 10000


CMD ["python", "timestampthrift.py"]