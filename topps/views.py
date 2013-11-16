from topps import app
from flask import Flask, request, session, g, render_template, redirect, url_for
from stmts import stmts as sql
from util import *
from MySQLdb import escape_string as escape

@app.before_request
def before_request():
    g.db = connect_db()
    g.user = session['username'] if 'username' in session else None

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
    cur.execute("SELECT * FROM users")
    rows = cur.fetchall()
    return render_template("example.html", rows=rows, user=g.user)


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
            session['username'] = str(results[0]["id"])
            return redirect(redirect_url())
        # error("couldn't log you in")
    return render_template("login.html")
