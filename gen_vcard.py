import argparse
import csv
import logging
import os 
import psycopg2 
import requests
import shutil

logger=None

def parse_args():
    parser=argparse.ArgumentParser(prog="gen_vcard.py",description="Generates sample names")
    parser.add_argument("ipfile",help="Name of the input file")
    parser.add_argument("opfile",help="Name of the output file")
    parser.add_argument("-b","--dbname",help="Name of the database",default='HRmgt')
    parser.add_argument("-u","--dbuser",help="Username of the database")
    
    subparsers = parser.add_subparsers(dest="op")
    subparsers.add_parser("initdb", help="initialise the database")
    
    parser.add_argument("-i","--input_type",help="Specify the data source",choices=['file','db'],required=True)
    parser.add_argument("-v", "--verbose", help="Print detailed logging", action='store_true', default=False)
    parser.add_argument("-n", "--number", help="Number of records to generate", action='store', type=int, default=10)
    parser.add_argument("-d", "--dimension", help="Change dimension of QRCODE", default=200 )
    parser.add_argument("-q", "--add_qr", help="Generate QRCODE of each record",action='store_true',default=False)
    parser.add_argument("-a", "--address", help="Change into new address",type=str, default="100 Flat Grape Dr.;Fresno;CA;95555;United States of America")
    args=parser.parse_args()
    return args

def setup_logging(is_verbose):
    global logger
    if is_verbose:
        level=logging.DEBUG
    else:
        level=logging.INFO
    logger=logging.getLogger("HR")
    handler=logging.StreamHandler()
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter("[%(levelname)s]| %(filename)s:%(lineno)d | %(message)s"))
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
   
def create_vcard(row,address):
    lname,fname,title,email,phone=row
    return f"""
BEGIN:VCARD
VERSION:2.1
N:{lname};{fname}
FN:{fname} {lname}
ORG:Authors, Inc.
TITLE:{title}
TEL;WORK;VOICE:{phone}
ADR;WORK:;;{address}
EMAIL;PREF;INTERNET:{email}
REV:20150922T195243Z
END:VCARD
"""

def file_exists(filename):
    if not os.path.exists(filename) or not os.path.isfile(filename):
        logger.error("%s input file not exists",filename)
        exit(1)

def clear_output_dir(args):
    if os.path.exists(args.opfile):
        shutil.rmtree(os.path.join(args.opfile))
        return "Folder removed"
    
def read_input_csv(csvfile):
    ret=[]
    with open(csvfile,newline='') as f:
        row = csv.reader(f)
        for r in row:
            ret.append(r)
    return ret

def parse_input_csv(row,args):
    lname,fname,title,email,phone=row
    vcard=create_vcard(lname,fname,title,email,phone,args.address)
    filename=f'{fname[:1]}{lname}.vcf'
    return filename,vcard

def create_vcard_file(row,vcard,args):
    vcard_path=os.path.join(args.opfile,f"{str(row[2][:1])}{str(row[1])}.vcf")
    with open(vcard_path, "w") as file:
        file.write(vcard)
   
def create_qr_code(row,vcard,args):
    url=f"https://chart.googleapis.com/chart?cht=qr&chs={args.dimension}x{args.dimension}&chl={args.email}"
    resp=requests.get(url)
    qr_path=os.path.join(args.opfile, f"{str(row[2][:1])}{str(row[1])}.qr.png")
    if os.path.exists(qr_path):
        logger.warning(f"File already exists: {qr_path}")
    else:
        if os.access(args.opfile, os.W_OK):
            with open(qr_path, "wb") as file:
                file.write(url.content)
                logger.info(f"Created QR code: {qr_path}")
        else:
            logger.warning(f"No write access to directory: {args.opfile}")
           
def initialize_db(args):
    with open("data/init.sql") as f:
        sql=f.read()
        logger.debug(sql)
    try:
        con=psycopg2.connect(dbname=args.dbname)
        cur=con.cursor()
        cur.execute(sql)
        con.commit()
    except psycopg2.OperationalError as e:
        logger.info(f"Database '{args.dbname}' doesn't exist")
      
def main():
    args=parse_args()
    file_exists(args.ipfile) #checks if file exists
    args = parse_args()
    setup_logging(args.verbose)
    ops = {"initdb" : initialize_db,
            
            }
    ops[args.op](args)
    data_from_db=fetch_values()
    if data_from_db:
        generate_output_from_db(data_from_db,args)
    else:
        logger.error("Failed to fetch database.")

if __name__=="__main__":
    main()
    



