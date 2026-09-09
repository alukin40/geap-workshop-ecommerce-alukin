# Lean image for the returns-desk A2A mock (python:3.12-slim + ADK). Same idea as mocks/inventory-mcp:
# a small image starts faster on Cloud Run than the generic buildpack image.
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY agent.py .
ENV PYTHONUNBUFFERED=1
CMD ["python", "agent.py"]
