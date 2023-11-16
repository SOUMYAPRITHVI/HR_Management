import argparse
import csv
import logging
import os  
import requests

logger=None

def parse_args():
    parser=argparse.ArgumentParser(prog="gen_vcard.py",description="Generates sample names")
    parser.add_argument("ipfile",help="names.csv")
    parser.add_argument("-v", "--verbose", help="Print detailed logging", action='store_true', default=False)
    parser.add_argument("-n", "--number", help="Number of records to generate", action='store', type=int, default=10)
    parser.add_argument("-d", "--dimension", help="Change dimension of QRCODE", default=200 )
    args=parser.parse_args()
    return args
def setup_logging(log_level):
    global logger
    logger=logging.getLogger("SheetGen")
    handler=logging.StreamHandler()
    fhandler=logging.FileHandler("run.log")
    fhandler.setLevel(logging.DEBUG)
    handler.setLevel(log_level)
    handler.setFormatter(logging.Formatter("[%(levelname)s] %(asctime)s | %(filename)s:%(lineno)d | %(message)s"))
    fhandler.setFormatter(logging.Formatter("[%(levelname)s] %(asctime)s | %(filename)s:%(lineno)d | %(message)s"))
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    logger.addHandler(fhandler)

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
def file_exists(filename):
    if not os.path.exists(filename) or not os.path.isfile(filename):
        logger.error("%s input file not exists",filename)
        exit(1)
def is_csv_file(filename):
    return filename.endswith('.csv')
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

def create_qr_code(row,dimension):
    lname,fname,title,email,phone=row
    url=f"https://chart.googleapis.com/chart?cht=qr&chs={dimension}x{dimension}&chl={email}"
    resp=requests.get(url)
    qr_file=f'{fname[:1]}{lname}.qr.png'
    return qr_file,resp

def generate_output(number,dimension,op_directory='V_cards'):
    if not os.path.exists(op_directory):
        os.makedirs(op_directory)
        row=read_input_csv('names.csv')
        count=1
        for r in row:
            filename,vcard=parse_input_csv(r)
            vcard_path=os.path.join(op_directory,filename)
            with open(vcard_path, 'w') as f:
                f.write(vcard)
            qrfile,resp=create_qr_code(r,dimension)
            vcard_path=os.path.join(op_directory,qrfile)
            with open(vcard_path, 'wb') as f:
                f.write(resp.content)
            if count==number:
                break
            count+=1
        return f"Successfully created the first {count} person files, each with a QR code sized at {dimension}. "
    else:
        return "The output folder already exists "
        
def main():
    args=parse_args()
    if args.verbose:
        setup_logging(logging.DEBUG)
    else:
        setup_logging(logging.INFO)
        
    file_exists(args.ipfile) #checks if file exists
    logger.info(generate_output(args.number,args.dimension))
if __name__=="__main__":
    main()
    
