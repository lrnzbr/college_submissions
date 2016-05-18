from flask import Flask, render_template, jsonify, request, url_for, abort, g, flash, redirect
from model import *
from flask.ext.httpauth import HTTPBasicAuth
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from passlib.apps import custom_app_context as pwd_context
from flask import session as login_session

app = Flask(__name__)
app.secret_key = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))

# Connect to Database and create database session
engine = create_engine('sqlite:///SixUp.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine, autoflush=False)
session = DBSession()
auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(email, password):
    student = session.query(Student).filter_by(email = email).first()
    if not student or not student.verify_password(password):
        return False
    g.student = student
    return True


@app.route("/")
def main():
    return render_template("main.html")

@app.route("/login", methods = ['GET', 'POST'])
def showLogin():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if email is None or password is None:
            print "Missing Arguments"
            abort(400)
        if verify_password(email, password):
            student = session.query(Student).filter_by(email=email).one()
            flash("Login Successful, welcome, %s" % g.student.name)
            login_session['name'] = student.name
            login_session['email'] = email
            login_session['id'] = student.id
            return redirect(url_for('main'))
        else:
            #Incorrect username/password
            flash("Incorrect username/password combination")
            return redirect(url_for('showLogin'))

@app.route('/register', methods = ['GET','POST'])
def new_student():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        address = request.form['address']
        if name is None or email is None or password is None:
            flash("missing arguments")
            return redirect(url_for('new_student'))
        if session.query(Student).filter_by(email = email).first() is not None:
            return jsonify({'message':'user already exists'}), 200#, {'Location': url_for('get_user', id = user.id, _external = True)}
        student = Student(name = name, email=email, address = address)
        student.hash_password(password)
        session.add(student)
        session.commit()
        flash("User Created Successfully!")
        return redirect(url_for('main'))
    else:
        return render_template('newStudent.html')
@app.route('/studentProfile/<int:student_id>')
def update_student(student_id):
    student = session.query(Student).filter_by(id = student_id).one()
    if method.request == 'GET':
        return render_template('updateApplication.html')
    elif method.request == 'POST':
        student.name = request.form['name']
        student.email = request.form['email']
        student.address = request.form['address']
        session.add(student)
        session.commit()
        flash("Student Profile Updated Successfully")
        return redirect(url_for('main'))

@app.route('/logout')
def logout():
    if 'name' not in login_session:
        flash("You must be logged in in order to log out")
        return redirect(url_for('main'))
    del login_session['name']
    del login_session['email']
    del login_session['id']
    flash ("Logged Out Successfully")
    return redirect(url_for('main'))

@app.route("/user")
def view_profile():
    if 'name' not in login_session:
        flash("You must be logged in in order to view your profile")
        return redirect(url_for('main'))
    profile = session.query(User).filter_by(id = login_session['id']).one()
    return render_template('student.html', profile=profile)

@app.route("/updateApplication/<int:app_id>", methods = ['GET', 'POST'])
def update_app(app_id):
    app = session.query(Application).filter_by(id=app_id).one()
    if request.method == 'GET':
        return render_template('updateApplication.html', app = app)
    elif request.method == 'POST':
        app.school = request.form['school']
        app.essay = request.form['essay']
        session.add(app)
        session.commit()
        flash("Application Updated Successfully")
        return redirect(url_for('view_applications'))

@app.route("/deleteApplication/<int:app_id>", methods = ['GET', 'POST'])
def remove_app(app_id):
    app = session.query(Application).filter_by(id=app_id).one()
    session.delete(app)
    session.commit()
    flash("Successfully Deleted Application")
    return redirect(url_for('view_applications'))

@app.route("/colleges")
def view_applications():
    if 'name' not in login_session:
        flash("You must be logged in in order to view your profile")
        return redirect(url_for('main'))
    applications = session.query(Application).filter_by(student_id = login_session['id']).all()
    return render_template('colleges.html', applications = applications)

@app.route("/application", methods = ['GET', 'POST'])
def new_application():
    if request.method == 'GET':
        return render_template('newApplication.html')
    elif request.method == 'POST':
        app = Application(school=request.form['school'], essay = request.form['essay'], student_id = login_session['id'])
        session.add(app)
        session.commit()
        flash("Application Created Successfully.")
        return redirect(url_for('view_applications'))

if __name__ == "__main__":
    app.debug = True
    app.run()
