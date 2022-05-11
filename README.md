# AmateurBank
## Description
This web application is a simple general bank applicaiton that provides basic operations. 
Once the user successfully create the account, the user is allowed to log in.
Once the user has successfully logged in, the user is allowed to deposit money, withdraw money, and check balance.   
This bank application is deliberately injected with several types of vulnerabilities.
It has been built with flask framework with Python.

## Installation
#### Step 1 Open terminal or shell, cd to the folder you want to clone the repo 

#### Step 2 Git Clone
```$ git clone https://github.com/StellaMaUCI/AmateurBank.git ```
#### Step 3 Cd to AmateurBank directory
#### Step 4 Instantiate venv
```$ python3 -m venv venv```
#### Step 5 Activate venv 
``` $source ./venv/bin/activate```(Unix/Mac)  
``` $venv\Scripts\activate``` (Windows)
#### Step 6 Export the path
```$ export FLASK_APP=bank``` (Unix/Mac)  
```$ set instead of export``` (Windows)
#### Step 7 Enable development mode so you don't have to rerun each time editing:
```$ export FLASK_ENV=development```
#### Step 8 install dependencies as you need
```$ pip install -r "requirements.txt"```
#### Step 9 Initialize the sqlite database:
```$ flask init-db```  
Windows: if you get >error 'flask' is not recognized as an external or internal command  
stop and install flask by using   
```$pip install Flask```
After installing flask, if this is still not working, use this command   
```$python -m flask run```
#### Step 10 Run flask
```$ flask run```
#### Step 11 Open your browser, input this link to register
```http://localhost:5000/auth/register-username```  

## Requirements to use this bank
### Valid Inputs
Username should not be empty.
Username should not be the same as others.
Username and password are restricted to underscores, hyphens, dots, digits, and lowercase alphabetical characters.
Username and password are to be between 1 and 127 characters long.

Numeric inputs are positive and provided in decimal without any leading 0’s. 
Thus “42” is a valid input number but the octal “052” or hexadecimal “0x2a” are not. 
The fractional input is in decimal and is always two digits and thus can include a leading 0.

### Valid Outputs
Correct output based on different operations (e.g., registration, deposit) should be displayed on screen. 
Numbers (including potentially unbounded account balances) should be shown with full precision.
