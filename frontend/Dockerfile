# frontend/Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY frontend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY frontend/ .

# Streamlit config for production
ENV STREAMLIT_SERVER_ENABLE_CORS=false
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_PORT=8501

# Expose port and run Streamlit
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]
