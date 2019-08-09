from definitions import Q_, CHECKING, CREDIT, VALID_ACCT_TYPES
import logging

from fihnance.transaction import Transaction
#from numpy import float64
from typing import Union, Optional
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# just used for type checking, not sure if this destroys the point


class AccountInterface():

    def __init__(self):
        pass


class Account(AccountInterface):

    def __init__(self,
                 name: str,
                 bal: str,
                 acct_type: str,
                 payback_date: Optional[float] = None,
                 payback_src: Optional[Union[str, float]]=None,
                 credit_limit: Optional[Union[str, float]]=None) -> None:

        self.name = name.strip().upper()
        self.balance = Q_(float(bal.replace('$', '').replace(',', '')), 'usd')
        self.acct_type = acct_type.upper()
        self.payback_date = payback_date
        self.payback_src = payback_src.strip().upper()

        self.credit_limit = credit_limit
        self._validate()

    def __repr__(self) -> str:
        return "{}: {}".format(self.name, self.balance)

    def _validate(self) -> None:
        if self.acct_type not in VALID_ACCT_TYPES:
            raise ValueError('What is this account type? {}\nMust be checking or credit'
                             .format(self.acct_type))
        if self.acct_type == CREDIT:
            self.balance = self.balance * (-1.0)

            if 28 > int(self.payback_date) > 0:
                self.payback_date = int(self.payback_date)

            self.credit_limit = Q_(float(self.credit_limit.replace('$', '').replace(',', '')), 'usd')

    def process_tx(self, amount_extractable_obj: Union[AccountInterface, Transaction]) -> None:
        """
        figure out which attribute the amount is stored in
        if its a transaction object use the amount attribute
        if its an account object then use the balance attribute
        """
        if hasattr(amount_extractable_obj, 'amount'):
            amount = amount_extractable_obj.amount
        elif hasattr(amount_extractable_obj, 'balance'):
            amount = amount_extractable_obj.balance

        self.balance += amount
        if self.acct_type == CREDIT:
            bal_credit_ratio = round(abs(self.balance / self.credit_limit) * 100., 1)
            if bal_credit_ratio > 20:
                logger.info("{}\nbe careful, you're debt/limit ratio is {}%\n\
                    anything over 20% may hurt your credit score."
                            .format(self, bal_credit_ratio))

        elif self.acct_type == CHECKING:
            if self.balance < Q_(0, 'usd'):
                logger.info("{} has just overdrafted.".format(self))

        # check if balance is an attribute, and update it

        if hasattr(amount_extractable_obj, "balance"):

            # don't just set to 0.0 because future functionality might pay a fraction of balance
            amount_extractable_obj.balance -= amount

            logger.debug("credit account {} was paid off".
                         format(amount_extractable_obj))

    def payoff_credit_acct(self, account_object: AccountInterface) -> None:
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
