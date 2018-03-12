# Gepetto Softwares Dashboard

## Reverse Proxy

Look at my Traefik easy setup for [dev](https://github.com/nim65s/traefik-dev) and
[prod](https://github.com/nim65s/traefik-prod)

## Configuration example

```
echo POSTGRES_PASSWORD=$(openssl rand -base64 32) >> .env
echo SECRET_KEY=$(openssl rand -base64 32) >> .env
echo EMAIL_HOST_PASSWORD=xxx >> .env
echo GITHUB_TOKEN=xxx >> .env
echo GITLAB_TOKEN=xxx >> .env
echo REDMINE_TOKEN=xxx >> .env
echo OPENROB_TOKEN=xxx >> .env
echo TRAVIS_TOKEN=xxx >> .env
```

## Launch

`docker-compose up -d`

## Populate

`docker-compose exec app ./manage.py populate`

## Create super user

`docker-compose exec app ./manage.py createsuperuser`

## TODO

- fix urls (https://api.github.com/repos/stack-of-tasks/pinocchio)
