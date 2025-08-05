FROM python:3.13

WORKDIR /app

RUN apt-get update && apt-get install -y \
    binutils libproj-dev gdal-bin libpq-dev \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

ENTRYPOINT ["sh", "docker/prod/entrypoint.sh"]
