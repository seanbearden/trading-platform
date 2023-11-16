#!/bin/bash
# Set DOCKER_HOST and run sam build
DOCKER_HOST=unix:///Users/seanbearden/.docker/run/docker.sock sam build --use-container -t template.yaml
# Validate the SAM template
sam validate
# Set DOCKER_HOST and run sam deploy
DOCKER_HOST=unix:///Users/seanbearden/.docker/run/docker.sock sam deploy --guided
