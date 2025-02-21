FROM python:alpine3.17

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 80

# Set the environment variable for Flask
ENV FLASK_APP=app.py

# Set the environment variable for Redis
ENV REDIS_HOST=redis
ENV REDIS_PORT=6379

# Run the command to start Flask app
CMD ["flask", "run", "--host=0.0.0.0", "--port=80"]
