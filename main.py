import datetime
import pandas as pd
import os
from definitions import ROOT_DIR


# read in a dataframe that defines all the recurring money transaction
money_df = pd.read_csv(os.path.join(ROOT_DIR,'data',"test_budget.csv"))
print str(money_df)

# 