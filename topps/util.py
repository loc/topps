import MySQLdb as mysql
import MySQLdb.cursors
from topps import app
from flask import g, redirect, url_for, request
from functools import wraps
from datetime import timedelta
from collections import defaultdict

def connect_db():
    return mysql.connect(host=app.config["HOST"], db=app.config["DATABASE"], user=app.config["USERNAME"], passwd=app.config["PASSWORD"], cursorclass=mysql.cursors.DictCursor)

def login_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('login', next=request.url))
        return func(*args, **kwargs)
    return decorated_function

def admin_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if g.user is None or g.user_record is None:
            return redirect(url_for('login', next=request.url))
        elif not g.user_record["is_admin"]:
            return redirect(url_for('cards'))
        else:
            return func(*args, **kwargs)
    return decorated_function

def redirect_url(default='index'):
    return request.args.get('next') or \
           request.referrer or \
           url_for(default)

def extra_points_for_active(current_datetime, last_points_given):
    diff_time = current_datetime - last_points_given
    one_day = timedelta(days=1)

    if diff_time >= one_day:
        return 5 # If they haven't got points in the last 24 hours, give them 5 more points
    else:
        return 0

sort_types = {
    "team": "team_name",
    "position": "position",
    "conference": "conference_name",
    "division": "division"
}

def card_sort(cards, sort):
    key = sort_types[sort]
    obj = defaultdict(list)
    for card in cards:
        #print card[key]
        obj[card[key]].append(card)
    return obj