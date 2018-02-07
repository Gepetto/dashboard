#!/bin/bash

set -ex

source .env
./manage.py migrate
./manage.py populate
./manage.py delete_perso
./manage.py fetch
./manage.py delete_perso
./manage.py robotpkg
./manage.py delete_perso
./manage.py cmake
./manage.py delete_perso
./manage.py travis
./manage.py delete_perso
./manage.py update
./manage.py delete_perso
./manage.py runserver
