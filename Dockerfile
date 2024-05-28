
FROM python:3.10-slim


WORKDIR /app


COPY requirements.txt .


RUN pip install --no-cache-dir -r requirements.txt


COPY . .


RUN chmod +x start_bot.sh


VOLUME /app/data


CMD ["python3 -m src.bot"]