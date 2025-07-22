FROM prefecthq/prefect:3-latest

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    git \
    apt-transport-https \
    unixodbc-dev \
    libssl3 \
    ca-certificates \
    && apt-get clean

# Add Microsoft GPG key
RUN mkdir -p /etc/apt/keyrings && \
    curl -sSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > /etc/apt/keyrings/microsoft.gpg

# Add Microsoft SQL Server ODBC 18 repo
RUN echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/microsoft.gpg] https://packages.microsoft.com/debian/12/prod bookworm main" \
    > /etc/apt/sources.list.d/mssql-release.list

# Install ODBC driver
RUN apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql18 && apt-get clean

# Clone your GitHub repo with flow code
RUN git clone https://github.com/danjsmith1510/sports.git /app/sports

# Install Python packages
RUN pip install -r /app/sports/requirements.txt

# Set working directory
WORKDIR /app/sports