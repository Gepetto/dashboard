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
./manage.py fetch
./manage.py robotpkg
./manage.py cmake
./manage.py travis
./manage.py update
./manage.py runserver
```

or, as a shortcut, `./launch.sh`

You can go to http://localhost:8000

## TODO

- supprimer le besoin de delete_perso
- populate public/private field
- fix interaction between pagination & filtering
- retrieve dependencies
    - classify system / rpkg
    - get their version depending on the target os
- dockerfile
    - generic Vs. using dependencies
