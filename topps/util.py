import MySQLdb as mysql
import MySQLdb.cursors
from topps import app
from flask import g, redirect, url_for, request
from functools import wraps

def connect_db():
    return mysql.connect(host=app.config["HOST"], db=app.config["DATABASE"], user=app.config["USERNAME"], passwd=app.config["PASSWORD"], cursorclass=mysql.cursors.DictCursor)  

def login_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('login', next=request.url))
        return func(*args, **kwargs)
    return decorated_function

def redirect_url(default='index'):
    return request.args.get('next') or \
           request.referrer or \
           url_for(default)