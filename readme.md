## Description
This script is scrape data from shopee like all transcation, detail transaction and shopeepay balance, this script using shopee public API do not neet register for shopee because Inused the public API that website like,
this script need to login first into some shopee account and then verify the account using link in Whatsapp (if you want to change you can change into SMS verifications) after success login will parsing the cookie and session from login and used that 2 variable to scrape the transaction and ba;ance from shopee.

## how to running this script
1. open this directory
2. install all depedensi "requirement.txt" by "pip install -r requirement.txt"
3. running the script by "python main.py"
4. input username/phone_number and password (password willbe hashed)
5. waiting for verification, open your whatapps and allow the new device to used your shopee account (integration part)
6. the script will running and get the transaction and get the first transaction to get the detail
7. the balance shopeepay will appear