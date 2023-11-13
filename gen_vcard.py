import os

import csv  

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
def generate_output(op_directory='V_cards'):
    if not os.path.exists(op_directory):
        os.makedirs(op_directory)
    with open('names.csv',newline='') as f:
        row = csv.reader(f)
        for r in row:
            lname,fname,title,email,phone=r
            vcard=create_vcard(lname,fname,title,email,phone)
            filename=f'{fname[:1]}{lname}.vcf'
            vcard_path=os.path.join(op_directory,filename)
            with open(vcard_path, 'w') as f:
                f.write(vcard)
if __name__=="__main__":
    generate_output()

