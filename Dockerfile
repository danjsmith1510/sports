# ✅ Base Python image
FROM python:3.13.5-slim

# ✅ Avoid interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# ✅ Install system dependencies
RUN apt-get update && apt-get install -y \
    wget unzip curl gnupg ca-certificates \
    unixodbc-dev libssl3 libglib2.0-0 libnss3 libgconf-2-4 \
    libfontconfig1 libxss1 libappindicator3-1 libasound2 libxtst6 \
    xdg-utils fonts-liberation git && \
    apt-get clean

# ✅ Install Google Chrome (stable channel)
RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    dpkg -i google-chrome-stable_current_amd64.deb || apt-get -fy install && \
    rm google-chrome-stable_current_amd64.deb

# ✅ Add Microsoft GPG key for SQL Server ODBC driver
RUN mkdir -p /etc/apt/keyrings && \
    curl -sSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > /etc/apt/keyrings/microsoft.gpg

# ✅ Add Microsoft SQL Server ODBC 18 repo
RUN echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/microsoft.gpg] https://packages.microsoft.com/debian/12/prod bookworm main" \
    > /etc/apt/sources.list.d/mssql-release.list

# ✅ Install ODBC Driver 18
RUN apt-get update && ACCEPT_EULA=Y apt-get install -y --no-install-recommends msodbcsql18 && apt-get clean

# ✅ Install ChromeDriver via webdriver-manager inside container
RUN pip install --no-cache-dir webdriver-manager selenium

# ✅ Copy your codebase
COPY . /app/sports

# ✅ Set working directory
WORKDIR /app/sports

# ✅ Install remaining Python requirements
RUN pip install --no-cache-dir -r requirements.txt