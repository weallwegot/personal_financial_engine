#!/bin/bash

BUCKET_NAME_PATH=$1

echo "beginning FRONTEND deployment script" >&2
echo "deploying $BUCKET_NAME_PATH" >&2

cd parallax-template
aws s3 sync . $BUCKET_NAME_PATH --exclude "*.DS*"

echo "successfully deployed to $BUCKET_NAME_PATH" >&2