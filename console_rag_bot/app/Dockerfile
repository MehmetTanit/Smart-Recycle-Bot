FROM python:3.12-slim
RUN apt-get update && apt-get upgrade -y
WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app
CMD ["python", "chatbot.py"]
