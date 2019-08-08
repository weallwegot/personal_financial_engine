#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import boto3
import csv
import io
import s3fs
import json
import logging


logger = logging.getLogger()
logger.setLevel(logging.INFO)

my_s3fs = s3fs.S3FileSystem()
toplevel_dir = "s3://financial-engine-data"
budget_data_filename = "planned-budget.csv"

BUDGET_FIELDNAMES = ["Description", "Amount", "Occurrence", "Type", "Sample_Date", "Source", "Until"]
ACCOUNT_FIELDNAMES = ["AccountName", "Balance", "Type", "PayoffDay", "PayoffSource", "CreditLimit"]

s3client = boto3.client('s3')

BUCKETNAME = "financial-engine-data"

DATA_MAP = {'account': {
    'filename': 'account-balance.csv',
    'fieldnames': ACCOUNT_FIELDNAMES,
    'bodykey': 'AccountData'

},
    'budget': {
    'filename': 'planned-budget.csv',
    'fieldnames': BUDGET_FIELDNAMES,
    'bodykey': 'BudgetData'

}}


def place_budget(userid: str, post_body: dict, entity: str) -> int:

    data_config = DATA_MAP[entity]
    full_path = f"{toplevel_dir}/user_data/{userid}/{data_config['filename']}"
    output = io.StringIO()
    # with my_s3fs.open(full_path, 'w') as fh:
    writer = csv.DictWriter(output, fieldnames=data_config['fieldnames'])
    writer.writeheader()
    for entry in post_body[data_config['bodykey']]:
        if set(entry.keys()) == set(data_config['fieldnames']):
            writer.writerow(entry)
        else:
            logger.warning(f"Posted Data Fields {entry.keys()} incompatible with expectations {data_config['fieldnames']}")

    s3client.put_object(Bucket="financial-engine-data",
                        Key=f"user_data/{userid}/TEST{data_config['filename']}",
                        Body=output.getvalue())

    return 100
