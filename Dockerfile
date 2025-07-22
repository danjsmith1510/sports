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

# Copy your local source code into the container (GitHub already pulled it to the VM)
COPY . /app/sports

# Set working directory
WORKDIR /app/sports

# Install Python packages
RUN pip install --upgrade pip && pip install -r requirements.txt