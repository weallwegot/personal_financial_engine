#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import boto3
import csv
import json
import logging
from budget_retrieval import get_budget
from budget_placement import place_budget


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

    path = event['path']
    user_uid = event['requestContext']['authorizer']['claims']['sub']

    if path.endswith('/retrieve'):
        response = get_budget(user_uid)
        import pdb
        pdb.set_trace()
    elif path.endswith('/place'):
        response = place_budget(event)

    return respond(err=None, res=response)


with open('event.json') as f:
    e = json.load(f)
lambda_handler(e, {})
