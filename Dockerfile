FROM python:bookworm

EXPOSE 8000

WORKDIR /app

ENV POETRY_VIRTUALENVS_IN_PROJECT=true PYTHONUNBUFFERED=1 PATH=/root/.local/bin:$PATH

CMD rm -f /opt/openrobots/etc/robotpkg.conf \
 && /srv/dashboard/robotpkg/bootstrap/bootstrap \
 && while ! nc -z postgres 5432; do sleep 1; done \
 && poetry run ./manage.py migrate \
 && poetry run ./manage.py collectstatic --no-input \
 && poetry run gunicorn \
    --bind 0.0.0.0 \
    dashboard.wsgi
RUN --mount=type=cache,sharing=locked,target=/var/cache/apt \
    --mount=type=cache,sharing=locked,target=/var/lib/apt \
    --mount=type=cache,sharing=locked,target=/root/.cache \
    apt-get update -y && DEBIAN_FRONTEND=noninteractive apt-get install -qqy --no-install-recommends \
    apt-transport-https \
    build-essential \
    gettext \
    curl \
    git \
    gnupg2 \
    graphviz \
    libffi-dev \
    libldap2-dev \
    libpq-dev \
    libsasl2-dev \
    msmtp \
    netcat-openbsd \
    python-is-python3 \
    python3-dev \
    python3-pip \
    python3-venv \
 && curl -fsSL https://download.docker.com/linux/debian/gpg | apt-key add - \
 && echo "deb [arch=amd64] https://download.docker.com/linux/debian bookworm stable" >> /etc/apt/sources.list \
 && apt-get update -qq && apt-get install -qqy docker-ce \
 && git config --global user.email "rainboard@laas.fr" \
 && git config --global user.name "rainboard.laas.fr" \
 && python -m pip install -U pip \
 && python -m pip install -U pipx \
 && python -m pipx install poetry

ADD pyproject.toml poetry.lock ./
RUN --mount=type=cache,sharing=locked,target=/root/.cache \
    poetry install --with prod --no-root --no-interaction --no-ansi

ADD . .
