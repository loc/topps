import MySQLdb as mysql
import MySQLdb.cursors
from topps import app
from flask import g, redirect, url_for, request
from functools import wraps
import time

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

def extra_points_for_active(current_ts, last_points_given):
    diff_points = current_ts - last_points_given
    one_day = (24 * 3600)

    if diff_points >= one_day:
        return 5 # If they haven't got points in the last 24 hours, give them 5 more points
    else:
        return 0