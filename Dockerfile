FROM python:3.11.8-alpine

RUN apk add --no-cache \
    build-base \
    libffi-dev \
    musl-dev \
    openblas-dev \
    gfortran \
    python3-dev

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

CMD ["flask", "run"]
