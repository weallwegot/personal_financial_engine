import json
import csv
import os
import s3fs
from dateutil import parser
from datetime import datetime

# from aws_toolbox.emails.email_sender import EmailSender


def lambda_handler(event, context):

    fs = s3fs.S3FileSystem()

    expected_tx_data = os.path.join('financial-engine-data', budget_csv)
    with fs.open(expected_tx_data, 'r') as f:
        reader = csv.DictReader(f)

        txs = []
        for row in reader:
            txs.append(row)

            parsed_date = parser.parse(row['date'])
            yr = parsed_date.year
            month = parsed_date.month
            day = parsed_date.day
            now = datetime.now()
            if yr == now.year and month == now.month and day == now.day:
                print(row['transactions'])
                import pdb
                pdb.set_trace()
                for tx in json.loads(row['transactions']):
                    print(tx)

                es = EmailSender(from_address='budgets@mail.andcomputers.io')

                es.send_email(to_address=event['email'],
                              subject='Transactions For {}/{}/{}'.format(month, day, yr),
                              message=str(row['transactions']))
                break


if __name__ == '__main__':
    lambda_handler({}, {})
