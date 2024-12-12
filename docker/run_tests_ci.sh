#!/bin/bash
#######################################################
# ABOUT THIS SCRIPT
#
# CI script for reliably running clean tests with current boxes
#
# Continuously builds assets using the included node container
# Doesn't seem to stop properly with ctrl-c
# use "docker stop <box_name>" to kill it
#######################################################
set -e
set -o xtrace

DCTEST="docker compose -f docker-compose.yml -f docker-compose.override.test.yml"

$DCTEST pull --ignore-pull-failures app fakes3_test

# annoying workaround to get host mounted file ownership mapped to the user inside the container
docker run --rm \
  --mount type=bind,source="$(pwd)/../",target=/source,bind-nonrecursive=true \
  alpine:latest find /source -path /source/.git -prune -o -exec chown 1000 {} +

# install php deps
$DCTEST run -T --rm --no-deps app composer install --no-progress

# run linter
source run_tests_lint.sh

# install widgets and run tests
source run_tests_coverage.sh

# turn off failure stop on error
set +e

# stop and remove docker containers
$DCTEST rm --force --stop
