FROM python:3.10-slim

# Creates a group and user
RUN groupadd -r appuser && useradd -r -g appuser appuser

RUN mkdir -p /app
WORKDIR /app

# Installs dependencies
COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

# Copies application
COPY . ./

# Changes ownership of the application files to appuser
RUN chown -R appuser:appuser /app

# Uses the new user to run the application
USER appuser

EXPOSE 8086
