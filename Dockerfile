# Use Python 3.13.5 official image
FROM python:3.13.5-slim

# Avoid interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget unzip curl gnupg ca-certificates \
    unixodbc-dev libssl3 libglib2.0-0 libnss3 libgconf-2-4 \
    libfontconfig1 libxss1 libappindicator3-1 libasound2 libxtst6 \
    xdg-utils fonts-liberation \
  && apt-get clean

# Install Chrome
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    dpkg -i google-chrome-stable_current_amd64.deb || apt-get -fy install && \
    rm google-chrome-stable_current_amd64.deb

# Add Microsoft GPG key
RUN mkdir -p /etc/apt/keyrings && \
    curl -sSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > /etc/apt/keyrings/microsoft.gpg

# Add Microsoft SQL Server ODBC 18 repo
RUN echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/microsoft.gpg] https://packages.microsoft.com/debian/12/prod bookworm main" \
    > /etc/apt/sources.list.d/mssql-release.list

# Install ODBC driver
RUN apt-get update && ACCEPT_EULA=Y apt-get install -y --no-install-recommends msodbcsql18 && apt-get clean

# Copy your local source code into the container (GitHub already pulled it to the VM)
COPY . /app/sports

# Set working directory
WORKDIR /app/sports

# Install Python packages
RUN pip install -r requirements.txt