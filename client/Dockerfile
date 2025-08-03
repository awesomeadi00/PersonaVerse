FROM python:3.12-alpine
WORKDIR /client
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5002
CMD ["python", "client.py"]