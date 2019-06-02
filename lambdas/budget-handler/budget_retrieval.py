#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import boto3
import csv
import s3fs
import json
import logging

my_s3fs = s3fs.S3FileSystem()
toplevel_dir = "s3://financial-engine-data"
budget_data_filename = "planned-budget.csv"


def get_budget(userid):
    full_path = f"{toplevel_dir}/user_data/{userid}/{budget_data_filename}"
    with my_s3fs.open(full_path, 'r', errors='ignore') as fh:
        reader = csv.DictReader(fh)
        rows = [row for row in reader]
    return rows
