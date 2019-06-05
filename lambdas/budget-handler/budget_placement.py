#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import boto3
import csv
import io
import s3fs
import json
import logging

my_s3fs = s3fs.S3FileSystem()
toplevel_dir = "s3://financial-engine-data"
budget_data_filename = "planned-budget.csv"

FIELDNAMES = ["Description", "Amount", "Occurrence", "Type", "Sample_Date", "Source", "Until"]

s3client = boto3.client('s3')


def place_budget(userid: str, post_body: dict) -> None:
    full_path = f"{toplevel_dir}/user_data/{userid}/{budget_data_filename}"
    output = io.StringIO()
    # with my_s3fs.open(full_path, 'w') as fh:
    writer = csv.DictWriter(output, fieldnames=FIELDNAMES)
    writer.writeheader()
    for entry in post_body['BudgetData']:
        if set(entry.keys()) == set(FIELDNAMES):
            writer.writerow(entry)
        else:
            logger.warning(f"Posted Data Fields {entry.keys()} incompatible with expectations {FIELDNAMES}")

    s3client.put_object(Bucket="financial-engine-data",
                        Key=f"user_data/{userid}/TEST{budget_data_filename}",
                        Body=output.getvalue())

    return post_body
