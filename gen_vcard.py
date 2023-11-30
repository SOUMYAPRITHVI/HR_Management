import argparse
import csv
import logging
import datetime
import os 
import sys
import shutil

import configparser
import psycopg2 
import requests
import sqlalchemy as sa

import db

class HRException(Exception):pass

logger=False
todays_date = str(datetime.date.today())

def parse_args():
    parser=argparse.ArgumentParser(prog="gen_vcard.py",description="Employee information manager for a small company.")
    config = configparser.ConfigParser()
    config.read('config.ini')
    # parser.add_argument("--dbname", help="Adding database name", action="store", type=str, default=config.get('Database', 'dbname'))
    parser.add_argument("-b","--dbname",help="Name of the database",default='HRmgt')
    parser.add_argument("--ipfile",help="Name of the input file as csv", default="names.csv")
    parser.add_argument("--opfile",help="Name of the output Folder", default="Vcard")
    # subcommand initdb
    subparsers = parser.add_subparsers(dest="op")
    subparsers.add_parser("initdb", help="Initialise the database")
    # import csv
    import_parser = subparsers.add_parser("import", help="Import data from csv file")
    import_parser.add_argument("employees_file", help="List of employees to import")
    # create vcards of each person
    vcard_parser=subparsers.add_parser("vcard",help="Generate vcard of each record")
    vcard_parser.add_argument("--qrcode",help="Generate QRCODE of each record",action='store_true',default=False)
    vcard_parser.add_argument("--addres", help="Change into new address",type=str, default="100 Flat Grape Dr.;Fresno;CA;95555;United States of America")
    # fetch vcard
    query_parser = subparsers.add_parser("query", help="Get information for a single employee")
    query_parser.add_argument("--displayvcard", help="Generate vcard for employee", action="store_true", default=False)
    query_parser.add_argument("id", help="Employee id")
    query_parser.add_argument("-q", "--qrcodee", help="Generate QRCODE of single person",action='store_true',default=False)
    query_parser.add_argument("--opfile",help="Name of the output Folder", default="Vcard")
    # query_parser.add_argument("-d", "--dimension", help="Change dimension of QRCODE",action='store_true', type=int, default=200 )
    # add leaves
    leave_parser = subparsers.add_parser("leave", help="Add leave to database")
    leave_parser.add_argument("date", type=str, help="Date of absence")
    leave_parser.add_argument("employee_id", type=int, help="Employee id of absentee")
    leave_parser.add_argument("reason", type=str, help="Reason of absence")
    #leave summery
    leave_summery=subparsers.add_parser("count",help="find count of leaves")
    leave_summery.add_argument("employee_id", type=int, help="Employee id of absentee")
    # export leave summary
    parser_export = subparsers.add_parser("export", help="Export leave summary")
    parser_export.add_argument("directory", help="Directory to export leave summary")
 
    # parser.add_argument("-i","--input_type",help="Specify the data source",choices=['file','db'],required=True)
    
    parser.add_argument("-v", "--verbose", help="Print detailed logging", action='store_true', default=False)
    # parser.add_argument("--vcard", help="Generate vcard of each record", action='store_true', default=True)
    parser.add_argument("-n", "--number", help="Number of records to generate", action='store', type=int, default=10)
    parser.add_argument("-d", "--dimension", help="Change dimension of QRCODE", default=200 )
    # parser.add_argument("-q", "--qrcodee", help="Generate QRCODE of each record",action='store_true',default=False)
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

def update_config(dbname):
  config = configparser.ConfigParser()
  config.read('config.ini')
  config.set('Database','dbname',dbname)
  with open('config.ini','w') as config_file:
     config.write(config_file)

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

   
def create_qr_code(vcard,args,row):
    print(args)
    url=f"https://chart.googleapis.com/chart?cht=qr&chs={args.dimension}x{args.dimension}&chl={vcard}"
    resp=requests.get(url).content
    qr_path=os.path.join(args.opfile, f"{str(row[1][:1])}{str(row[0])}.qr.png")
    if os.path.exists(qr_path):
        logger.warning(f"File already exists: {qr_path}")
    else:
        with open(qr_path, "wb") as file:
            file.write(resp)
            logger.debug(f"Created QR code: {qr_path}")
    # else:
            # logger.warning(f"No write access to directory: {args.opfile}")
         
def initialize_db(args):
    db_uri = f"postgresql:///{args.dbname}"
    db.create_all(db_uri)
    session =db.get_session(db_uri)
    d1 = db.Designation(title="CEO",max_leaves=20)
    d2 = db.Designation(title="Engineer",max_leaves=20)
    session.add(d1)
    session.add(d2)
    session.commit()
     
def handle_import(args):
    try:
        db_uri = f"postgresql:///{args.dbname}"
        session = db.get_session(db_uri)
        with open(args.employees_file) as f:
            reader=csv.reader(f)
            for lname, fname, title, email, phone in reader:
                psql=sa.select(db.Designation).where(db.Designation.title==title)
                designation = session.execute(psql).scalar_one()
                logging.info("Values inserted ")
    except psycopg2.Error as e:
        logging.info(f"Database error: {e}")
        con.rollback()
        logging.info("Values not inserted ")
    finally:
        con.close() 
def create_vcard_file(row,vcard,args):
    vcard_path=os.path.join(args.opfile,f"{str(row[1][:1])}{str(row[0])}.vcf")
    with open(vcard_path, "w") as file:
        file.write(vcard)
def clear_output_dir(args):
    if os.path.exists(args.opfile):
        shutil.rmtree(os.path.join(args.opfile))
        return "Folder removed"
def generate_multiple_vcards_from_db(emplyee_data,args):
    count=1
    if not os.path.exists(args.opfile):
        os.makedirs(args.opfile)
        if args.qrcode:
            logger.info("QR code generation started,Take few minutes to complete.")
        for row in emplyee_data[:args.number]:
            vcard=create_vcard(row[:5],args.addres)
            create_vcard_file(row[:5],vcard,args)
            if args.qrcode:
                create_qr_code(vcard,args,row[:2])
            if count==args.number:
                break
            count +=1
            logger.debug(f"Created the file of {row[:1]} ")
        logger.info(f"Successfully created the first {count} person files")
    else:
        logger.warning("The output folder already exists,If you want to Delete press (y/n): ")
        warn=input()
        if warn=="y":
            logger.info( clear_output_dir(args))
        else:
            logger.info("Output directory not removed" )
def create_vcard_from_db(args):
    try:
        with psycopg2.connect(dbname=args.dbname) as con:
            with con.cursor() as cur:        
                query=f"select e.fname, e.lname, e.email, e.phone,d.designation_name  from employees e  INNER JOIN designation d ON e.title_id = d.designation_id"
                cur.execute(query)
                data=[list(row) for row in cur.fetchall()]
                generate_multiple_vcards_from_db(data,args)
    except psycopg2.Error as e:
                logging.info(f"Database error: {e}")
def get_single_person_from_db(args):
    try:
        with psycopg2.connect(dbname=args.dbname) as con:
            with con.cursor() as cur:       
                query=f"select e.fname, e.lname, e.email, e.phone,d.designation_name  from employees e  inner JOIN designation d ON e.title_id = d.designation_id where e.employee_id={args.id}"
                cur.execute(query)
                fname, lname, email, phone ,designation= cur.fetchone()
                print (f"""Name        : {fname} {lname}\nDesignation : {designation}\nEmail       : {email}\nPhone       : {phone}""")
                if (args.displayvcard):
                    data=lname, fname, designation, email, phone
                    vcard = create_vcard(data,args.address)
                    print (f"\n{vcard}")
                if args.qrcodee:
                    print(args)
                    desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
                    # Create the full path to the new folder
                    new_folder_path = os.path.join(desktop_path, args.opfile)
                    if not os.path.exists(new_folder_path):
                        os.makedirs(new_folder_path)
                        url=f"https://chart.googleapis.com/chart?cht=qr&chs={args.dimension}x{args.dimension}&chl={vcard}"
                        resp=requests.get(url).content
                        qr_path=os.path.join(new_folder_path, f"{str(data[1][:1])}{str(data[0])}.qr.png")
                        with open(qr_path, "wb") as file:
                            file.write(resp)
                        logger.info("QR code generated in user specified folder in desktop")
                    else:
                        logger.warning("The output folder already exists,If you want to Delete press (y/n): ")
                        warn=input()
                        if warn=="y":
                            shutil.rmtree(os.path.join(new_folder_path))
                            logger.info("Output directory removed from desktop" )
                        else:
                            logger.info("Output directory not removed" )
       
    except psycopg2.Error as e:
                logging.info(f"Database error: {e}")
  

def insert_leaves(args):
    try:
        with psycopg2.connect(dbname=args.dbname) as con:
            with con.cursor() as cur: 
                psql="SELECT id FROM leaves WHERE employee = %s AND date = %s;"
                cur.execute(psql,(args.employee_id,args.date))
                exists=cur.fetchone()
                if exists:
                    logger.warning(f"Employee already taken leave on {args.date}")
                    return
                psql="""   SELECT e.fname,e.lname,d.total_no_of_leaves, COUNT(l.employee) AS count
                FROM employees e
                left JOIN leaves l ON e.employee_id = l.employee
                JOIN designation d ON e.title_id=d.designation_id 
                WHERE l.employee =%s
                GROUP BY e.fname,e.lname,d.total_no_of_leaves;"""
                cur.execute(psql,(args.employee_id,))
                data=cur.fetchall()
                if data==[]:
                    psql="insert into leaves(date,employee,reason) values(%s,%s,%s)"
                    cur.execute(psql,(args.date,args.employee_id,args.reason))
                    con.commit()
                    logger.info("Leave details inserted ")
                else:
                    for fname,lname,total_leave,count in data:
                        if total_leave==count:
                            logger.warning(f"Mr/Mrs.{fname} {lname} You can't able to take no more leave,Your leave is Finished")
                        return
    except psycopg2.Error as e:
        logger.info(f"Database error: {e}")
        con.rollback()
        logger.info("Leave details not inserted ")
    finally:
        cur.close()
        con.close()
def count_of_leaves(args):
    try:
        with psycopg2.connect(dbname=args.dbname) as con:
            with con.cursor() as cur: 
                psql='''SELECT e.fname, e.lname, d.designation_name, d.total_no_of_leaves, COUNT(l.employee) AS count
                    FROM employees e
                    JOIN leaves l ON e.employee_id = l.employee
                    JOIN designation d ON d.designation_id =e.title_id
                    WHERE l.employee =%s
                    GROUP BY e.fname, e.lname, d.designation_name, d.total_no_of_leaves;
                    '''
                cur.execute(psql,(args.employee_id,))
                data=cur.fetchall()
                for fname,lname,desig,total_leave,count in data:
                    remainig=total_leave-count
                    print(f'''Employee name   :{fname}{lname}
                Designation   :{desig}
                Total leaves   :{total_leave}
                Leaves taken  :{count}
                Remaining leave :{remainig}
                ''')
    except psycopg2.Error as e:
         logging.info(f"Database error: {e}")
    finally:
        cur.close()
        con.close()   

def export_leave_summary(args):
    try:
        with psycopg2.connect(dbname=args.dbname) as con:
            with con.cursor() as cur:   
                psql='''SELECT e.fname, e.lname, d.designation_name, d.total_no_of_leaves, COUNT(l.employee) AS leaves_taken
            FROM employees e
            LEFT JOIN leaves l ON e.employee_id = l.employee
            JOIN designation d ON e.title_id = d.designation_id 
            GROUP BY e.fname, e.lname, d.designation_name, d.total_no_of_leaves;
            '''
                cur.execute(psql)
                data=cur.fetchall()
                directory=args.directory
                os.makedirs(directory,exist_ok=True)
                with open(os.path.join(directory,'leave_summary.csv'),'w',newline='') as csvfille:
                    fieldnames=['First Name','Last Name','Designation','Total Leaves','Leaves Taken','Leaves Remaining']
                    writer=csv.DictWriter(csvfille,fieldnames=fieldnames)
                    writer.writeheader()
                    for item in data:
                        fname,lname,designation_name,total_no_of_leaves,leaves_taken =item
                        leaves_remain=total_no_of_leaves-leaves_taken
                        writer.writerow({
                            'First Name':fname,
                            'Last Name':lname,
                            'Designation':designation_name,
                            'Total Leaves':total_no_of_leaves,
                            'Leaves Taken':leaves_taken,
                            'Leaves Remaining':leaves_remain})
                    print(f"Summary exported to folder {os.path.join(directory,'leaves_summary.csv')}")
    except psycopg2.Error as e:
        print(f"Failed to export data:{e}")
    finally:
        cur.close()
        con.close()
            
def main():
    try:
        args = parse_args()
        setup_logging(args.verbose)
        ops = {"initdb" : initialize_db,
                "import" : handle_import,
                "query" : get_single_person_from_db,
                "vcard" : create_vcard_from_db,
                "leave" : insert_leaves, 
                "count": count_of_leaves,
                "export":export_leave_summary
                }
        
        ops[args.op](args)       
    except HRException as e:
        logger.error("Program aborted, %s", e)
        sys.exit(-1)

if __name__=="__main__":
    main()
    



