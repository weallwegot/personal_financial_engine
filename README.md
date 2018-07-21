# personal_financial_engine
program to forecast the amount of money youll have at a certain date


## Inputs

#### *A budget*

|                      |          |            |           |             |             |         | 
|----------------------|----------|------------|-----------|-------------|-------------|---------| 
| Description          | Amount   | Occurrence | Type      | Sample_Date | Source      | Until   | 
| Rent                 | $780.00  | 30d        | Deduction | 4/1/18      | WF_Checking |         | 
| Car Payment          | $300.00  | 30d        | Deduction | 3/15/18     | WF_Checking |         | 
| School Loans         | $450.00  | 30d        | Deduction | 2/11/18     | WF_Checking |         | 
| Cell Phone Bill      | $60.00   | 30d        | Deduction | 3/1/18      | WF_Checking |         | 
| Car Insurance        | $150.00  | 30d        | Deduction | 3/4/18      | WF_Checking |         | 
| Gym Membership       | $30.00   | 30d        | Deduction | 4/2/18      | WF_Checking |         | 
| Amazon Prime Student | $49.00   | 365d       | Deduction | 5/18/17     | WF_Checking |         | 
| HBO thru Amazon      | $15.00   | 4w 2d      | Deduction | 6/19/17     | WF_Checking |         | 
| Apple Music          | $15.99   | 4w 2d      | Deduction | 3/1/18      | WF_Checking |         | 
| iCloud Storage       | $1.99    | 4w 2d      | Deduction | 3/2/18      | WF_Checking |         | 
| Electricity Bill     | $60.00   | 4w 2d      | Deduction | 1/14/17     | CitiCredit  |         | 
| Locs Retwist         | $100.00  | 4w 2d      | Deduction | 4/1/17      | WF_Credit   |         | 
| Hair cut             | $30.00   | 2w 1d      | Deduction | 6/1/18      | CitiCredit  |         | 
| Groceries            | $65.00   | 30d        | Deduction | 2/22/18     | CitiCredit  |         | 
| Eating Out           | $50.00   | 1w         | Deduction | 4/11/18     | CitiCredit  |         | 
| Gas for Car          | $40.00   | 3w         | Deduction | 4/1/18      | CitiCredit  |         | 
| School Applications  | $295.00  | 4w         | Deduction | 7/18/18     | WF_Checking | 8/18/18 | 
| My Paycheck          | $1500.00 | 2w         | Payment   | 4/16/18     | WF_Checking |         | 



#### *Starting Point for Accounts*

|             |         |          |           |              |             | 
|-------------|---------|----------|-----------|--------------|-------------| 
| AccountName | Balance | Type     | PayoffDay | PayoffSource | CreditLimit | 
| WF_Checking | $100    | Checking | N/A       | N/A          | N/A         | 
| WF_Credit   | $20     | Credit   | 3         | WF_Checking  | $3000       | 
| CitiCredit  | $500    | Credit   | 15        | WF_Checking  | $10000      | 




## Output

just run the following from the root directory:

`python main.py -m data/test_budget.csv -a data/sample_account_info.csv -f 60`

- f is for forecast and indicates the number of days to project into the future (f for forecast).
- m is the path to the your csv that contains your data (m for money)
- a is argument for the path to your simple account info (a for account).


<img width="817" alt="account balances over time" src="https://user-images.githubusercontent.com/13176059/42800327-5a6497b8-8969-11e8-9d76-9d177b388a37.png">




## Contributing

Its still pretty early but if you have suggestions, thoughts, feedback, criticism, etc feel free to open a PR or submit an Issue. 

Thanks in advance :blush:

& Thanks to [this nifty tool](https://donatstudio
.com/CsvToMarkdownTable) for csv -> markdown made easy.

--------------------------------------------------------------------------

#### Donating

If ya feeling generous, hollr @ the kid :heart:

https://www.paypal.me/hijodelsol

**BTC: 3EbMygEoo8gqgPHxmqa631ZVSwgWaoCj3m**

**ETH: 0x2F2604AA943dB4E7257636793F38dD3B1808A9e7**

**LTC: MQVgzNDgw43YzyUg3XmH3jQ7L8ndVswmN3**
