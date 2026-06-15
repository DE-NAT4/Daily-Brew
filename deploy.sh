#!/bin/bash

set -e

aws cloudformation deploy \
  --template-file deployment-bucket-stack.yml \
  --stack-name daily-brew-deployment-stack \
  --capabilities CAPABILITY_IAM

aws cloudformation deploy \
  --template-file etl-stack.yml \
  --stack-name daily-brew-etl-stack \
  --capabilities CAPABILITY_IAM