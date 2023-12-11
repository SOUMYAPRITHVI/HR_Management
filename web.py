import flask

import models
from flask import Flask, request, flash, url_for, redirect, render_template
from sqlalchemy.sql import func
app =flask.Flask("hrms")
app.secret_key="abc"
db=models.SQLAlchemy(model_class=models.HRDBBase)

# @app.route("/", methods=["GET", "POST"])
# def index():
#     if flask.request.method == "GET":
#         return flask.render_template("index.html")
#     elif flask.request.method == "POST":
#         return "Posted!"

@app.route("/", methods=["GET"])
def index():
    if request.method == "GET":
        return render_template("index.html")


@app.route("/employees")
def employees():
    query = db.select(models.Employee).order_by(models.Employee.fname)
    users = db.session.execute(query).scalars()
    return render_template("userlist.html", users = users)

# @app.route("/employees/<int:empid>")
# def employee_details(empid):
#     qs = db.select(models.Employee).order_by(models.Employee.fname)
#     users= db.session.execute(qs).scalars()
#     query = db.select(models.Employee).where(models.Employee.id == empid)
#     user = db.session.execute(query).scalar()
#     query_for_leaves = db.select(func.count(models.Employee.id)).join(models.Leave, models.Employee.id == models.Leave.employee_id).filter(models.Employee.id == empid)
#     leave = db.session.execute(query_for_leaves).scalar()
#     return render_template("userdetails.html", user = user,leave=leave,users=users)

@app.route("/employees/<int:empid>",methods=(["GET","POST"]))
def employee_details(empid):
    query = db.select(models.Employee).where(models.Employee.id == empid)
    user = db.session.execute(query).scalar()
    query_for_leaves = db.select(func.count(models.Employee.id)).join(models.Leave, models.Employee.id == models.Leave.employee_id).filter(models.Employee.id == empid)
    leave = db.session.execute(query_for_leaves).scalar()
    query2 = db.select(models.Designation.max_leaves).where(models.Designation.id == models.Employee.title_id)
    max_leaves = db.session.execute(query2).scalar()
    if request.method == 'POST':
         date=request.form['leavedate']
         reason=request.form['leavereason']
         newleave = models.Leave(date=date,employee_id=empid,reason=reason)
         db.session.add(newleave)
         db.session.commit()
        #  flash("Leave added")
         return redirect(url_for("employees"))
    ret = { "id"   :user.id,
            "fname" : user.fname,
           "lname" : user.lname,
           "title" : user.title.title,
           "email" : user.email,
           "phone" : user.phone,
           "leave" : leave,
           "max_leaves":max_leaves,
           "leave_remain":max_leaves-leave}
    return flask.jsonify(ret)

# @app.route("/leaves/<int:empid>", methods=["GET","POST"])
# def add_leaves(empid):
#     if request.method == 'POST':
#          date=request.form['leavedate']
#          reason=request.form['leavereason']
#          newleave = models.Leave(date=date,employee_id=empid,reason=reason)
#          db.session.add(newleave)
#          db.session.commit()
#         #  flash("Leave added")
#          return redirect(url_for("employees"))
#     return render_template("add_leave.html",empid=empid)

@app.route("/about")
def about():
    return render_template("about.html")
   