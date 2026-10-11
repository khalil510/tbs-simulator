FROM python:3.12-slim

# GEOS/GDAL/PROJ are required by GeoDjango (PostGIS driver).
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgeos-c1v5 libgdal34 libproj25 curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2"]
