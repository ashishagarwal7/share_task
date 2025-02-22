FROM eclipse-mosquitto:latest

# Copy the files from the host file system to the image file system
COPY mosquitto.conf /mosquitto/config/mosquitto.conf

# port expose
EXPOSE 1883

# Run a command to start the application
CMD ["/usr/sbin/mosquitto","-c", "/mosquitto/config/mosquitto.conf"]
