#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import boto3
import csv
import json
import logging
from budget_retrieval import get_budget
from budget_placement import place_budget


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
    body = json.loads(event['body'])
    path = '/retrieve' if body['RetrieveOrPlace'].endswith('retrieve') else '/place'

    entity = 'budget' if body['Entity'] else 'account'
    print(path)

    if path.endswith('/retrieve'):
        response = get_budget(user_uid, entity)
    elif path.endswith('/place'):
        response = place_budget(user_uid, body, entity)

    return respond(err=None, res=response)


# with open('event.json') as f:
#     e = json.load(f)
# lambda_handler(e, {})
