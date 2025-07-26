FROM python:3.13.5-slim

ENV DEBIAN_FRONTEND=noninteractive

# Install system and Playwright dependencies
RUN apt-get update && apt-get install -y \
    curl wget gnupg ca-certificates \
    libglib2.0-0 libnss3 libgconf-2-4 libxss1 libappindicator3-1 \
    libasound2 libatk-bridge2.0-0 libgtk-3-0 libx11-xcb1 \
    libxcb1 libxcomposite1 libxdamage1 libxi6 \
    libfontconfig1 xdg-utils fonts-liberation \
    && apt-get clean

# Add Microsoft GPG key
RUN mkdir -p /etc/apt/keyrings && \
    curl -sSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > /etc/apt/keyrings/microsoft.gpg

# Add Microsoft SQL Server ODBC 18 repo
RUN echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/microsoft.gpg] https://packages.microsoft.com/debian/12/prod bookworm main" \
    > /etc/apt/sources.list.d/mssql-release.list

# Install ODBC driver
RUN apt-get update && ACCEPT_EULA=Y apt-get install -y --no-install-recommends \
    msodbcsql18 unixodbc-dev libssl3 && apt-get clean

# Copy your app code
COPY . /app/sports
WORKDIR /app/sports

# Install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright + dependencies
RUN playwright install --with-deps