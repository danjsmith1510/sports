# ===============================
# ✅ DOCKERFILE (stable + headless selenium setup)
# ===============================
FROM python:3.13.5-slim

ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies
RUN apt-get update && apt-get install -y \
    wget unzip curl gnupg ca-certificates \
    libglib2.0-0 libnss3 libgconf-2-4 \
    libfontconfig1 libxss1 libappindicator3-1 libasound2 libxtst6 \
    xdg-utils fonts-liberation \
    libu2f-udev \
    chromium \
    chromium-driver \
    && apt-get clean

# Add Microsoft GPG key
RUN mkdir -p /etc/apt/keyrings && \
    curl -sSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > /etc/apt/keyrings/microsoft.gpg

# Add Microsoft SQL Server ODBC 18 repo
RUN echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/microsoft.gpg] https://packages.microsoft.com/debian/12/prod bookworm main" \
    > /etc/apt/sources.list.d/mssql-release.list

# Install ODBC driver
RUN apt-get update && ACCEPT_EULA=Y apt-get install -y --no-install-recommends msodbcsql18 unixodbc-dev libssl3 && apt-get clean

# Set environment variable to locate the correct driver
ENV CHROMEDRIVER_PATH=/usr/lib/chromium/chromedriver

# Copy source
COPY . /app/sports
WORKDIR /app/sports

# Install Python deps
RUN pip install --no-cache-dir -r requirements.txt