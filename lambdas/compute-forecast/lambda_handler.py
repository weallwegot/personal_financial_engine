#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import boto3
import csv
import json
import logging
from collections import OrderedDict
from typing import List, Tuple

my_s3fs = s3fs.S3FileSystem()
toplevel_dir = "s3://financial-engine-data"
BUDGET_DATA_FILENAME = "planned-budget.csv"
ACCOUNT_DATA_FILENAME = 'account-balance.csv'
TX_DATA_FILENAME = '.csv'
DAYS_TO_PROJECT = 250
FIELDNAMES = []


def get_data(userid: str) -> Tuple[List[OrderedDict], List[OrderedDict]]:
    data_config = DATA_MAP[entity]
    acc_path = f"{toplevel_dir}/user_data/{userid}/{ACCOUNT_DATA_FILENAME}"

    budget_path = f"{toplevel_dir}/user_data/{userid}/{BUDGET_DATA_FILENAME}"

    with my_s3fs.open(acc_path, 'r', errors='ignore') as a_fh:
        acc_reader = csv.DictReader(a_fh)
        account_rows = [row for row in acc_reader]
    with my_s3fs.open(budget_path, 'r', errors='ignore') as b_fh:
        budget_reader = csv.DictReader(b_fh)
        budget_rows = [row for row in budget_reader]

    return account_rows, budget_rows


def place_forecasted_data(userid: str, tx_data: dict) -> None:
    """
    place the data calculated in the main handler into s3
    """
    output = io.StringIO()
    # with my_s3fs.open(full_path, 'w') as fh:
    writer = csv.DictWriter(output, fieldnames=FIELDNAMES)
    writer.writeheader()
    for entry in tx_data:
        if set(entry.keys()) == set(FIELDNAMES):
            writer.writerow(entry)
        else:
            logger.warning(f"Posted Data Fields {entry.keys()} incompatible with expectations {FIELDNAMES}")

    s3client.put_object(Bucket="financial-engine-data",
                        Key=f"user_data/{userid}/TEST{TX_DATA_FILENAME}",
                        Body=output.getvalue())


def specify_txs(txs_tuples_list, account_name):
    """Reduce the original tuple list to only include transactions
    that acorrespond to the account_name passed in

    Args:
        txs_tuples_list (string): string of list of tuples
        account_name (string): account name string

    Returns:
        str: string with transaction for a particular account only
    """

    reduced_list_of_tuples = [tx_tuple for tx_tuple in txs_tuples_list if tx_tuple[1] == account_name]

    logger.debug("\noriginal list of tuples\n {}\nAcct Name {}".format(txs_tuples_list, account_name))
    logger.debug("\nreduced list of tuples! {}".format(reduced_list_of_tuples))

    return str(reduced_list_of_tuples).replace('[', '').replace(']', '')


def lambda_handler(event, context):
    '''
    Lambda that triggers on s3 put into the userdata directory
    of backend data
    '''

    userid = event['userid']
    accounts, transactions = get_data(userid)
    accts_dict = {}
    for account in account:
        acctname = account['AccountName']
        balance = account['Balance']
        account_type = account['Type']
        paydate = account['PayoffDay']
        paysrc = account['PayoffSource']
        creditlim = account['CreditLimit']

        accts_dict[acctname] = account.Account(
            name=acctname,
            bal=balance,
            acc_type=account_type,
            payback_date=paydate,
            payback_src=paysrc,
            credit_limit=creditlim)

    txs_list = []
    for tx in transactions:
        desc = tx['Description']
        freq = tx['Occurrence']
        amt = tx['Amount']
        tx_type = tx['Type']
        samp_d = tx['Sample_Date']
        src = tx['Source']
        until = tx['Until']

        tx_obj = transaction.Transaction(
            f=freq,
            a=amt,
            t=tx_type,
            d=desc,
            sd=samp_d,
            sc=src,
            u=until)
        txs_list.append(tx_obj)

    days = range(DAYS_TO_PROJECT)

    # This the actual simulation running through days
    for day in days:
        txs_occurring_today = []
        # use units to add one day per iteration
        simulated_day = now + Q_(day, 'day')
        # loop through all the available transactions
        for tx in txs_list:
            # determine if a transaction should occur on simulated day
            if tx.should_payment_occur_today(simulated_day):
                logger.debug(f"Paying {tx.description} Today\nSample Date: {tx.sample_date}\nSimulated Day:{simulated_day}\n")

                logger.debug(f"From Acct: {tx.source}")

                # attempt to grab the account that the transactions is coming from or into or both.
                try:
                    acct_obj = accts_dict[tx.source]
                except KeyError:
                    raise KeyError(f"Transaction Source {tx.source} is not an account in {accts_dict.keys()}")
                # take the money from the account it is coming from
                acct_obj.process_tx(tx)
                # track the transactions that happened today
                txs_occurring_today.append((tx.description, tx.source, tx.amount.magnitude))

        # update transaction list to only include ones that are forever recurring
        """
        Update transaction list
        This is important bc of the "until_date" attribute.
        If the current simulated day is past the until date,
        then the transaction should no longer be processed in the future.
        TODO: move this logic into transaction object itself.
        A method that takes a datetime object and compares it to
        its until_date attribute and returns a boolean of
        [tx for tx in txs_list if tx.is_active(simulated_day)]
        """
        txs_list = [tx for tx in txs_list if tx.until_date == FOREVER_RECURRING or tx.until_date > simulated_day]

        # check all the accounts and see if its a payoff date
        for acct_obj in accts_dict.values():
            # only credit accounts can get paid off
            if acct_obj.acct_type == CREDIT and simulated_day.day == acct_obj.payback_date:
                try:
                    payback_src_acct = accts_dict[acct_obj.payback_src]
                except KeyError:
                    raise KeyError("Credit Acct Payoff Source {} is not an account in {}"
                                   .format(acct_obj.payback_src, accts_dict.keys()))

                # this function modifies both accounts in place
                payback_src_acct.payoff_credit_acct(acct_obj)

        logger.info(f"Day: {simulated_day}".format(simulated_day))
        logger.info(f"Amount: {accts_dict.values()}")

        acct_data = []
        acct_names = []
        for acc in accts_dict.values():
            acct_data.append(acc.balance.magnitude)
            acct_names.append(acc.name)

        # create a row to concatenate to dataframe
        datalist = [simulated_day, txs_occurring_today]
        col_list = ['date', 'transactions']
        # extend modifies list in place
        datalist.extend(acct_data)
        col_list.extend(acct_names)
        newrow = pd.DataFrame([datalist], columns=col_list)

        # pandas dataframe append method returns a dataframe (vs. list append which modifies in place)
        aggregate_df = aggregate_df.append(newrow, ignore_index=True)

    for curract in accts_dict.keys():
        acct_specific_txs = [specify_txs(tx, curract) for tx in aggregate_df['transactions']]
        new_col_name = curract + 'transactions'
        aggregate_df[new_col_name] = acct_specific_txs

    place_forecasted_data(aggregate_df)


# with open('event.json') as f:
#     e = json.load(f)
# lambda_handler(e, {})
