FROM python

EXPOSE 8000

RUN mkdir /app
WORKDIR /app

ADD requirements.txt ./

RUN apt-get update -qq && apt-get install -qqy \
    git \
    libpq-dev \
    netcat-openbsd \
 && pip3 install --no-cache-dir -r requirements.txt \
    gunicorn \
    psycopg2 \
    python-memcached

ADD . .

CMD while ! nc -z postgres 5432; do sleep 1; done \
 && ./manage.py migrate \
 && ./manage.py collectstatic --no-input \
 && gunicorn \
    --bind 0.0.0.0 \
    dashboard.wsgi
