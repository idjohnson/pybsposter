# Use an official Python runtime as a parent image
FROM python:3.11-slim

RUN DEBIAN_FRONTEND=noninteractive apt update -y \
  && umask 0002 \
  && DEBIAN_FRONTEND=noninteractive apt install -y procps

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

RUN pip install --upgrade pip && \
    pip install "fastapi[standard]"

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 8000

# Define environment variable
ENV NAME=World

# Run app.py when the container launches
CMD ["fastapi", "run", "app.py"]

#harbor.freshbrewed.science/library/pybsposter:0.1.1
