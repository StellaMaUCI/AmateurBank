# AmateurBank
## Description
This web application is a simple general bank applicaiton that provides basic operations. 
Once the user successfully create the account, the user is allowed to log in.
Once the user has successfully logged in, the user is allowed to deposit money, withdraw money, and check balance. 
This bank application is deliberately injected with several types of vulnerabilities.
It has been built with flask framework with Python.
## Requirements
### Valid Inputs
Any input that is not valid according to the rules below should result in a string “invalid_input” that is shown on the screen.
Numeric inputs are positive and provided in decimal without any leading 0’s (should match /(0|[1-9][0-9]*)/). 
Thus “42” is a valid input number but the octal “052” or hexadecimal “0x2a” are not. 

Any reference to “number” below refers to this input specification.
Balances and currency amounts are specified as a number indicating a whole amount and a fractional input separated by a period.
The fractional input is in decimal and is always two digits and thus can include a leading 0 (should match /[0-9]{2}/).
The interpretation of the fractional amount v is that of having value equal to v/100 of a whole amount (akin to cents and dollars in US currency).
Command line input amounts are bounded from 0.00 to 4294967295.99 inclusively but an account may accrue any non-negative balance over multiple transactions.
Account names and passwords are restricted to underscores, hyphens, dots, digits, and lowercase alphabetical characters (each character should match /[_\\-\\.0-9a-z]/). Account names and passwords are to be between 1 and 127 characters long.
### Outputs
Correct output based on different operations (e.g., registration, deposit) should be displayed on screen. 
Numbers (including potentially unbounded account balances) should be shown with full precision.
## Installation
#### Step 1 Open terminal or shell, cd to the folder you want to clone the repo 

#### Step 2 Git Clone
```$ git clone https://github.com/StellaMaUCI/AmateurBank.git ```
#### Step 3 Instantiate venv
```$ python3 -m venv venv```
#### Step 4 Active venv 
``` $source ./venv/bin/activate #$venv\Scripts\activate (if on Windows)```
#### Step 5 Install dependencies
```$ pip install -r "requirements.txt"```
#### Step 6 Export the path
```$ export FLASK_APP=bank  #$set instead of export (if on Windows)```
#### Step 7 Enable development mode so you don't have to rerun each time editing:
```$ export FLASK_ENV=development```
#### Step 8 Initialize the sqlite database:
```$ flask init-db```
#### Step 9 Run flask
```$ flask run```
