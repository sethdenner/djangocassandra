#!/bin/bash
rm data
docker-compose kill
docker-compose rm --force
