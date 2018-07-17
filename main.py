import datetime
from dateutil import parser
import os
import pandas as pd
import pint
from bokeh.plotting import figure, output_file, show

from definitions import ROOT_DIR, Q_, CHECKING, CREDIT, VALID_ACCT_TYPES

import logging

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
# money_df = pd.read_csv(os.path.join(ROOT_DIR,'data',"money_io.csv"))
money_df = pd.read_csv(os.path.join(ROOT_DIR,'data',"test_budget.csv"))
accounts_df = pd.read_csv(os.path.join(ROOT_DIR,'data',"sample_account_info.csv"))
# print str(money_df)

class Account(object):
	def __init__(self,name,bal,acct_type,payback_date=None,payback_src=None,credit_limit=None):
		self.name = name
		self.balance = Q_(float(bal.replace('$','')),'usd')
		self.acct_type = acct_type.upper()
		self.payback_date = payback_date
		self.payback_src = payback_src

		self.credit_limit = credit_limit
		self._validate()

	def __repr__(self):
		return "{}: {}".format(self.name, self.balance)

	def _validate(self):
		if self.acct_type not in VALID_ACCT_TYPES:
			raise ValueError('What is this account type? {}\nMust be checking or credit'
				.format(self.acct_type))
		if self.acct_type == CREDIT:
			self.balance = self.balance*(-1.0)

			if 28 > int(self.payback_date) > 0:
				self.payback_date = int(self.payback_date)

			self.credit_limit = Q_(float(self.credit_limit.replace('$','')),'usd')

	def process_tx(self,amount_extractable_obj):

		"""
		figure out which attribute the amount is stored in
		if its a transaction object use the amount attribute
		if its an account object then use the balance attribute
		"""
		if hasattr(amount_extractable_obj,'amount'):
			amount = amount_extractable_obj.amount
		elif hasattr(amount_extractable_obj,'balance'):
			amount = amount_extractable_obj.balance

		self.balance += amount
		if self.acct_type == CREDIT:
			bal_credit_ratio = round(abs(self.balance/self.credit_limit)*100.,1)
			if bal_credit_ratio > 20:
				logger.info("{}\nbe careful, you're debt/limit ratio is {}%\n\
					anything over 20% may hurt your credit score."
					.format(self,bal_credit_ratio))

		elif self.acct_type == CHECKING:
			if self.balance < Q_(0,'usd'):
				logger.info("{} has just overdrafted.".format(self))

		# check if balance is an attribute, and update it

		if hasattr(amount_extractable_obj,"balance"):

			# don't just set to 0.0 because future functionality might pay a fraction of balance
			amount_extractable_obj.balance -= amount

			logger.debug("credit account {} was paid off".
				format(amount_extractable_obj))

	def payoff_credit_acct(self,account_object):
		"""
		modify the account_object by paying off its balance
		"""

		if account_object.acct_type == CREDIT:

			if self.acct_type == CHECKING:
				self.process_tx(account_object)

			else:
				logger.warning("Need to payoff_credt_acct with a checking account.\
					Skipping this operation.")
				return

		else:
			logger.warning("Cannot payoff_credit_acct with {} type acct.\n\
				skipping this operation."
				.format(account_object.acct_type))
			return


class Transaction(object):

	def __init__(self,f,a,t,d,sd,sc):
		# change to have the units recognized by pint and the + as a mathematical operation
		self.frequency = f
		self.amount = a
		self.transaction_type = t
		self.description = d
		self.sample_date = sd
		self.source = sc
		self._parse_attributes()

	def _parse_attributes(self):

		self.amount = Q_(float(self.amount.replace('$','')),'usd')

		if self.transaction_type.lower() == 'deduction':
			self.amount = self.amount*(-1.0)
		elif self.transaction_type.lower() == 'payment':
			pass

		self.frequency = Q_(self.frequency.replace('d','day').replace('w','week').replace(' ','+')).to('week')

		self.sample_date = parser.parse(self.sample_date)

	def should_payment_occur_today(self,datetime_object,check_cycles=55):
		"""
		Given a datetime object determine if this transaction
		would have occurred on a given date
		function does some math based on the sample date provided
		and the frequency indicated
		TODO: this is slow and inefficient
		:param check_cycles: number of occurrences (in weeks) to check in either direction from sample date 
		"""

		cycles = range(check_cycles)
		dtc = datetime_object.day
		mtc = datetime_object.month
		ytc = datetime_object.year

		for occ in cycles:

			forward = self.sample_date + self.frequency*occ
			backward = self.sample_date - self.frequency*occ

			if ((backward.day == dtc)
			and (backward.month == mtc)
			and (backward.year == ytc)):
				return True
			elif (forward.day == dtc) and (forward.month == mtc) and (forward.year == ytc):
				return True
			else:
				continue

		return False


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

	accts_dict[acctname] = Account(
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

	tx = Transaction(
		f=freq,
		a=amt,
		t=tx_type,
		d=desc,
		sd=samp_d,
		sc=src)
	# print tx.frequency
	txs_list.append(tx)



# TODO make this a command line argument beloved
DAYS_TO_PROJECT = 50
now = datetime.datetime.now()
tings2plot = []
days = range(DAYS_TO_PROJECT)

acct_lines = {}
# This the actual simulation running through days
for day in days:
	simulated_day = now + Q_(day,'day')
	for tx in txs_list:
		if tx.should_payment_occur_today(simulated_day):
			logger.debug("Paying {} Today\nSample Date: {}\nSimulated Day:{}\n"
				.format(tx.description,tx.sample_date,simulated_day))

			logger.debug("From Acct: {}".format(tx.source))

			try:
				acct_obj = accts_dict[tx.source]
			except KeyError:
				raise KeyError("Transaction Source {} is not an account in {}"
					.format(tx.source,accts_dict.keys()))
			
			acct_obj.process_tx(tx)
	# check all the accounts and see if its a payoff date
	for acct_obj in accts_dict.values():
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
p = figure(width=800, height=250, x_axis_type="datetime")


for act_name,act_line in acct_lines.items():
	# make a line of x,y values for each account
	clr = 'red'
	if accts_dict[act_name].acct_type == CHECKING:
		clr = 'green'

	p.line([x[0] for x in act_line],[x[1].magnitude for x in act_line],color=clr,legend=act_name)


# p.line([x[0] for x in tings2plot],[x[1].magnitude for x in tings2plot])

show(p)



p_total = figure(width=800, height=250, x_axis_type="datetime")
p_total.line([x[0] for x in tings2plot],[x[1].magnitude for x in tings2plot],color='blue',legend='total balance')
show(p_total)








