FROM python:3.10-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Install the package
RUN pip install -e .

# Expose the default port
EXPOSE 8080

# Default command
ENTRYPOINT ["python", "-m", "github_mcp_server"]
CMD ["http", "--port", "8080"]
