import MySQLdb as mysql
import MySQLdb.cursors
from topps import app
from flask import g, redirect, url_for, request
from functools import wraps
from datetime import timedelta
from collections import defaultdict

def connect_db(app):
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
        if g.is_admin:
            return func(*args, **kwargs)
        elif g.user:
            return redirect(url_for('cards', next=request.url))
        else:
            return redirect(url_for('login', next=request.url))
        return func(*args, **kwargs)
    return decorated_function

def redirect_url(default='index'):
    return request.args.get('next') or \
           request.referrer or \
           url_for(default)

def extra_points_for_active(current_datetime, last_points_given):
    if last_points_given is None:
            return 5

    diff_time = current_datetime - last_points_given
    one_day = timedelta(days=1)

    if diff_time >= one_day:
        return 5 # If they haven't got points in the last 24 hours, give them 5 more points
    else:
        return 0

def pretty_date(time=False):
    """
    Get a datetime object or a int() Epoch timestamp and return a
    pretty string like 'an hour ago', 'Yesterday', '3 months ago',
    'just now', etc
    """
    from datetime import datetime
    now = datetime.now()
    if type(time) is int:
        diff = now - datetime.fromtimestamp(time)
    elif isinstance(time,datetime):
        diff = now - time 
    elif not time:
        diff = now - now
    second_diff = diff.seconds
    day_diff = diff.days

    if day_diff < 0:
        return ''

    if day_diff == 0:
        if second_diff < 10:
            return "just now"
        if second_diff < 60:
            return str(second_diff) + " seconds ago"
        if second_diff < 120:
            return  "a minute ago"
        if second_diff < 3600:
            return str( second_diff / 60 ) + " minutes ago"
        if second_diff < 7200:
            return "an hour ago"
        if second_diff < 86400:
            return str( second_diff / 3600 ) + " hours ago"
    if day_diff == 1:
        return "Yesterday"
    if day_diff < 7:
        return str(day_diff) + " days ago"
    if day_diff < 31:
        return str(day_diff/7) + " weeks ago"
    if day_diff < 365:
        return str(day_diff/30) + " months ago"
    return str(day_diff/365) + " years ago"

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