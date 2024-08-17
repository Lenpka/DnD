# Use an official Python runtime as a parent image
FROM python:3.10-slim

RUN apt-get update && apt-get install -y ca-certificates git
RUN update-ca-certificates
RUN pip install gigachain-cli
RUN gigachain install-rus-certs || true

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file
COPY requirements.txt /app/

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . /app

# Define environment variable
ENV TELEGRAM_TOKEN=YOUR_BOT_API_TOKEN

# Run bot.py when the container launches
CMD ["python", "./src/bot.py"]