FROM python:jessie

EXPOSE 8000

RUN mkdir /app
WORKDIR /app

ADD requirements.txt ./

RUN apt-get update -qq && apt-get install -qqy \
    apt-transport-https \
    git \
    libpq-dev \
    netcat-openbsd \
 && curl -fsSL https://download.docker.com/linux/debian/gpg | apt-key add - \
 && echo "deb [arch=amd64] https://download.docker.com/linux/debian jessie stable" >> /etc/apt/sources.list \
 && apt-get update -qq && apt-get install -qqy docker-ce

RUN pip3 install --no-cache-dir -r requirements.txt \
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
