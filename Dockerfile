FROM python:slim-buster

EXPOSE 8000

WORKDIR /app

ENV PYTHONUNBUFFERED=1

RUN apt-get update -qq && apt-get install -qqy \
    apt-transport-https \
    build-essential \
    curl \
    git \
    gnupg2 \
    graphviz \
    libldap2-dev \
    libpq-dev \
    libsasl2-dev \
    netcat-openbsd \
    msmtp \
 && curl -fsSL https://download.docker.com/linux/debian/gpg | apt-key add - \
 && echo "deb [arch=amd64] https://download.docker.com/linux/debian buster stable" >> /etc/apt/sources.list \
 && apt-get update -qq && apt-get install -qqy docker-ce \
 && git config --global user.email "rainboard@laas.fr" \
 && git config --global user.name "rainboard.laas.fr"

RUN pip3 install --no-cache-dir \
    gunicorn \
    ipython \
    poetry \
    psycopg2-binary \
    python-memcached

ADD pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false --local \
 && poetry install --no-dev --no-root --no-interaction --no-ansi

ADD . .

CMD rm -f /opt/openrobots/etc/robotpkg.conf \
 && /srv/dashboard/robotpkg/bootstrap/bootstrap \
 && while ! nc -z postgres 5432; do sleep 1; done \
 && ./manage.py migrate \
 && ./manage.py collectstatic --no-input \
 && gunicorn \
    --bind 0.0.0.0 \
    dashboard.wsgi
