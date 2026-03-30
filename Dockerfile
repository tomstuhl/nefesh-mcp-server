FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY proxy.py .

ENV NEFESH_API_KEY=""
ENV NEFESH_API_URL="https://api.nefesh.ai"

CMD ["python", "proxy.py"]
