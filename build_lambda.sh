#!/usr/bin/env bash

export PROJECT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

echo $PROJECT_ROOT
cd $PROJECT_ROOT
rm lambda1.zip
cd $PROJECT_ROOT/venv/lib/*/site-packages/
zip -r $PROJECT_ROOT/lambda.zip *
cd $PROJECT_ROOT
rm .env

if [[ $1 == "prod" ]]; then
    echo "Using prod credentials"
    cp prod_env_secret .env
else
    echo "Using dev credentials"
    cp dev_env_secret .env
fi

zip -r $PROJECT_ROOT/lambda.zip main.py .env

echo "Deploying to lambda"
aws lambda update-function-code --function-name youtubeSummarize --zip-file fileb://lambda.zip