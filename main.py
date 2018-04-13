import datetime
import os
import pandas as pd
import pint
from definitions import ROOT_DIR, Q_



# read in a dataframe that defines all the recurring money transaction
money_df = pd.read_csv(os.path.join(ROOT_DIR,'data',"test_budget.csv"))
# print str(money_df)

class Transaction(object):

	def __init__(self,f,a,t,d):
		# change to have the units recognized by pint and the + as a mathematical operation
		self.frequency = f
		self.amount = a
		self.transaction_type = t
		self.description = d
		self.parse_attributes()

	def parse_attributes(self):

		self.amount = Q_(float(self.amount.replace('$','')),'usd')

		if self.transaction_type.lower() == 'deduction':
			self.amount = self.amount*(-1.0)
		elif self.transaction_type.lower() == 'payment':
			pass

		self.frequency = Q_(self.frequency.replace('d','day').replace('w','week').replace(' ','+'))






rows = money_df.to_records()
txs_list = []
for row in rows:
	desc = row.Description
	freq = row.Occurrence
	amt = row.Amount
	tx_type = row.Type

	tx = Transaction(f=freq,a=amt,t=tx_type,d=desc)
	txs_list.append(tx)




