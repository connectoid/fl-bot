FROM python:3.10.8
RUN mkdir -p /usr/src/fl-bot
WORKDIR /usr/src/fl-bot
COPY . /usr/src/fl-bot
RUN pip install --no-cache-dir -r requirements.txt
CMD ["python", "bot.py"]