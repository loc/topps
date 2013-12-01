from topps import app
from flask import Flask, request, session, g, render_template, redirect, url_for, jsonify, json, make_response
# stmts does escaping internally
from stmts import stmts as sql
from util import *
import urllib
from datetime import datetime
from pprint import pprint

@app.before_request
def before_request():
    if '/static/' in request.path:
        return
    g.db = connect_db()
    g.user = session['user'] if 'user' in session else None
    if g.user:
        cur = g.db.cursor()
        cur.execute(sql.get_user(g.user))
        user = cur.fetchone()
        if user:
            g.user_record = user
            last_points_given_at = user["last_points_given_at"] or datetime.now()
            now = datetime.now()
            extra_points = extra_points_for_active(now, last_points_given_at)
            if extra_points > 0:
                cur = g.db.cursor()
                cur.execute(sql.after_login(g.user, extra_points))

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
        cur = g.db.cursor()
        cur.execute(sql.login(request.form['email'], request.form['password']))
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


@app.route('/cards/')
@app.route('/cards/<int:id>')
@app.route('/cards/<int:id>/sort/<string:sort>')
@app.route('/cards/sort/<string:sort>')
@login_required
def cards(id=None, sort="team"):
    if not id:
        id=g.user
    cur = g.db.cursor()
    cur.execute(sql.get_user_cards(id))
    cards = cur.fetchall()

    cur.execute(sql.get_user(id))
    user = cur.fetchone()

    print user

    is_my_own = False
    if int(g.user) == int(user['id']):
        is_my_own = True


    for i, card in enumerate(cards):
        cards[i]["image_url"] = urllib.unquote(card['image_url'])

    cards_sorted = {'type': sort, 'cards': card_sort(cards, sort)}

    return render_template("cards.html", sorted=cards_sorted, user=user, is_my_own=is_my_own, sort=sort)

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

    return render_template("card.html",card_id=card_id, first_name=first_name, last_name=last_name, number=number, image_url=image_url, position=position, team_name=team_name)

@app.route('/trade/<other_user_id>/initiate', methods=['GET', 'POST'])
def initiate_trade(other_user_id):
    cur = g.db.cursor()
    cur.execute(sql.check_trades(g.user, other_user_id)) #if trade between user1 and user2 exists, return it
    results = cur.fetchone()

    #update trade cards table based on post (user1's desired cards and cards willing to trade)
    if request.method == 'POST': 
        user1_cards = request.form['user1_cards'].split()
        user1_desired = request.form['user1_desired'].split()

        for id in user1_cards:
            cur.execute(sql.insert_trade_cards(results['trade_id'], id, g.user, False))
            g.db.commit()

        for id in user1_desired:
            cur.execute(sql.insert_trade_cards(results['trade_id'], id, g.user, True))   
            g.db.commit()

        return redirect(url_for('accept_trade', other_user_id=other_user_id)) #after post, redirect to accept stage

    #check and make sure there are no previously unresolved trades between the two parties
    if results is not None:
        return render_template("status.html", status_text="trade has already been initiated")

    #initiate a trade in the trade table
    cur.execute(sql.initiate_trade(g.user, other_user_id))
    g.db.commit()
    return render_template("status.html", status_text="trade initiated")


@app.route('/trade/<other_user_id>/accept', methods=['GET', 'POST'])
def accept_trade(other_user_id):
    status_text = None;
    cur = g.db.cursor()
    cur.execute(sql.check_trades(g.user, other_user_id)) #if a trade between user1 and user2 exists, return it
    results = cur.fetchone()

    #update trade cards on a post (user2's cards willing to trade)
    if request.method == 'POST':
        user2_cards = request.form['user2_cards'].split()

        for id in user2_cards:
            cur.execute(sql.insert_trade_cards(results['trade_id'], id, other_user_id, False))
            g.db.commit()

        return redirect(url_for('confirm_trade', other_user_id=other_user_id)) #after post, redirect to confirm stage

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
    cur.execute(sql.accept_trade(g.user,other_user_id))
    g.db.commit()
    return render_template("status.html", status_text="trade accepted")

@app.route('/trade/<other_user_id>/confirm', methods=['GET', 'POST'])
def confirm_trade(other_user_id):
    status_text = None
    cur = g.db.cursor()
    cur.execute(sql.check_trades(g.user, other_user_id))
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
    cur.execute(sql.confirm_trade(g.user,other_user_id))
    g.db.commit()
    return render_template("status.html", status_text="trade confirmed")

@app.route('/trade/<other_user_id>/perform', methods=['GET', 'POST'])
def perform_trade(other_user_id):
    status_text = None; 
    cur = g.db.cursor()
    cur.execute(sql.check_trades(g.user, other_user_id))
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

        if trade['from_id'] == int(g.user) and trade['desired'] == False :
            cur.execute(sql.trade_card(trade['card_id'], other_user_id))
            g.db.commit()

        elif trade['from_id'] == int(other_user_id) and trade['desired'] == False :
            cur.execute(sql.trade_card(trade['card_id'], g.user))
            g.db.commit()           

    return render_template("status.html", status_text="trade performed")

@app.route('/trade/<other_user_id>/cancel', methods=['GET', 'POST'])
def cancel_trade(other_user_id):
    cur = g.db.cursor()
    cur.execute(sql.cancel_trade(g.user,other_user_id))
    g.db.commit()
    return render_template("status.html", status_text="trade canceled")


@app.route('/purchase/<pack_id>', methods=['GET', 'POST'])
def purchase(pack_id):
    cur = g.db.cursor()
    # if request.method == 'POST':
    print session['user']
    print pack_id
    cur.execute(sql.purchase_pack(session['user'], pack_id))
    cur.execute(sql.get_user_points(session['user']))
    user_points = cur.fetchone()
    cur.execute(sql.get_pack_points(pack_id))
    pack_points = cur.fetchone()
    if user_points >= pack_points:
        cur.execute(sql.deduct_points(session['user'], pack_id))
        g.db.commit()
    else:
        return render_template("status.html", status_text="you dont have enough pts")       
    return render_template("status.html", status_text="trade complete")     
    # cur.execute(sql.get_pack(pack_id))
    # results = cur.fetchall()
    # #print results
    # return render_template("purchase_pack.html", results=results)

@app.route('/register', methods=['GET', 'POST'])
def register():
	status_text = None
	cur=g.db.cursor()
	if request.method == 'POST':
		full_name = request.form['full_name']
		email = request.form['email']
		password = request.form['password']
		confirm_password = request.form['confirm_password']
		
		if full_name == "":
			status_text = "Must input a name"

		elif email == "":
			status_text = "Must input an email"
	
		elif password == "":
			status_text = "Must input a password"

		elif confirm_password == "":
			status_text = "Must input password confirmation"

		elif password != confirm_password:
			status_text = "Password and password confirmation do not match"
	
		else:
			cur.execute(sql.check_registered(email))
			registered = cur.fetchone()
			print registered
			if registered is not None:
				status_text = "This email is already registered"

		if status_text is not None:
			return render_template("status.html", status_text=status_text)

		cur.execute(sql.register_user(email, full_name, password))
		g.db.commit()
		status_text="registration success"
	if status_text is not None:
		return render_template("status.html", status_text=status_text)
	else:
		return render_template("register.html")


@app.route('/export.json', methods=['GET', 'POST'])
@admin_required
def export():
	status_text = None
	export = {}
	cur = g.db.cursor()
 
	export['users'] = []
	cur.execute(sql.get_users())
	for user_row in cur.fetchall():
		export['users'].append(user_row)

	export['card'] = []
	cur.execute(sql.get_card())
	for card_row in cur.fetchall():
		export['card'].append(card_row)

	export['conference']=[]
	cur.execute(sql.get_conference())
	for conference_row in cur.fetchall():
		export['conference'].append(conference_row)

	export['division']=[]
	cur.execute(sql.get_division())
	for division_row in cur.fetchall():
		export['division'].append(division_row)

	export['packs']=[]
	cur.execute(sql.get_packs())
	for packs_row in cur.fetchall():
		export['packs'].append(packs_row)

	export['packs_players']=[]
	cur.execute(sql.get_packs_players())
	for packs_players_row in cur.fetchall():
		export['packs_players'].append(packs_players_row)

	export['player']=[]
	cur.execute(sql.get_player())
	for player_row in cur.fetchall():
		export['player'].append(player_row)

	export['team']=[]
	cur.execute(sql.get_packs())
	for team_row in cur.fetchall():
		export['team'].append(team_row)
	
	export['trade']=[]
	cur.execute(sql.get_trade())
	for trade_row in cur.fetchall():
		export['trade'].append(trade_row)

	export['trade_cards']=[]
	cur.execute(sql.get_trade_cards())
	for trade_cards_row in cur.fetchall():
		export['trade_cards'].append(trade_cards_row)

	json_result = json.dumps(export, indent=2)
	response = make_response(json_result)
	response.headers['Content-Disposition']="attachment;filename=export.json"
	response.headers['Content-Type']="application/json"
 
	return response

