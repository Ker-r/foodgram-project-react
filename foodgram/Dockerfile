FROM python:3.7-slim

WORKDIR /app

COPY foodgram/requirements.txt pwd

RUN pip3 install --upgrade pip && pip3 install -r /app/foodgram/requirements.txt --no-cache-dir

COPY . .

CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000" ]
