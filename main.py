import datetime
from dateutil import parser
import os
import pandas as pd
import pint
from bokeh.plotting import figure, output_file, show

from definitions import ROOT_DIR, Q_



# read in a dataframe that defines all the recurring money transaction
money_df = pd.read_csv(os.path.join(ROOT_DIR,'data',"test_budget.csv"))
# print str(money_df)

class Transaction(object):

	def __init__(self,f,a,t,d,sd):
		# change to have the units recognized by pint and the + as a mathematical operation
		self.frequency = f
		self.amount = a
		self.transaction_type = t
		self.description = d
		self.sample_date = sd
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


rows = money_df.to_records()
txs_list = []
for row in rows:
	desc = row.Description
	freq = row.Occurrence
	amt = row.Amount
	tx_type = row.Type
	samp_d = row.Sample_Date

	tx = Transaction(f=freq,a=amt,t=tx_type,d=desc,sd=samp_d)
	# print tx.frequency
	txs_list.append(tx)


DAYS_TO_PROJECT = 300
# checkings account vs credit card debt lmao
START_AMOUNT = Q_(2800,'usd') - Q_(3400,'usd')
now = datetime.datetime.now()
tings2plot = []
days = range(DAYS_TO_PROJECT)
curr_amt = START_AMOUNT
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









