# HR Mangement
Flask based web application for managing human resource 

## Overview

-This script converts data from table(use SQLAlchemy) to individual vCards (VCF format) and QR codes in png format for each person and organizes them in a user-specified folder.
-Then changed it to web application to handle frontend as reactJS


## Features

- Reads data from a CSV file.
- Generates tables based on table data create vcard and QR codes for each person.
- Saves vCards in VCF format and QR codes in png.
- Generate leave table based on this data create live summary.

## Requirements

- [Python](https://www.python.org/) 

## Usage

1. Clone the repository:

   git clone https://github.com/your-username/HR_Management/.git

## How to run

- `python3 gen_vcard.py names.csv V_card -i db initdb` -Initialise the database.

-`python3 gen_vcard.py --dbname newhr initdb`Initialise the database(using config).

- `python3 gen_vcard.py -i db import names.csv` -Import entries from the CSV file

- `python3 gen_vcard.py -i db query 10` -Get information for a single employee

- ` python3 gen_vcard.py query 12 --displayvcard ` -Get information for a single employee with vcard

- `python3 gen_vcard.py query --displayvcard 12 -q --opfile newtest1` -Get information for a single employee 

   with vcard and qr code

- `python3 gen_vcard.py web` -Get information as json api format and pass it to frontend


