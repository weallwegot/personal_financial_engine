from definitions import Q_, FOREVER_RECURRING
from dateutil import parser
import logging

logger = logging.getLogger('finance_app')

class Transaction(object):

	def __init__(self,f,a,t,d,sd,sc,u):
		# change to have the units recognized by pint and the + as a mathematical operation
		self.frequency = f
		self.amount = a
		self.transaction_type = t
		self.description = d
		self.sample_date = sd
		self.source = sc
		self.until_date = u
		self._parse_attributes()

	def __repr__(self):
		return self.description

	def _parse_attributes(self):

		self.amount = Q_(float(self.amount.replace('$','')),'usd')

		if self.transaction_type.lower() == 'deduction':
			self.amount = self.amount*(-1.0)
		elif self.transaction_type.lower() == 'payment':
			pass

		self.frequency = Q_(self.frequency.replace('d','day').replace('w','week').replace(' ','+')).to('week')

		self.sample_date = parser.parse(self.sample_date)

		try:
			self.until_date = parser.parse(self.until_date)
		except TypeError:
			self.until_date = FOREVER_RECURRING



	def should_payment_occur_today(self,datetime_object,check_cycles=1):
		"""
		Given a datetime object determine if this transaction
		would have occurred on a given date
		function does some math based on the sample date provided
		and the frequency indicated
		TODO: this is slow and inefficient
		TODO: intelligent update check_cycle based on sample date and datetime_object
		:param check_cycles: number of occurrences (in weeks) to check in either direction from sample date 
		"""

		cycles = range(check_cycles)
		dtc = datetime_object.day
		mtc = datetime_object.month
		ytc = datetime_object.year

		time_delta = datetime_object - self.sample_date
		"""
		if there is more time between the sample date and current simulated day (datetime_obj) 
		than would be reachable within the check_cycles of frequency
		then update the sample_date to be further in the future
		"""
		# frequency is a quantity with units so update weeks to days before comparing integers
		range_of_time_reachable = (self.frequency*check_cycles).to('days')
		while abs(time_delta.days) > range_of_time_reachable.magnitude:
			# if time_delta days is positive, then the sample date is too far in the past, step forward
			if time_delta.days > 0:
				self.sample_date += range_of_time_reachable

			# if time_delta days is negative, then the sample date is too far in the future, step backwards
			elif time_delta.days < 0:
				self.sample_date -= range_of_time_reachable
			# update time_delta with new sample date
			time_delta = datetime_object - self.sample_date

		# TODO: this for loop is likely not needed anymore, avoiding refactoring until unit tests are set up
		for occ in cycles:

			forward = self.sample_date + self.frequency*occ
			backward = self.sample_date - self.frequency*occ

			if ((backward.day == dtc)
			and (backward.month == mtc)
			and (backward.year == ytc)):
				logger.debug("Found it on {}th occurence".format(occ))
				# update the sample date such that it always stays close to the simulated day
				self.sample_date = backward
				return True
			elif (forward.day == dtc) and (forward.month == mtc) and (forward.year == ytc):
				logger.debug("Found it on {}th occurence".format(occ))
				# update the sample date such that it always stays close to the simulated day
				self.sample_date = forward
				return True
			else:
				continue

		return False