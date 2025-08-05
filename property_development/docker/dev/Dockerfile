FROM python:3.13

WORKDIR /app

RUN apt-get update && apt-get install -y \
    binutils libproj-dev gdal-bin libpq-dev netcat-openbsd \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

ENTRYPOINT ["sh", "docker/dev/entrypoint.sh"]
