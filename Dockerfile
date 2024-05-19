# Use the official Python image from the Docker Hub
FROM python:3.8-alpine

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install dependencies
RUN apk update \
    && apk add --no-cache --virtual .build-deps gcc libc-dev linux-headers \
    && apk add --no-cache mariadb-dev \
    && pip install --upgrade pip \
    && apk del .build-deps

# Create directories
RUN mkdir -p /app /vol/web /vol/static

# Set the working directory to /app
WORKDIR /app

# Copy the requirements file into the image
COPY ./requirements.txt /requirements.txt

# Install the Python dependencies
RUN pip install -r /requirements.txt

# Copy the application files into the image
COPY ./app /app

# Copy the entrypoint script
COPY ./scripts /scripts
RUN chmod +x /scripts/*

# Ensure that the /vol directory exists and change ownership
RUN adduser -D user
RUN chown -R user:user /vol

# Set file permissions
RUN chmod -R 755 /vol/web

# Switch to the new user
USER user

# Run the entrypoint script
ENTRYPOINT ["/scripts/entrypoint.sh"]

# Expose the port that the app runs on
EXPOSE 8001