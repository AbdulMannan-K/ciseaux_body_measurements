FROM python:3.11.1

# Install OS dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libffi-dev \
    libopenblas-dev \
    gfortran \
    python3-dev \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

CMD ["flask", "run"]
