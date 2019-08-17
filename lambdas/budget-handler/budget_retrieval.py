#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import json
import logging
from typing import List

import boto3
from botocore.exceptions import ClientError
import s3fs

logger = logging.getLogger()
logger.setLevel(logging.INFO)


my_s3fs = s3fs.S3FileSystem()
toplevel_dir = "s3://financial-engine-data"
budget_data_filename = "planned-budget.csv"

DATA_MAP = {'account': {
    'filename': 'account-balance.csv'

},
    'budget': {
    'filename': 'planned-budget.csv'

}}


def get_acct_names(userid: str)->List[str]:
    ACCOUNT_DATA_FILENAME = DATA_MAP['account']['filename']
    acc_path = f"{toplevel_dir}/user_data/{userid}/{ACCOUNT_DATA_FILENAME}"

    with my_s3fs.open(acc_path, 'r', errors='ignore') as a_fh:
        acc_reader = csv.DictReader(a_fh)
        account_rows = [row for row in acc_reader]

    accnames = [x['AccountName'] for x in account_rows]
    return accnames


def get_budget(userid: str, entity: str)-> List[str]:
    data_config = DATA_MAP[entity]
    full_path = f"{toplevel_dir}/user_data/{userid}/{data_config['filename']}"

    try:
        account_names = get_acct_names(userid)
    except ClientError:
        logger.warning("Missing the account information for {userid}")
        return {"Error": "Missing the account information for user"}

    try:
        with my_s3fs.open(full_path, 'r', errors='ignore') as fh:
            reader = csv.DictReader(fh)
            rows = [row for row in reader]
    except (ClientError, FileNotFoundError):
        logger.warning(f"There was an error opening {full_path}")
        return {"AccountNames": account_names, "Error": "Missing the budget information for user"}

    return {"BudgetItems": rows, "AccountNames": account_names}
