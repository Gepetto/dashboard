#!/bin/bash

set -ex

source .env
./manage.py migrate
./manage.py populate
./manage.py fetch
./manage.py robotpkg
./manage.py cmake
./manage.py travis
./manage.py update
./manage.py runserver
