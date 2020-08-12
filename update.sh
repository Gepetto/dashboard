#!/bin/bash -eux

git pull
docker-compose pull
docker-compose up -d
docker system prune -f
docker-compose logs -f --tail 20
