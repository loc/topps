from topps import app
from flask import Flask, request, session, g, render_template, redirect, url_for
from stmts import stmts as sql
from util import *
import urllib
from MySQLdb import escape_string as escape
from datetime import datetime

@app.before_request
def before_request():
    g.db = connect_db()
    g.user = session['user'] if 'user' in session else None
    if g.user:
        cur = g.db.cursor()
        cur.execute(sql.get_user(), (int(g.user),))
        user = cur.fetchone()
        if user:
            last_points_given_at = user["last_points_given_at"] or datetime.now()
            now = datetime.now()
            extra_points = extra_points_for_active(now, last_points_given_at)
            if extra_points > 0:
                cur = g.db.cursor()
                cur.execute(sql.after_login(), (extra_points, int(g.user)))

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
    cur.execute(sql.get_user(), (g.user))
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

@app.route('/card/<card_id>')
def card(card_id):
        cur = g.db.cursor()
        cur.execute(sql.populate_card(card_id))
        results = cur.fetchone()
	first_name=results['first_name']
	last_name=results['last_name']
	number=results['number']
	position=results['position']
	team_name=results['team_name']

	if results['image_url'] is not None:
		image_url=urllib.unquote(results['image_url'])
	else:
		image_url="http://blog.escapecreative.com/wp-content/themes/patus/images/no-image-half-landscape.png"	

    	return render_template("cards.html",card_id=card_id, first_name=first_name, last_name=last_name, number=number, image_url=image_url, position=position, team_name=team_name)

@app.route('/trade/<user_id_1>/<user_id_2>/initiate', methods=['GET', 'POST'])
def initiate_trade(user_id_1, user_id_2):
	cur = g.db.cursor()
	cur.execute(sql.check_trades(user_id_1, user_id_2)) #if trade between user1 and user2 exists, return it
	results = cur.fetchone()

	#update trade cards table based on post (user1's desired cards and cards willing to trade)
	if request.method == 'POST': 
        	user1_cards = escape(request.form['user1_cards'])
        	user1_cards = user1_cards.split()
		user1_desired = escape(request.form['user1_desired'])
		user1_desired = user1_desired.split()

		for id in user1_cards:
			cur.execute(sql.insert_trade_cards(results['trade_id'], id, user_id_1, False))
			g.db.commit()

		for id in user1_desired:
			cur.execute(sql.insert_trade_cards(results['trade_id'], id, user_id_1, True))	
			g.db.commit()

		return redirect(url_for('accept_trade', user_id_1=user_id_1, user_id_2=user_id_2)) #after post, redirect to accept stage

	#check and make sure there are no previously unresolved trades between the two parties
	if results is not None:
		return render_template("status.html", status_text="trade has already been initiated")

	#initiate a trade in the trade table
	cur.execute(sql.initiate_trade(user_id_1,user_id_2))
	g.db.commit()
    	return render_template("status.html", status_text="trade initiated")


@app.route('/trade/<user_id_1>/<user_id_2>/accept', methods=['GET', 'POST'])
def accept_trade(user_id_1, user_id_2):
	status_text = None;
	cur = g.db.cursor()
	cur.execute(sql.check_trades(user_id_1, user_id_2)) #if a trade between user1 and user2 exists, return it
	results = cur.fetchone()

	#update trade cards on a post (user2's cards willing to trade)
	if request.method == 'POST':
        	user2_cards = escape(request.form['user2_cards'])
        	user2_cards = user2_cards.split()

		for id in user2_cards:
			cur.execute(sql.insert_trade_cards(results['trade_id'], id, user_id_2, False))
			g.db.commit()

		return redirect(url_for('confirm_trade', user_id_1=user_id_1, user_id_2=user_id_2)) #after post, redirect to confirm stage

	#check and make sure a trade has previously been initiated between the two parties
	if results is None:
		return render_template("status.html", status_text="trade has not been initiated")

	#check and make sure that the initiated trade has not been accepted or confirmed yet

	if results['accepted_at'] is not None:
		status_text="trade has already been accepted"

	if results['confirmed_at'] is not None:
		status_text="trade has already been confirmed"

	if status_text is not None:
		return render_template("status.html", status_text=status_text)

	#update trade table to include accept timestamp
	cur.execute(sql.accept_trade(user_id_1,user_id_2))
	g.db.commit()
    	return render_template("status.html", status_text="trade accepted")

@app.route('/trade/<user_id_1>/<user_id_2>/confirm', methods=['GET', 'POST'])
def confirm_trade(user_id_1, user_id_2):
	status_text = None
	cur = g.db.cursor()
	cur.execute(sql.check_trades(user_id_1, user_id_2))
	results = cur.fetchone()

	#check and make sure a trade has both been initiated and accepted between the two parties
	if results is None:
		return render_template("status.html", status_text="trade has not been initiated")
	
	#check and make sure that the initiated trade has been accepted but not confirmed yet
	if results['accepted_at'] is None:
		status_text="trade has not been accepted"

	if results['confirmed_at'] is not None:
		status_text="trade has already been confirmed"

	if status_text is not None:		
		return render_template("status.html", status_text=status_text)		

	#update trade table to include confirm timestamp
	cur.execute(sql.confirm_trade(user_id_1,user_id_2))
	g.db.commit()
    	return render_template("status.html", status_text="trade confirmed")

@app.route('/trade/<user_id_1>/<user_id_2>/perform', methods=['GET', 'POST'])
def perform_trade(user_id_1, user_id_2):
	status_text = None;	
	cur = g.db.cursor()
	cur.execute(sql.check_trades(user_id_1, user_id_2))
	results = cur.fetchone()

	#check and make sure trade has been initiated, accepted, and confirmed
	if results is None:
		return render_template("status.html", status_text="trade has not been initiated")

	if results['confirmed_at'] is None:
		status_text="trade has not been confirmed"

	if results['accepted_at'] is None:
		status_text="trade has not been accepted"
	
	if status_text is not None:
		return render_template("status.html", status_text=status_text)

	#perform trade, change owner id's in card table
	cur.execute(sql.select_trade_cards(results['trade_id']))
	trade_results = cur.fetchall()
	for trade in trade_results:

		if trade['from_id'] == int(user_id_1) and trade['desired'] == False :
			cur.execute(sql.trade_card(trade['card_id'], user_id_2))
			g.db.commit()

		elif trade['from_id'] == int(user_id_2) and trade['desired'] == False :
			cur.execute(sql.trade_card(trade['card_id'], user_id_1))
			g.db.commit()			

    	return render_template("status.html", status_text="trade performed")

@app.route('/trade/<user_id_1>/<user_id_2>/cancel', methods=['GET', 'POST'])
def cancel_trade(user_id_1, user_id_2):
	cur = g.db.cursor()
	cur.execute(sql.cancel_trade(user_id_1,user_id_2))
	g.db.commit()
    	return render_template("status.html", status_text="trade canceled")



