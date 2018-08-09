import datetime
import argparse
from dateutil import parser
import os
import pandas as pd
import pint

import plotly.offline as pltly
import plotly.graph_objs as go

from definitions import ROOT_DIR, Q_, CHECKING, CREDIT, FOREVER_RECURRING

from fihnance import account, transaction

import logging

argparser = argparse.ArgumentParser(description='Forecasting acoount balance based on budget.')
argparser.add_argument('--forecast','-f', required=True, type=int, help='how many days to forecast account balances')
argparser.add_argument('--money','-m', required=True, type=str, help='csv file with transaction specifications')
argparser.add_argument('--account','-a', required=True, type=str, help='csv file with account balances')

args = argparser.parse_args()

logger = logging.getLogger('finance_app')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler('finance_app.log')
fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)

# read in a dataframe that defines all the recurring money transaction
money_df = pd.read_csv(args.money)
# read in dataframe that contains account information
accounts_df = pd.read_csv(args.account)


# Initialize Account Objects
accts_dict = {}
acct_rows = accounts_df.to_records()
for acct in acct_rows:
	acctname = acct.AccountName
	bal = acct.Balance
	acct_type = acct.Type
	paydate = acct.PayoffDay
	paysrc = acct.PayoffSource
	climit = acct.CreditLimit

	accts_dict[acctname] = account.Account(
		name=acctname,
		bal=bal,
		acct_type=acct_type,
		payback_date=paydate,
		payback_src=paysrc,
		credit_limit=climit)


# Initialize Transaction Objects
rows = money_df.to_records()
txs_list = []
accounts = {}
for row in rows:
	desc = row.Description
	freq = row.Occurrence
	amt = row.Amount
	tx_type = row.Type
	samp_d = row.Sample_Date
	src = row.Source
	until = row.Until

	tx = transaction.Transaction(
		f=freq,
		a=amt,
		t=tx_type,
		d=desc,
		sd=samp_d,
		sc=src,
		u=until)
	txs_list.append(tx)

DAYS_TO_PROJECT = args.forecast
now = datetime.datetime.now()
tings2plot = []
days = range(DAYS_TO_PROJECT)

acct_lines = {}
aggregate_df = pd.DataFrame()
# This the actual simulation running through days
for day in days:
	txs_occurring_today = []
	# use units to add one day per iteration
	simulated_day = now + Q_(day,'day')
	# loop through all the available transactions
	for tx in txs_list:
		# determine if a transaction should occur on simulated day
		if tx.should_payment_occur_today(simulated_day):
			logger.debug("Paying {} Today\nSample Date: {}\nSimulated Day:{}\n"
				.format(tx.description,tx.sample_date,simulated_day))

			logger.debug("From Acct: {}".format(tx.source))

			# attempt to grab the account that the transactions is coming from or into or both.
			try:
				acct_obj = accts_dict[tx.source]
			except KeyError:
				raise KeyError("Transaction Source {} is not an account in {}"
					.format(tx.source,accts_dict.keys()))
			# take the money from the account it is coming from
			acct_obj.process_tx(tx)
			# track the transactions that happened today
			txs_occurring_today.append((tx.description,tx.source))



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
					.format(acct_obj.payback_src,accts_dict.keys()))

			# this function modifies both accounts in place
			payback_src_acct.payoff_credit_acct(acct_obj)

	logger.info("Day: {}".format(simulated_day))
	logger.info("Amount: {}".format(accts_dict.values()))


	acct_data = []
	acct_names = []
	for acc in accts_dict.values():
		acct_data.append(acc.balance.magnitude)
		acct_names.append(acc.name)

	# create a row to concatenate to dataframe
	datalist = [simulated_day,txs_occurring_today]
	col_list = ['date','transactions']
	# extend modifies list in place
	datalist.extend(acct_data)
	col_list.extend(acct_names)
	newrow = pd.DataFrame([datalist]
		,columns=col_list)

	# pandas dataframe append method returns a dataframe (vs. list append which modifies in place)
	aggregate_df = aggregate_df.append(newrow,ignore_index=True)

traces2plot = []
# make money a float not a string
def specify_txs(txs_tuples_list,account_name):
	"""Reduce the original tuple list to only include transactions
	that acorrespond to the account_name passed in
	
	Args:
	    txs_tuples_list (string): string of list of tuples
	    account_name (string): account name string
	
	Returns:
	    str: string with transaction for a particular account only
	"""

	reduced_list_of_tuples = [tx_tuple for tx_tuple in txs_tuples_list if tx_tuple[1] == account_name]

	logger.debug("\noriginal list of tuples\n {}\nAcct Name {}".format(txs_tuples_list,account_name))
	logger.debug("\nreduced list of tuples! {}".format(reduced_list_of_tuples))

	return str(reduced_list_of_tuples).replace('[','').replace(']','')

# TODO: add a trace for the total, maybe
for curract in accts_dict.keys():
	acct_specific_txs = [specify_txs(tx,curract) for tx in aggregate_df['transactions']]
	new_col_name = curract+'transactions'
	aggregate_df[new_col_name] = acct_specific_txs
	traceAcct = go.Scatter(x=aggregate_df['date']
		,y=aggregate_df[curract].values,
		mode='lines',
		name=curract,
		text=aggregate_df[new_col_name])
	traces2plot.append(traceAcct)


layout = go.Layout(
    title='My Money',
    xaxis=dict(
        title='Date',
        titlefont=dict(
            family='Courier New, monospace',
            size=18,
            color='#7f7f7f'
        )
    ),
    yaxis=dict(
        title='Account Total ($)',
        titlefont=dict(
            family='Courier New, monospace',
            size=18,
            color='#7f7f7f'
        )
    )
)

fig = go.Figure(data=traces2plot, layout=layout)
pltly.plot(fig)











