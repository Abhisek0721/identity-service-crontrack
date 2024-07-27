# Use the official Python image from the Docker Hub
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /usr/src/app

# Install dependencies
COPY requirements.txt /usr/src/app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /usr/src/app/

# Create a user to run the application
RUN adduser --disabled-password --gecos '' djangouser

# Set ownership and permissions
RUN chown -R djangouser:djangouser /usr/src/app
USER djangouser

# Expose the port the app runs on
EXPOSE ${APP_PORT}


