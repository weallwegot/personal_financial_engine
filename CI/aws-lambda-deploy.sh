#!/bin/bash


ISNEW=$1
RESOURCE_ROLE=$2
ALIAS=$3

FNAME=$4
HANDLER=$5
TIMEOUT=$6
MEMSIZE=$7
DESC=$8
ENV=$9
RUNTIME=${10}
REGION=${11}


echo "beginning deployment script" >&2

echo "install requirements.txt"
mkdir lambda_deployment_package
cd lambda_deployment_package
# install s3fs seperately because the dependencies are already in the lamdba env
pip install --no-deps --no-cache-dir --compile s3fs --target .
pip install --no-cache-dir --compile -r ../requirements.txt --target .


echo "zipping deployment package" >&2
zip -r9 ../function.zip .
cd ../

# get handler file name from $HANDLER variable
IFS='.' read -r HANDLER_FILE_NAME string <<< "$HANDLER"

echo "Handler Name $HANDLER_FILE_NAME" >&2

# assumes its a .py # TODO, dynamic determine or wild-card
zip -g function.zip "$HANDLER_FILE_NAME.py"




if [ $ISNEW == "True" ]
then
echo "deploying brand new function" >&2
aws lambda create-function \
    --function-name $FNAME \
    --handler $HANDLER \
    --timeout $TIMEOUT \
    --memory-size $MEMSIZE \
    --zip-file fileb://function.zip \
    --runtime $RUNTIME \
    --environment "$ENV" \
    --role "$RESOURCE_ROLE" \
    --description "$DESC" \

echo "creating/updating alias of $ALIAS" >&2
aws lambda create-alias \
    --function-name $FNAME \
    --name "$ALIAS" \
    --function-version \$LATEST

aws lambda update-alias \
    --function-name $FNAME \
    --name "$ALIAS" \
    --function-version \$LATEST


elif [ $ISNEW == "False" ]
then
echo "updating function" >&2
# update function code
aws lambda update-function-code \
    --function-name "${FNAME}" \
    --zip-file fileb://function.zip \
    --publish

# update function configuration (echo to higher than std.out so its displayed)
echo "updating function configuration" >&2

aws lambda update-function-configuration \
    --function-name "$FNAME" \
    --handler "$HANDLER" \
    --timeout "$TIMEOUT" \
    --memory-size $MEMSIZE \
    --runtime $RUNTIME \
    --environment "$ENV" \
    --role "${RESOURCE_ROLE}" \
    --description "$DESC" \

echo "creating/updating alias of $ALIAS" >&2
aws lambda create-alias \
    --function-name $FNAME \
    --name "$ALIAS" \
    --function-version \$LATEST

aws lambda update-alias \
    --function-name $FNAME \
    --name "$ALIAS" \
    --function-version \$LATEST

else
echo "not a new function. but not an old function. this line should not be hit." >&2
fi






