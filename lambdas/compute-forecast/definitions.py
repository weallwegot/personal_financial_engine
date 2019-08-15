import os
from pint import UnitRegistry

# load up the registry to be used everywhere
ureg = UnitRegistry()
# add currency as a type of unit since it is not part of the default
ureg.define('usd = [currency]')
Q_ = ureg.Quantity


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

CREDIT = "CREDIT"
CHECKING = "CHECKING"
VALID_ACCT_TYPES = [CREDIT, CHECKING]

DEBT_RATIO = "DEBT/CREDIT RATIO HIGH"
OVERDRAFT = "CHECKING ACCOUNT OVERDRAFT"
OVERCREDIT = "BALANCE HIGHER THAN CREDIT LIMIT"

ISSUE_NOTES = {DEBT_RATIO: "FICO recommends keeping a debt to limit ratio of under 25%",
               OVERDRAFT: "Spent more money than you have in this checking account",
               OVERCREDIT: "Credit card balance exceeds your limit."}

FOREVER_RECURRING = "recurring payment like forever"
