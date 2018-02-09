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

- populate public/private field
- fix interaction between pagination & filtering
- retrieve dependencies
    - classify system / rpkg
    - get their version depending on the target os
- dockerfile
    - generic Vs. using dependencies
