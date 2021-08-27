import re
from app import app
from flask import render_template,redirect,request,flash, make_response
from app.models.user import User
import os
from functools import wraps

users =  [name[:-5] for name in os.listdir(app.config['DB_DIR'])]

def login (func):
    @wraps(func)
    def loginFunc(*arg, **kwargs):
        try:
            account = User.read_data(request.cookies.get('user'))
            if account.check_session(request.cookies.get('token')):
                return func(*arg, **kwargs)
        except:
            pass
        flash('login required!')
        return redirect('/signIn')
    return loginFunc

def no_login (func):
    @wraps(func)
    def loginFunc(*arg, **kwargs):
        try:
            account = User.read_data(request.cookies.get('user'))
            if account.check_session(request.cookies.get('token')):
                return redirect('/index')
        except:
            pass
        return  func(*arg, **kwargs)
    return loginFunc

@app.route('/')
def main():
   return redirect('/signIn')

@app.route("/index")
@login
def index():
    return render_template("index.html")

@app.route("/signIn", methods=['POST','GET'])
@no_login
def signIn():
    if request.method == 'GET':
        return render_template('signIn.html')
    elif request.method == 'POST':
        user, password = request.form.get('user'), request.form.get('password')
        if user in users:
            account = User.read_data(user)
            if account.check_password(password):
                token= account.generate_session()
                res = make_response(redirect('/index'))
                res.set_cookie('user', account.user)
                res.set_cookie('token', token)
                return res
            else:
                flash('Invalid user or password!!!')
                return redirect('/signIn')
        else:
            flash('Invalid user or password!!!')
            return redirect('/signIn')

        
@app.route('/signUp', methods=['GET', 'POST'])
def signUp():
    if request.method == 'GET':
        return render_template("signUp.html")
    elif request.method == 'POST':
        user, password, confirmPass = request.form.get('user'), request.form.get('password'), request.form.get('confirmPass')
        global users
        if user in users:
            flash('User already exists!!!')
            return redirect('/signUp')
        elif password == confirmPass:
            account = User(user,password)
            account.hash_password(password)
            users =  [name[:-5] for name in os.listdir(app.config['DB_DIR'])]
            flash("User created successfully!")
            return redirect('/signIn')
        else:
            flash('password dont match!!' )
            return redirect('/signUp') 

@app.route("/logOut")
@login
def logOut():
    account = User.read_data(request.cookies.get('user'))
    account.delete_session()
    res = make_response(redirect('/signIn'))
    res.delete_cookie('user')
    res.delete_cookie('token')
    return res



@app.route("/changePass", methods=['GET','POST'])
@login
def changePass():
    if request.method == 'GET':
        return render_template("changePass.html")
    
    elif request.method == 'POST':
        account = User.read_data(request.cookies.get('user'))
        currentPassword, newPassword, confirmPassword = request.form.get('currentPass'), request.form.get('newPass'), request.form.get('confirmPass')
        if account.check_password(currentPassword):
            if newPassword == confirmPassword:
                account.hash_password(newPassword)
                account.delete_session()
                flash('Successful Change!!!')
                res = make_response(redirect('/signIn'))
                res.delete_cookie('user')
                res.delete_cookie('token')
                return res   
            else:
                flash('Password do not match !!')
                return redirect('/changePass')
        else:
            flash('Invalid password!!!')
            return redirect('/changePass')
