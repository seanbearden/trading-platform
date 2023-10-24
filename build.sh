#!/bin/bash

# Build the Docker image using a specific Dockerfile
docker build -t create-stock-report -f Dockerfile.report .

# Push the Docker image to Amazon ECR
aws ecr create-repository --repository-name create-stock-report
docker tag create-stock-report:latest 047672427450.dkr.ecr.us-east-1.amazonaws.com/create-stock-report:latest
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 047672427450.dkr.ecr.us-east-1.amazonaws.com
docker push 047672427450.dkr.ecr.us-east-1.amazonaws.com/create-stock-report:latest

