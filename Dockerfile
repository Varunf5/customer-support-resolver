FROM python:3.10-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV API_BASE_URL=https://api.openai.com/v1
ENV MODEL_NAME=gpt-4
ENV HOST=0.0.0.0
ENV PORT=7860

# Default to inference for OpenEnv evaluation
# Set CMD_TYPE=flask to run Flask app instead
# Usage: docker run customer-support:latest  (runs inference)
# Usage: docker run -e CMD_TYPE=flask customer-support:latest  (runs Flask app)

RUN echo '#!/bin/bash\n\
if [ "$CMD_TYPE" = "flask" ]; then\n\
  python app.py\n\
else\n\
  python inference.py\n\
fi' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
