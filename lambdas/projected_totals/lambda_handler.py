
import boto3
import csv
import s3fs
import json
import logging


my_s3fs = s3fs.S3FileSystem()
toplevel_dir = "s3://financial-engine-data"
forecasted_data_filename = "forecasted-daily-txs.csv"
COLUMS_WITHOUT_ACCOUNT_TOTALS = ["date", "transactions"]


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

    operation = event['httpMethod']
    user_uid = event['requestContext']['authorizer']['claims']['sub']

    full_path = f"{toplevel_dir}/user_data/{user_uid}/{forecasted_data_filename}"
    with my_s3fs.open(full_path, 'r', errors='ignore') as fh:
        #my_file_lines = fh.readlines()
        reader = csv.DictReader(fh)
        rows = []

        for row in reader:
            day_total = sum([float(v) for k, v in row.items()
                             if k not in COLUMS_WITHOUT_ACCOUNT_TOTALS and not k.endswith('transactions')])
            row['daily_total'] = day_total
            row.pop("")

            rows.append(row)

    return respond(err=None, res=rows)


# with open('event.json') as f:
#     e = json.load(f)
# lambda_handler(e, {})
