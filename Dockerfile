# syntax=docker/dockerfile:1

FROM debian:bullseye

# Install python3
RUN apt-get update
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y python3 python3-pip
RUN apt-get clean

# Create app directory
RUN mkdir /app
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt
RUN rm requirements.txt

# Copy files
COPY . .

# Python support
ENV PYTHONUNBUFFERED=true

# Start app
CMD ["python3", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips", "*"]
