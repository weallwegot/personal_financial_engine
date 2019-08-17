# personal_financial_engine
program to forecast the amount of money youll have at a certain date


## Inputs

#### *A budget*

|                      |          |            |           |             |                           |         |
|----------------------|----------|------------|-----------|-------------|---------------------------|---------|
| Description          | Amount   | Occurrence | Type      | Sample_Date | Source                    | Until   |
| Rent                 | $780.00  | 4w 2d      | Deduction | 4/1/18      | Chase Saphire Credit Card |         |
| Car Payment          | $300.00  | 4w 2d      | Deduction | 3/15/18     | Chase Saphire Credit Card |         |
| School Loans         | $450.00  | 4w 2d      | Deduction | 2/11/18     | Chase Saphire Credit Card |         |
| Cell Phone Bill      | $60.00   | 4w 2d      | Deduction | 3/1/18      | Chase Checking Account    |         |
| Car Insurance        | $150.00  | 4w 2d      | Deduction | 3/4/18      | Chase Checking Account    |         |
| Gym Membership       | $30.00   | 4w 2d      | Deduction | 4/2/18      | Chase Saphire Credit Card |         |
| Amazon Prime Student | $49.00   | 52w 1d     | Deduction | 5/18/17     | Chase Saphire Credit Card |         |
| HBO thru Amazon      | $15.00   | 4w 2d      | Deduction | 6/19/17     | Chase Checking Account    |         |
| Apple Music          | $15.99   | 4w 2d      | Deduction | 3/1/18      | Chase Saphire Credit Card |         |
| iCloud Storage       | $1.99    | 4w 2d      | Deduction | 3/2/18      | Chase Saphire Credit Card |         |
| Electricity Bill     | $60.00   | 4w 2d      | Deduction | 1/14/17     | Amex Delta Card           |         |
| Locs Retwist         | $100.00  | 4w 2d      | Deduction | 4/1/17      | Chase Checking Account    |         |
| Hair cut             | $30.00   | 2w 1d      | Deduction | 6/1/18      | Amex Delta Card           |         |
| Groceries            | $65.00   | 4w 2d      | Deduction | 2/22/18     | Amex Delta Card           |         |
| Eating Out           | $50.00   | 1w         | Deduction | 4/11/18     | Amex Delta Card           |         |
| Gas for Car          | $40.00   | 3w         | Deduction | 4/1/18      | Amex Delta Card           |         |
| School Applications  | $195.00  | 15d        | Deduction | 7/18/18     | Chase Saphire Credit Card | 8/18/18 |
| My Paycheck          | $1890.00 | 2w         | Payment   | 4/16/18     | Chase Checking Account    |         |



#### *Starting Point for Accounts*

|                           |         |          |           |                        |             |
|---------------------------|---------|----------|-----------|------------------------|-------------|
| AccountName               | Balance | Type     | PayoffDay | PayoffSource           | CreditLimit |
| Chase Checking Account    | $450    | Checking | N/A       | N/A                    | N/A         |
| Amex Delta Card           | $20     | Credit   | 3         | Chase Checking Account | $3000       |
| Chase Saphire Credit Card | $500    | Credit   | 15        | Chase Checking Account | $10000      |




## Output

just run the following from the `local_engine` directory:

`bash sample_run.sh`

If you observe the `local_engine/sample_run.sh` file you'll see the following:

`python main.py -f 80 -m data_for_sample/test_budget.csv -a data_for_sample/sample_account_info.csv`

- f is for forecast and indicates the number of days to project into the future (f for forecast).
- m is the path to the your csv that contains your data (m for money)
- a is argument for the path to your simple account info (a for account).


![big_finance_tool_demo](https://user-images.githubusercontent.com/13176059/43878383-dbaf88e0-9b6c-11e8-9db4-6a2485b751cd.gif)



## Contributing

Its still pretty early but if you have suggestions, thoughts, feedback, criticism, etc feel free to open a PR or submit an Issue.

Thanks in advance :blush:

& Thanks to [this nifty tool](https://donatstudio.com/CsvToMarkdownTable) for csv -> markdown made easy.

--------------------------------------------------------------------------

#### Donating

If ya feeling generous, hollr @ the kid :heart:

https://patreon.com/andcomputers

**BTC: 3EbMygEoo8gqgPHxmqa631ZVSwgWaoCj3m**

**ETH: 0x2F2604AA943dB4E7257636793F38dD3B1808A9e7**

**LTC: MQVgzNDgw43YzyUg3XmH3jQ7L8ndVswmN3**
