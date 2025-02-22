FROM python:3.9

LABEL maintainer=ashish

# Set the working directory in the image
WORKDIR /app

# Copy the files from the host file system to the image file system
COPY mqtt_client.py .env .

# Install the necessary packages
RUN pip install gmqtt jsonschema dotenv

# Run a command to start the application
CMD ["python3", "mqtt_client.py"]
