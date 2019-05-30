
import boto3
import s3fs
import json
import logging


my_s3fs = s3fs.S3FileSystem()
toplevel_dir = "s3://financial-engine-data/users/"


def respond(err, res=None):
    return {
        'statusCode': '400' if err else '200',
        'body': err.message if err else json.dumps(res),
        'headers': {
            'Content-Type': 'application/json',
            "Access-Control-Allow-Origin": "*",  # Required for CORS support to work
            "Access-Control-Allow-Credentials": True
        },
    }


def lambda_handler(event, context):
    '''Demonstrates a simple HTTP endpoint using API Gateway. You have full
    access to the request and response payload, including headers and
    status code.

    '''

    operations = {
        'GET': 'get_method()',
        'POST': 'post_method()'
    }

    operation = event['httpMethod']
    user_uid = event['requestContext']['authorizer']['claims']['sub']
    if operation in operations:
        if operation == 'GET':

            full_path = f"{toplevel_dir}/users/{user_uid}/daily-txs.csv"
            with my_s3fs.open(full_path, 'r', errors='ignore') as fl:
                my_file_lines = fl.readlines()

            return respond(err=None, res=payload)

        elif operation == 'POST':
            print("Event Body {}".format(event['body']))
            json_data = json.loads(event['body'])

            return respond(err=None, res=payload)

        return respond(err=None, res=operations[operation])

    else:
        return respond(ValueError('Unsupported method "{}"'.format(operation)))
