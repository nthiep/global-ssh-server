#!/usr/bin/env python
#
# Name:     Global SSH Webservice
# Description:  help connect ssh between client via return public ip and ramdom port.
#               use websocket and HTTP server.
# project 2
# Server:   cloud platform heroku
#
# Author:   Nguyen Thanh Hiep - Nguyen Huu Dinh
# Time:     2014/10
# Requirements:  view requirements.txt
#

import sys, time, os, datetime, hashlib, random
from functools import wraps
from flask import Flask, request, Response, json, render_template, session, redirect, url_for, render_template, flash

lib_path = os.path.abspath(os.path.join('..', ''))
sys.path.append(lib_path)
from gshs import Database, Users, Machines, APIusers
app = Flask(__name__)
app.config['SECRET_KEY'] = "global-ssh-6173b812b1d07e2306f37246d49d147ea601305b"
app.config['DEBUG'] = True

try:
    conn = Database()
    database = conn.connect()
    if not database:
        raise Exception("Database Error: not database config")
    datatype = conn.datatype
except Exception, e:
    print e
    raise Exception("Database Error: can connect to database")

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("you must login first.")
            return redirect(url_for('api_login'))
    return decorated
def createtoken():
    """ create random api key token"""
    code = random.getrandbits(128)
    return hashlib.sha1(str(code)).hexdigest()
def register(user, pswd, fullname, email, website):
    users = Users(database, datatype)    
    pswd = hashlib.md5(pswd).hexdigest()
    pswd = hashlib.sha1(pswd).hexdigest()
    apikey = createtoken()
    if users.adduser(user, pswd, fullname, email, website, apikey):
        return True
    return False
    
def login(user, pswd):
    users = Users(database, datatype)
    pswd = hashlib.md5(pswd).hexdigest()
    pswd = hashlib.sha1(pswd).hexdigest()
    if users.checkauth(user, pswd):
        session['logged_in'] = True
        session['username'] = user
        return True
    return False
def user(user):
    users = Users(database, datatype)
    return users.userinfo(user)
def machines(user):
    apiuser = APIusers(database, datatype)
    lsmu = apiuser.listmac(user)
    machine  = Machines(database, datatype)   
    lsmachine   = machine.listmachine(lsmu)
    return lsmachine

def logs(user):
    res = []
    return res

def logout(user):
    for u in lsclient:
        if u.name == user:
            u.connection.close()
            lsclient.remove(u)
            return "you has logout"
    return "you are not login"

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'logged_in' in session:
        return render_template('content.html', data = machines(session['username']), page = "machines")
    return render_template('index.html')
@app.route('/register', methods=['GET', 'POST'])
def api_register():
    if 'logged_in' in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        if not register(request.form['username'], request.form['password'], request.form['fullname'], request.form['email'], request.form['website']):
            return render_template('register.html', error = True)
        else:
            return render_template('login.html', error = False, reg = True)
    return render_template('register.html', error = False)
    
@app.route('/login', methods=['GET', 'POST'])
def api_login():
    if 'logged_in' in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        if not login(request.form['username'], request.form['password']):            
            return render_template('login.html', error = True, reg=False)
        else:
            session['logged_in'] = True
            session['username'] = request.form['username']
            return redirect(url_for('index'))
    return render_template('login.html', error = False, reg=False)

@app.route('/user/<username>', methods=['GET', 'POST'])
@requires_auth
def api_user(username):
    return render_template('user.html', info = user(username), user = username )

@app.route('/machines', methods=['GET', 'POST'])
@requires_auth
def api_machines():
    return render_template('content.html', data = machines(session['username']), page = "machines")
@app.route('/logs', methods=['GET', 'POST'])
@requires_auth
def api_logs():
    return render_template('content.html', data = logs(session['username']), page = "logs")

@app.route('/logout', methods=['GET', 'POST'])
@requires_auth
def api_logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    flash('logged out')
    return redirect(url_for('index'))
@app.route('/about', methods=['GET'])
def api_about():
    return redirect("https://gssh.github.io/about.html", code=302)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run("",5000)