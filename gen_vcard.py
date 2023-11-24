import argparse
import csv
import logging
import os 
import psycopg2 
import requests
import sys

class HRException(Exception):pass

logger=False

def parse_args():
    parser=argparse.ArgumentParser(prog="gen_vcard.py",description="Generates sample names")
    # parser.add_argument("ipfile",help="Name of the input file")
    # parser.add_argument("opfile",help="Name of the output file")
    parser.add_argument("-b","--dbname",help="Name of the database",default='HRmgt')
    parser.add_argument("-u","--dbuser",help="Username of the database")
    # subcommand initdb
    subparsers = parser.add_subparsers(dest="op")
    subparsers.add_parser("initdb", help="Initialise the database")
    
    # import csv
    import_parser = subparsers.add_parser("import", help="Import data from csv file")
    import_parser.add_argument("employees_file", help="List of employees to import")
    # fetch vcard
    query_parser = subparsers.add_parser("query", help="Get information for a single employee")
    query_parser.add_argument("--vcard", action="store_true", default=False, help="Generate vcard for employee")
    query_parser.add_argument("id", help="Employee id")
    # add leaves
    leave_parser = subparsers.add_parser("leave", help="Add leave to database")
    leave_parser.add_argument("date", type=str, help="Date of absence")
    leave_parser.add_argument("employee_id", type=int, help="Employee id of absentee")
    leave_parser.add_argument("reason", type=str, help="Reason of absence")
   
    # add designation
    designation_parser = subparsers.add_parser("designation", help="Add designation      to database")
    designation_parser.add_argument("name", type=str, help="Name of designation")
    designation_parser.add_argument("percentage", type=int, help="Percentage of employee in designation")
    designation_parser.add_argument("leaves", type=str, help="Total no. of leaves")
    
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
   
def generate_vcard(lname,fname,title,email,phone):
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
        logger.info('Database intialized successfully')
    except psycopg2.OperationalError as e:
        raise HRException(f"Database '{args.dbname}' doesn't exist")
     
def handle_import(args):
    con=psycopg2.connect(dbname=args.dbname)
    cur=con.cursor()
    cur.execute("truncate table employees restart identity cascade")
    try:
        with open(args.employees_file) as f:
            reader=csv.reader(f)
            for row in reader:
                psql="insert into employees(fname,lname,title,email,phone) values(%s,%s,%s,%s,%s)"
                cur.execute(psql,row[:5])
        con.commit()
        print("Values inserted ")
    except:
        con.rollback()
        print("Values not inserted ")
    finally:
        cur.close()
        con.close() 
def fetch_from_db(args):
    con=psycopg2.connect(dbname=args.dbname)
    cur=con.cursor()
    query=f"select e.fname, e.lname, e.email, e.phone,d.designation_name  from employees e  INNER JOIN designation d ON e.title_id = d.designation_id where e.employee_id={args.id}"
    cur.execute(query)
    fname, lname, email, phone ,designation= cur.fetchone()
    print (f"""Name        : {fname} {lname}
Designation : {designation}
Email       : {email}
Phone       : {phone}""")
    if (args.vcard):
        vcard = generate_vcard(lname, fname, designation, email, phone)
        print (f"\n{vcard}")
    con.close()

def insert_designation(args):
    con=psycopg2.connect(dbname=args.dbname)
    cur=con.cursor()
    try:
        psql="insert into designation(designation_name,percentage_of_employees,total_no_of_leaves) values(%s,%s,%s)"
        cur.execute(psql,(args.name,args.percentage,args.leaves))
        con.commit()
        print("Designation details inserted ")
    except:
        con.rollback()
        print("Designation details not inserted ")
    finally:
        cur.close()
        con.close() 

def main():
    try:
        args = parse_args()
        setup_logging(args.verbose)
        ops = {"initdb" : initialize_db,
                "import" : handle_import,
                "query" : fetch_from_db,
               
                "designation" : insert_designation,
               
                }
        
        ops[args.op](args)
    except HRException as e:
        logger.error("Program aborted, %s", e)
        sys.exit(-1)
if __name__=="__main__":
    main()
    



