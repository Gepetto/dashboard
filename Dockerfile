FROM python:alpine

EXPOSE 8000

RUN mkdir /app
WORKDIR /app

RUN apk update && apk add --no-cache git

ADD requirements.txt manage.py ./
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -U https://github.com/jieter/django-tables2/archive/template-makeover.zip

ADD . .

CMD ./manage.py runserver 0.0.0.0:8000
