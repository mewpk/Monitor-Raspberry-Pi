FROM python:3.11-slim

WORKDIR /app

# Install necessary packages for camera and Python
RUN apt-get update && \
    apt-get install -y python3-pip && \
    apt-get install -y python3-dev python3-setuptools && \
    apt-get install -y libatlas-base-dev && \
    apt-get clean

# Copy the requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

COPY . .

EXPOSE 5555

# Command to run the application
CMD ["python", "app.py"]
