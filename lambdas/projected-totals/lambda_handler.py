
import boto3
import csv
import s3fs
import json
import logging


my_s3fs = s3fs.S3FileSystem()
toplevel_dir = "s3://financial-engine-data"
forecasted_data_filename = "forecasted-daily-txs.csv"
money_warnings_filename = "money-warnings.csv"
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


def process_forecast_money_reader(csv_dict_reader):
    """
    process the csv dict reader that read in the
    data for the forecasted money
    """

    rows = []

    for row in csv_dict_reader:
        day_total = sum([float(v) for k, v in row.items()
                         if k not in COLUMS_WITHOUT_ACCOUNT_TOTALS and not k.endswith('transactions')])
        row['daily_total'] = day_total
        try:
            row.pop("")
        except KeyError:
            pass

        rows.append(row)

    return rows


def process_money_warning_reader(csv_dict_reader):
    """
    process the csv dict reader that read in the
    data for the money warnings
    """

    rows = []

    for row in csv_dict_reader:
        try:
            row.pop("")
        except KeyError:
            pass

        rows.append(row)

    return rows


def retrieve_csv_data(full_path):
    """
    retrieve the forecast data

    Arguments:
        full_path {str} -- path to s3 file for forecast data
    """
    try:
        with my_s3fs.open(full_path, 'r', errors='ignore') as fh:
            #my_file_lines = fh.readlines()
            reader = csv.DictReader(fh)
            if full_path.endswith(forecasted_data_filename):
                return process_forecast_money_reader(reader)
            elif full_path.endswith(money_warnings_filename):
                return process_money_warning_reader(reader)
    except FileNotFoundError as e:
        logging.info(f"{e}")

    return None


def lambda_handler(event, _context):
    '''Demonstrates a simple HTTP endpoint using API Gateway. You have full
    access to the request and response payload, including headers and
    status code.

    '''

    operation = event['httpMethod']
    user_uid = event['requestContext']['authorizer']['claims']['sub']

    full_path_forecast = f"{toplevel_dir}/user_data/{user_uid}/{forecasted_data_filename}"
    full_path_money_warnings = f"{toplevel_dir}/user_data/{user_uid}/{money_warnings_filename}"

    forecast_data = retrieve_csv_data(full_path_forecast)
    money_warning_data = retrieve_csv_data(full_path_money_warnings)

    res_package = {"forecastData": forecast_data, "moneyWarningData": money_warning_data}

    return respond(err=None, res=res_package)

if __name__ == "__main__":
    with open('event.json') as f:
        e = json.load(f)
    # print(lambda_handler(e, {}))
