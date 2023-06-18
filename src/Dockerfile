FROM python:3.10-alpine

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY entrypoint.sh entrypoint.sh
COPY . ./src


RUN pip install --upgrade pip \
    && pip install -r /app/src/requirements.txt

CMD ["/bin/sh", "-c", "pwd; cd src ; gunicorn -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000"]
