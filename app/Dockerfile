# 1. Containerize app to create Dockerfile (done)
# 2. Build Docker image: docker build -t shiny-app:latest --platform linux/amd64 .
# 3. Run Docker container:
# docker run --platform linux/amd64 \
#   -e BUCKET_NAME=BUCKET_NAME \
#   -v ~/.config/gcloud:/root/.config/gcloud \
#   -p 8080:8080 shiny-app:latest

# https://hub.docker.com/_/python/
FROM python:3.12

# set environment variables
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PIP_ROOT_USER_ACTION=ignore

# make the app available by listening on general host and exposing the right port
ENV HOST=0.0.0.0
ENV PORT=8080
EXPOSE 8080

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy application files
COPY . /app
WORKDIR /app

# run the application
# https://docs.docker.com/reference/dockerfile/#understand-how-cmd-and-entrypoint-interact
CMD ["shiny", "run", "drought.py", "--host", "0.0.0.0", "--port", "8080"]
