import flask
from flask_cors import CORS
import models
from flask import request,render_template
from sqlalchemy.sql import func

app =flask.Flask("hrms")
CORS(app)
db=models.SQLAlchemy(model_class=models.HRDBBase)

@app.route("/", methods=["GET"])
def index():
    if request.method == "GET":
        return render_template("index.html")


@app.route("/employees")
def employees():
    query = db.select(models.Employee).order_by(models.Employee.fname)
    users = db.session.execute(query).scalars()
    emps=[]
    for u in users:
        ret = { "id"   :u.id,
                "fname" : u.fname,
            "lname" : u.lname,
            "title" : u.title.title,    
            "email" : u.email,
            "phone" : u.phone,
        }
        emps.append(ret)
    return flask.jsonify(emps)
  

@app.route("/employees/<int:empid>")
def employee_details(empid):
    query = db.select(models.Employee).where(models.Employee.id == empid)
    user = db.session.execute(query).scalar()
    query_for_leaves = db.select(func.count(models.Employee.id)).join(models.Leave, models.Employee.id == models.Leave.employee_id).filter(models.Employee.id == empid)
    leave = db.session.execute(query_for_leaves).scalar()
    query2 = db.select(models.Designation.max_leaves).where(models.Designation.id == models.Employee.title_id)
    max_leaves = db.session.execute(query2).scalar()
    emps = []
    ret = { "id"   :user.id,
        "fname" : user.fname,
        "lname" : user.lname,
        "title" : user.title.title,
        "email" : user.email,
        "phone" : user.phone,
        "leave" : leave,
        "max_leaves":max_leaves,
        "leave_remain":max_leaves-leave}
    emps.append(ret)
    return flask.jsonify(emps)


@app.route("/leave/<int:empid>", methods=["GET", "POST"])
def addleave(empid):
    query_for_leaves = db.select(func.count(models.Employee.id)).join(models.Leave, models.Employee.id == models.Leave.employee_id).filter(models.Employee.id == empid)
    leave = db.session.execute(query_for_leaves).scalar()
    query2 = db.select(models.Designation.max_leaves).where(models.Designation.id == models.Employee.title_id)
    max_leaves = db.session.execute(query2).scalar()
    if int(leave) <= int(max_leaves) -1 :
        try:
            if request.method == "POST":
                data = request.get_json()
                date = data.get('date')
                reason = data.get('reason')
                insert_data = models.Leave(employee_id=empid ,date=date, reason=reason)
                db.session.add(insert_data)
                db.session.commit()
                return flask.jsonify({'message': 'Leave added successfully'})
        except:
            db.session.rollback()
            return flask.jsonify({'message': 'Leave already taken in this date'}),403
    else :
        return flask.jsonify({'error': 'maximum number of leaves exceeds '}), 405
  


@app.errorhandler(404)
def not_found_error(error):
    return flask.jsonify({'error': 'Page not found'}), 404

@app.errorhandler(500)
def internal_server_error(error):
    return flask.jsonify({'error': 'page'}), 200


@app.route("/about")
def about():
    return render_template("about.html")
