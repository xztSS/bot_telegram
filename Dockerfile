FROM python:3.11-slim
RUN apt-get update && apt-get install -y libzbar0 libzbar-dev
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "qr_bot.py"]
