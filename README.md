# CSV to vCard Converter

## Overview

This script converts data from table to individual vCards (VCF format) and QR codes in png format for each person and organizes them in a user-specified folder.

## Features

- Reads data from a CSV file.
- Generates tables based on table data create vcard and QR codes for each person.
- Saves vCards in VCF format and QR codes in png.
- Generate leave table based on this data create live summary.

## Requirements

- [Python](https://www.python.org/) 

## Usage

1. Clone the repository:

   git clone https://github.com/your-username/csv-to-vcard-converter.git

## How to run

- `python3 gen_vcard.py names.csv V_card -i db initdb` -Initialise the database.

- `python3 gen_vcard.py -i db import names.csv` -Import entries from the CSV file

- `python3 gen_vcard.py -i db query 10` -Get information for a single employee

- `python3 gen_vcard.py -i db query 11 --vcard` -Get information for a single employee with vcard


