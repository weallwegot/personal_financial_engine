import datetime
import argparse
from dateutil import parser
import os
import pandas as pd
import pint
from bokeh.plotting import figure, output_file, show
from bokeh.models import HoverTool

from definitions import ROOT_DIR, Q_, CHECKING, CREDIT, TOOLTIPS, FOREVER_RECURRING

from fihnance import account, transaction

import logging

argparser = argparse.ArgumentParser(description='Forecasting acoount balance based on budget.')
argparser.add_argument('--forecast','-f', required=True, type=int, help='how many days to forecast account balances')
args = argparser.parse_args()

logger = logging.getLogger('finance_app')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler('finance_app.log')
fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)

# read in a dataframe that defines all the recurring money transaction
money_df = pd.read_csv(os.path.join(ROOT_DIR,'data',"test_budget.csv"))
accounts_df = pd.read_csv(os.path.join(ROOT_DIR,'data',"sample_account_info.csv"))


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
# This the actual simulation running through days
for day in days:
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

	# update transaction list to only include ones that are forevor recurring
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

	# for an overall balance measure
	curr_amt = sum([acc.balance for acc in accts_dict.values()])
	myliltuple = (simulated_day,curr_amt)

	for act in accts_dict.values():
		currtuple = (simulated_day,act.balance)
		if act.name in acct_lines.keys():
			acct_lines[act.name].append(currtuple)
		else:
			acct_lines[act.name] = [currtuple]

	# update the overall balance across all accounts
	tings2plot.append(myliltuple)

# create a new plot with a datetime axis type
p = figure(width=800, height=250, x_axis_type="datetime",tooltips=TOOLTIPS)

for act_name,act_line in acct_lines.items():
	# make a line of x,y values for each account
	clr = 'red'
	if accts_dict[act_name].acct_type == CHECKING:
		clr = 'green'

	p.line([x[0] for x in act_line],[x[1].magnitude for x in act_line],color=clr,legend=act_name)

# p.line([x[0] for x in tings2plot],[x[1].magnitude for x in tings2plot])
hover = p.select(dict(type=HoverTool))
hover.tooltips = TOOLTIPS
hover.mode = 'vline'
show(p)

p_total = figure(width=800, height=250, x_axis_type="datetime",tooltips=TOOLTIPS)
p_total.line([x[0] for x in tings2plot],[x[1].magnitude for x in tings2plot],color='blue',legend='total balance')
hover = p_total.select(dict(type=HoverTool))
hover.tooltips = TOOLTIPS
hover.mode = 'vline'
show(p_total)

