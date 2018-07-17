import datetime
from dateutil import parser
import os
import pandas as pd
import pint
from bokeh.plotting import figure, output_file, show

from definitions import ROOT_DIR, Q_



# read in a dataframe that defines all the recurring money transaction
# money_df = pd.read_csv(os.path.join(ROOT_DIR,'data',"money_io.csv"))
money_df = pd.read_csv(os.path.join(ROOT_DIR,'data',"new_job_refinanced_loan.csv"))
accounts_df = pd.read_csv(os.path.join(ROOT_DIR,'data',"sample_account_info.csv"))
# print str(money_df)

class Account(object):
	def __init__(self,name,bal,acct_type,payback_date=None):
		self.name = name
		self.balance = bal
		self.acct_type = acct_type.upper()
		self.payback_date = payback_date
		self._validate()

	def _validate(self):
		if self.acct_type not in ["CHECKING","CREDIT"]:
			raise ValueError('What is this account type? {}\nMust be checking or credit'
				.format(self.acct_type))
		if self.acct_type == "CREDIT":
			self.balance = -(bal)

			if 28 > int(self.payback_date) > 0:
				self.payback_date = int(self.payback_date)



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
	accts_dict[acctname] = Account(acctname,bal,acct_type,paydate)


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

	tx = Transaction(f=freq,a=amt,t=tx_type,d=desc,sd=samp_d,sc=src)
	# print tx.frequency
	txs_list.append(tx)
	if src in accounts.keys():
		continue
	else:	
		accounts[src] = Account(src)



# TODO make this a command line argument beloved
DAYS_TO_PROJECT = 100
now = datetime.datetime.now()
tings2plot = []
days = range(DAYS_TO_PROJECT)
curr_amt = START_AMOUNT


# This the actual simulation running through days
for day in days:
	simulated_day = now + Q_(day,'day')
	for tx in txs_list:
		if tx.should_payment_occur_today(simulated_day):
			# print "Paying {} Today\nSample Date: {}\nSimulated Day:{}\n".format(tx.description,tx.sample_date,simulated_day)
			curr_amt += tx.amount

	print "Day: {}".format(simulated_day)
	print "Amount: {}".format(curr_amt)
	myliltuple = (simulated_day,curr_amt)
	tings2plot.append(myliltuple)


# create a new plot with a datetime axis type
p = figure(width=800, height=250, x_axis_type="datetime")
p.line([x[0] for x in tings2plot],[x[1].magnitude for x in tings2plot])
show(p)









