FROM python:3.9.10

ENV PYTHONDONTWRITEBYTECODE=1

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .

RUN apt-get update && apt-get install -y ffmpeg libsm6 libxext6
RUN apt-get install --reinstall ca-certificates
RUN pip install --no-cache-dir -r requirements.txt


COPY . .

# CMD ["python", "main.py"]

# ENTRYPOINT ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--log-config", "log_config.json"]