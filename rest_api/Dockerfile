FROM python:3.9

LABEL maintainer=ashish

# Set the working directory in the image
WORKDIR /app

# Copy the files from the host file system to the image file system
COPY app.py .env .

# Install the necessary packages
RUN pip install fastapi uvicorn dotenv 

#Running server at port 8000
EXPOSE 8000

# Run a command to start the application
CMD ["uvicorn", "app:app", "--host","0.0.0.0","--port", "8000"]
