# Use the official Python image from the Docker Hub
FROM python:3.8-alpine

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apk update && apk add --no-cache \
    gcc \
    libc-dev \
    linux-headers \
    mariadb-dev \
    build-base \
    python3-dev \
    musl-dev \
    libffi-dev \
    openssl-dev

# Create directories
RUN mkdir -p /app /vol/web /vol/static

# Set the working directory to /app
WORKDIR /app

# Copy the requirements file into the image
COPY ./requirements.txt /requirements.txt

# Check and print the contents of the requirements file
RUN cat /requirements.txt

# Install the Python dependencies
RUN pip install --no-cache-dir -r /requirements.txt

# Copy the application files into the image
COPY ./app /app

# Copy the entrypoint script
COPY ./scripts /scripts
RUN chmod +x /scripts/*

# Ensure that the /vol directory exists and change ownership
RUN adduser -D user
RUN mkdir -p /vol && chown -R user:user /vol

# Set file permissions
RUN chmod -R 755 /vol/web

# Switch to the new user
USER user

# Run the entrypoint script
ENTRYPOINT ["entrypoint.sh"]

# Expose the port that the app runs on
EXPOSE 8001
