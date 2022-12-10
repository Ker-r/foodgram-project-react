FROM python:3.7-slim

WORKDIR /app

COPY foodgram/requirements.txt pwd

RUN pip install -r /app/requirements.txt

COPY . .

CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000" ]
