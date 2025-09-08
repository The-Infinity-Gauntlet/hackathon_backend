# Verificar risco na imagem.
FROM python:3.13-slim 

WORKDIR /app

RUN apt-get update && apt-get upgrade -y \
	 && apt-get install -y --no-install-recommends \
		 build-essential \
		 gdal-bin \
		 libgdal-dev \
		 libspatialindex-dev \
		 libproj-dev \
		 proj-data \
		 proj-bin \
		 libgeos-dev \
		 libsqlite3-mod-spatialite \
	 && rm -rf /var/lib/apt/lists/*
COPY pyproject.toml pdm.lock ./
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal \
	C_INCLUDE_PATH=/usr/include/gdal
RUN pip install --no-cache-dir pdm && pdm install --no-lock --no-editable

COPY . .

EXPOSE 8000

CMD ["pdm", "run", "dev", "0.0.0.0:8000"]