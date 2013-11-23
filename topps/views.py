from topps import app
from flask import Flask, request, session, g, render_template, redirect, url_for
from stmts import stmts as sql
from util import *
import urllib
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

@app.route('/card/<card_id>')
def card(card_id):
        cur = g.db.cursor()
        cur.execute(sql.populate_card(card_id))
        results = cur.fetchall()
	print results
	first_name=results[0]['first_name']
	last_name=results[0]['last_name']
	number=results[0]['number']
	if results[0]['image_url'] is not None:
		image_url=urllib.unquote(results[0]['image_url'])
	else:
		image_url="http://blog.escapecreative.com/wp-content/themes/patus/images/no-image-half-landscape.png"
	position=results[0]['position']
	team_name=results[0]['team_name']	
    	return render_template("cards.html",card_id=card_id, first_name=first_name, last_name=last_name, number=number, image_url=image_url, position=position, team_name=team_name)
