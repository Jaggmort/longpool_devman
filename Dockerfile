FROM  python:3.9.18-alpine

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . . 

CMD ["python", "./bot.py"]