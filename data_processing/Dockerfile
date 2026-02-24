# build container: docker build -t drought-to-zarr:latest --platform linux/amd64 .
# run container  : docker run -t drought-to-zarr:latest --platform linux/amd64

# https://hub.docker.com/_/python/
FROM python:3.12-slim

# set environment variables
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PIP_ROOT_USER_ACTION=ignore
ENV PYTHONUNBUFFERED=1

# system build requirements
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libgeos-dev \
        libproj-dev \
        proj-data \
        libgdal-dev \
        gdal-bin \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy the script into the image
COPY drought_to_zarr.py .

# google looks for a callable named `function`
CMD ["python3", "drought_to_zarr.py"]