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

def generate_output(op_directory='V_cards'):
    if not os.path.exists(op_directory):
        os.makedirs(op_directory)
        row=read_input_csv('names.csv')
        for r in row:
            filename,vcard=parse_input_csv(r)
            vcard_path=os.path.join(op_directory,filename)
            with open(vcard_path, 'w') as f:
                f.write(vcard)
            qrfile,resp=create_qr_code(r)
            print(qrfile,resp)
            vcard_path=os.path.join(op_directory,qrfile)
            with open(vcard_path, 'wb') as f:
                f.write(resp.content)

if __name__=="__main__":
    generate_output()
    
