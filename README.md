# Gepetto Softwares Dashboard

## Dependencies

Get Python3.6, create a virtualenv, and install dependencies:

`pip install -U -r requirements.txt`

## Launch

```
export GITHUB_TOKEN=xxx
export GITLAB_TOKEN=xxx
export REDMINE_TOKEN=xxx
export OPENROB_TOKEN=xxx
export TRAVIS_TOKEN=xxx
./manage.py migrate
./manage.py populate
./manage.py runserver
```

You can then go to http://localhost:8000

## TODO

- fix urls (https://api.github.com/repos/stack-of-tasks/pinocchio)

## Prod

### Traefik

```
docker network create web
cd traefik
docker-compose up -d
```

### Dashboard

```
docker-compose up -d
docker-compose exec app ./manage.py collectstatic --noinput
docker-compose exec app ./manage.py migrate
```
