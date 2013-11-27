from topps import app
from flask import Flask, request, session, g, render_template, redirect, url_for
from stmts import stmts as sql
from util import *
from MySQLdb import escape_string as escape

@app.before_request
def before_request():
    g.db = connect_db()
    g.user = session['user'] if 'user' in session else None

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
            session['user'] = str(results[0]["id"])
            return redirect(redirect_url())
        # error("couldn't log you in")
    return render_template("login.html")


@app.route('/logout')
def logout():
    if g.user is None:
        return redirect(url_for('login'))
    session.pop("user")
    return redirect(url_for('index'))

@app.route('/purchase/<pack_id>', methods=['GET', 'POST'])
def purchase(pack_id):
	cur = g.db.cursor()
	if request.method == 'POST':
		print session['user']
		print pack_id
		cur.execute(sql.purchase_pack, {"user_id": session['user'], "pack_id": pack_id})
		cur.execute(sql.get_user_points, {"user_id": session['user']})
		user_points = cur.fetchone()
		cur.execute(sql.get_pack_points, {"pack_id": pack_id})
		pack_points = cur.fetchone()
		if user_points >= pack_points:
			cur.execute(sql.deduct_points, {"user_id": session['user'], "pack_id": pack_id})
			g.db.commit()
		else:
			return render_template("status.html", status_text="you dont have enough pts")		
		return render_template("status.html", status_text="trade complete")		
	cur.execute(sql.get_pack, (pack_id,))
	results = cur.fetchall()
	#print results
	return render_template("purchase_pack.html", results=results)
