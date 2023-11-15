import os

import csv  
import requests

def create_vcard(lname,fname,title,email,phone):
    return f"""
BEGIN:VCARD
VERSION:2.1
N:{lname};{fname}
FN:{fname} {lname}
ORG:Authors, Inc.
TITLE:{title}
TEL;WORK;VOICE:{phone}
ADR;WORK:;;100 Flat Grape Dr.;Fresno;CA;95555;United States of America
EMAIL;PREF;INTERNET:{email}
REV:20150922T195243Z
END:VCARD
"""
def read_input_csv(csvfile):
    ret=[]
    with open(csvfile,newline='') as f:
        row = csv.reader(f)
        for r in row:
            ret.append(r)
    return ret


def parse_input_csv(row):
    lname,fname,title,email,phone=row
    vcard=create_vcard(lname,fname,title,email,phone)
    filename=f'{fname[:1]}{lname}.vcf'
    return filename,vcard

def create_qr_code(row):
    lname,fname,title,email,phone=row
    url=f"https://chart.googleapis.com/chart?cht=qr&chs=500x500&chl={email}"
    resp=requests.get(url)
    qr_file=f'{fname[:1]}{lname}.qr.png'
    return qr_file,resp

if __name__=="__main__":
    create_vcard()
    
