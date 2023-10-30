FROM  python:3.9.18-alpine

WORKDIR /opt/longpool_devman

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . . 

CMD ["python", "./bot.py"]