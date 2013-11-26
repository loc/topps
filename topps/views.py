from topps import app
from flask import Flask, request, session, g, render_template, redirect, url_for
from stmts import stmts as sql
from util import *
from MySQLdb import escape_string as escape
import time

@app.before_request
def before_request():
    g.db = connect_db()
    g.user = session['user'] if 'user' in session else None
    if g.user:
        cur = g.db.cursor()
        cur.execute(sql.get_user(g.user))
        user = cur.fetchone()
        if user:
            (user_id, email, full_name, password_md5, last_points_given_at, points) = user
            now = time.time()
            extra_points = extra_points_for_active(now, int(last_points_given_at))
            cur = g.db.cursor()
            cur.execute(sql.after_login(user_id, now, extra_points))

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
       db.close()

@app.route('/secret')
@login_required
def secret():
    return "secret"

@app.route('/')
def index():
    cur = g.db.cursor()
    cur.execute(sql.get_user(g.user))
    user = cur.fetchone()
    
    cur = g.db.cursor()
    cur.execute("SELECT * FROM users")
    rows = cur.fetchall()
    return render_template("example.html", rows=rows, user=user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if g.user is not None:
        return redirect(url_for('index'))
    if request.method == 'POST':
        email = escape(request.form['email'])
        password = escape(request.form['password'])

        cur = g.db.cursor()
        cur.execute(sql.login(email, password))
        results = cur.fetchall()
        print results
        if len(results) == 1:
            session['user'] = str(results[0]["id"])
            # After_login logic
            return redirect(redirect_url())
        # error("couldn't log you in")
    return render_template("login.html")


@app.route('/logout')
def logout():
    if g.user is None:
        return redirect(url_for('login'))
    session.pop("user")
    return redirect(url_for('index'))

@app.route('/cards')
def cards():
    return render_template("cards.html")
