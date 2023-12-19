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

import models
import web

class HRException(Exception):pass

logger=False
todays_date = str(datetime.date.today())

def parse_args():
    parser=argparse.ArgumentParser(prog="gen_vcard.py",description="Employee information manager for a small company.")
    config = configparser.ConfigParser()
    config.read('config.ini')
    parser.add_argument("--dbname", help="Adding database name", action="store", type=str, default=config.get('Database', 'dbname'))
    # parser.add_argument("-b","--dbname",help="Name of the database",default='HRmgt')
    parser.add_argument("--ipfile",help="Name of the input file as csv", default="names.csv")
    parser.add_argument("--opfile",help="Name of the output Folder", default="Vcard")
    # subcommand initdb
    subparsers = parser.add_subparsers(dest="op")
    subparsers.add_parser("initdb", help="Initialise the database")

    web_parser = subparsers.add_parser("web", help="Start web server")
    # import csv
    import_parser = subparsers.add_parser("import", help="Import data from csv file")
    import_parser.add_argument("employees_file", help="List of employees to import")
    # create vcards of each person
    vcard_parser=subparsers.add_parser("vcard",help="Generate vcard of each record")
    vcard_parser.add_argument("--qrcode",help="Generate QRCODE of each record",action='store_true',default=False)
   
    # fetch vcard
    query_parser = subparsers.add_parser("query", help="Get information for a single employee")
    query_parser.add_argument("--displayvcard", help="Generate vcard for employee", action="store_true", default=False)
    query_parser.add_argument("id", help="Employee id")
    query_parser.add_argument("-q", "--qrcodee", help="Generate QRCODE of single person",action='store_true',default=False)
    query_parser.add_argument("--opfile",help="Name of the output Folder", default="Vcard")
    
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
    parser_export.add_argument("-directory", help="Directory to export leave summary")
 
    # parser.add_argument("-i","--input_type",help="Specify the data source",choices=['file','db'],required=True)
    parser.add_argument("-v", "--verbose", help="Print detailed logging", action='store_true', default=False)
    parser.add_argument("-n", "--number", help="Number of records to generate", action='store', type=int, default=10)
    parser.add_argument("-d", "--dimension", help="Change dimension of QRCODE", default=200 )
    # parser.add_argument("-q", "--qrcodee", help="Generate QRCODE of each record",action='store_true',default=False)
    parser.add_argument("-a", "--address", help="Change into new address",type=str,default="100 Flat Grape Dr.;Fresno;CA;95555;United States of America")
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

def create_vcard(fname,lname,title,email,phone,address):
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

   
def create_qr_code(fname,lname,vcard,args):
    url=f"https://chart.googleapis.com/chart?cht=qr&chs={args.dimension}x{args.dimension}&chl={vcard}"
    resp=requests.get(url).content
    qr_path=os.path.join(args.opfile, f"{str(fname[:1])}{str(lname)}.qr.png")
    if os.path.exists(qr_path):
        logger.warning(f"File already exists: {qr_path}")
    else:
        with open(qr_path, "wb") as file:
            file.write(resp)
            logger.debug(f"Created QR code: {qr_path}")     

def initialize_db(args):
    db_uri = f"postgresql:///{args.dbname}"
    models.create_all(db_uri)
    session = models.get_session(db_uri)
    exist_designation=session.query(models.Designation).first()
    if not exist_designation:
        d1 = models.Designation(title = "Staff Engineer", max_leaves = 10)
        d2 = models.Designation(title = "Tech Lead", max_leaves = 20)
        d3 = models.Designation(title = "Project Manager", max_leaves = 40)
        d4 = models.Designation(title = "Senior Engineer", max_leaves = 15)
        d5 = models.Designation(title = "Junior Engineer", max_leaves = 15)
        session.add(d1)
        session.add(d2)
        session.add(d3)
        session.add(d4)
        session.add(d5)
        session.commit()
def handle_import(args):
    db_uri = f"postgresql:///{args.dbname}"
    session = models.get_session(db_uri)
    exist_employee=session.query(models.Employee).first()
    if not exist_employee:
        with open(args.employees_file) as f:
            reader = csv.reader(f)  
            for lname, fname, title, email, phone in reader:
                designation = session.query(models.Designation).filter(models.Designation.title == title).first()
                try:
                    if designation:
                        logger.info("Inserting %s", email)
                        employee = models.Employee(
                            lname=lname,
                            fname=fname,
                            title=designation,
                            email=email,
                            phone=phone
                        )
                        session.add(employee)
                    else:
                        logger.warning(f"Value is not inserted: {email}")
                except Exception as e:
                    logger.error("Already exits this email" )
            session.commit()
    
def insert_leaves(args):
    db_uri = f"postgresql:///{args.dbname}"
    session = models.get_session(db_uri)
    date=args.date
    employee_id=args.employee_id
    reason=args.reason
    leave=models.Leave(date=date,employee_id=employee_id,reason=reason)
    session.add(leave)
    session.commit()
    logger.info("Leave added for Employee Id %s on %s with reason:%s",employee_id,date,reason)

def get_single_vcard(args):
    db_uri = f"postgresql:///{args.dbname}"
    session = models.get_session(db_uri)
    employee_id = int(args.id)  # Convert the ID to an integer
    employee=session.query(models.Employee).filter(models.Employee.id==args.id).first()
    if employee:
        vcard = create_vcard(employee.fname,employee.lname,employee.title.title,employee.email,employee.phone, args.address)
        if vcard:
            print (f"\n{vcard}")
            if args.qrcodee:
                    desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
                    # Create the full path to the new folder
                    new_folder_path = os.path.join(desktop_path, args.opfile)
                    if not os.path.exists(new_folder_path):
                        os.makedirs(new_folder_path)
                        url=f"https://chart.googleapis.com/chart?cht=qr&chs={args.dimension}x{args.dimension}&chl={vcard}"
                        resp=requests.get(url).content
                        qr_path=os.path.join(new_folder_path, f"{str(employee.fname[:1])}{str(employee.lname)}.qr.png")
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
       
        else:
            logger.error("Failed to generate vCard.")
    else:
        logger.error("Employee with ID %s not found", employee_id) 
def count_of_leaves(args):
    db_uri = f"postgresql:///{args.dbname}"
    session = models.get_session(db_uri)
    employee_id = int(args.employee_id)  # Convert the ID to an integer
    employee=session.query(models.Employee).filter(models.Employee.id==employee_id).first()
    if employee:
        total_leaves=employee.title.max_leaves
        leaves_taken=session.query(models.Leave).filter(models.Leave.employee_id==employee_id).count()
        leaves_remaining = total_leaves - leaves_taken
        print(f'''Employee name     :{employee.fname} {employee.lname}
Designation       :{employee.title.title}
Total leaves      :{total_leaves}
Leaves taken      :{leaves_taken}
Remaining leave   :{leaves_remaining}
                ''')
    else:
        logger.error("Employee with ID %s not found", employee_id)
def export_leave_summary(args):
    db_uri = f"postgresql:///{args.dbname}"
    session = models.get_session(db_uri)
    employees=session.query(models.Employee).all()
    directory=args.directory
    os.makedirs(directory,exist_ok=True)
    with open(os.path.join(directory,'leave_summary.csv'),'w',newline='') as csvfille:
        fieldnames=['First Name','Last Name','Designation','Total Leaves','Leaves Taken','Leaves Remaining']
        writer=csv.DictWriter(csvfille,fieldnames=fieldnames)
        writer.writeheader()
        for employee in employees:
            total_leaves=employee.title.max_leaves
            leaves_taken=session.query(models.Leave).filter(models.Leave.employee_id==employee.id).count()
            leaves_remain = total_leaves - leaves_taken
            writer.writerow({
                            'First Name':employee.fname,
                            'Last Name':employee.lname,
                            'Designation':employee.title,
                            'Total Leaves':total_leaves,
                            'Leaves Taken':leaves_taken,
                            'Leaves Remaining':leaves_remain})
        print(f"Summary exported to folder {os.path.join(directory,'leaves_summary.csv')}")
    
def create_vcard_file(fname,lname,vcard,args):
    vcard_path=os.path.join(args.opfile,f"{str(fname[:1])}{str(lname)}.vcf")
    with open(vcard_path, "w") as file:
        file.write(vcard)
def clear_output_dir(args):
    if os.path.exists(args.opfile):
        shutil.rmtree(os.path.join(args.opfile))
        return "Folder removed"

def create_vcard_from_db(args):
    db_uri = f"postgresql:///{args.dbname}"
    session = models.get_session(db_uri)
    employees=session.query(models.Employee).all()
    if employees:
        count=1
        if not os.path.exists(args.opfile):
            os.makedirs(args.opfile)
            if args.qrcode:
                logger.info("QR code generation started,Take few minutes to complete.")
            for employee in employees:
                vcard=create_vcard(employee.lname,employee.fname,employee.title.title,employee.email,employee.phone,args.address)
                create_vcard_file(employee.fname,employee.lname,vcard,args)
                if args.qrcode:
                    create_qr_code(employee.fname,employee.lname,vcard,args)
                if count==args.number:
                    break
                count +=1
                logger.debug(f"Created the file of {employee.fname} ")
            logger.info(f"Successfully created the first {count} person files")
        else:
            logger.warning("The output folder already exists,If you want to Delete press (y/n): ")
            warn=input()
            if warn=="y":
                logger.info( clear_output_dir(args))
            else:
                logger.info("Output directory not removed" )
def handle_web(args):
    web.app.config["SQLALCHEMY_DATABASE_URI"]=f"postgresql:///{args.dbname}"
    web.db.init_app(web.app)
    web.app.run()

def main():
    try:
        args = parse_args()
        setup_logging(args.verbose)
        ops = {"initdb" : initialize_db,
                "import" : handle_import,
                "query" : get_single_vcard,
                "vcard" : create_vcard_from_db,
                "leave" : insert_leaves, 
                "count": count_of_leaves,
                "export":export_leave_summary,
                "web"    : handle_web,
            }
        
        ops[args.op](args)       
    except HRException as e:
        logger.error("Program aborted, %s", e)
        sys.exit(-1)

if __name__=="__main__":
    main()
    



