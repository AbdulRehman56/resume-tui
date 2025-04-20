# Dockerfile

# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code into the container
# This includes main.py, resume.json, me.png
COPY . .

# IMPORTANT: Keep the container running so you can SSH into it.
# Don't run the python script directly here.
# 'sleep infinity' is a common way to do this.
CMD ["sleep", "infinity"]