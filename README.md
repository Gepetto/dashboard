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
./manage.py migrate
./manage.py populate
./manage.py runserver
```

You can go to http://localhost:8000
