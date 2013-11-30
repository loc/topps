from topps import app

from flask import Flask, request, session, g, render_template, redirect, url_for
# stmts does escaping internally
from stmts import stmts as sql
from util import *
import urllib
from datetime import datetime
from pprint import pprint
from MySQLdb import IntegrityError

app.jinja_env.filters['pretty_date'] = pretty_date

@app.before_request
def before_request():
    if '/static/' in request.path:
        return
    g.db = connect_db(app)
    g.user = session['user'] if 'user' in session else None
    g.notifications = None
    if g.user:
        cur = g.db.cursor()
        cur.execute(sql.get_user(g.user))
        user = cur.fetchone()
        if user:
            cur.execute(sql.get_notifications_count(g.user))
            g.notifications = int(cur.fetchone().values()[0])
            last_points_given_at = user["last_points_given_at"]
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
    return redirect(url_for('cards'))


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

@app.route('/active')
@login_required
def active_trades():
    cur = g.db.cursor()
    cur.execute(sql.get_active_trades(g.user))
    trades = cur.fetchall()

    return render_template("active_trades.html", trades=trades)


@app.route('/cards/')
@app.route('/cards/<int:id>')
@app.route('/cards/<int:id>/sort/<string:sort>')
@app.route('/cards/sort/<string:sort>')
@login_required
def cards(id=None, sort=None):
    if not id:
        id=g.user

    if sort:
        user, cards_sorted, is_my_own = cards_logic(id, sort)
        cards = None 
    else:
        cur = g.db.cursor()
        cur.execute(sql.get_user_cards(id))
        cards = cur.fetchall()

        cur.execute(sql.get_user(id))
        user = cur.fetchone()

        for i, card in enumerate(cards):
            cards[i]["image_url"] = urllib.unquote(card['image_url'])

        cards_sorted = None
        is_my_own = False
        if int(g.user) == int(user['id']):
            is_my_own = True


    return render_template("cards.html", cards=cards, sorted=cards_sorted, user=user, is_my_own=is_my_own, sort=sort)

def cards_logic(id, sort):
    cur = g.db.cursor()
    cur.execute(sql.get_user_cards(id))
    cards = cur.fetchall()

    cur.execute(sql.get_user(id))
    user = cur.fetchone()

    is_my_own = False
    if int(g.user) == int(user['id']):
        is_my_own = True

    for i, card in enumerate(cards):
        cards[i]["image_url"] = urllib.unquote(card['image_url'])

    cards_sorted = {'type': sort, 'cards': card_sort(cards, sort)}

    return (user, cards_sorted, is_my_own)

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


@app.route('/trade/propose/', methods=['GET', 'POST'])
@app.route('/trade/propose/<trade_id>', methods=['GET', 'POST'])
def propose_trade(trade_id=None):
    cur = g.db.cursor()
    if trade_id:
        cur.execute(sql.select_trade(trade_id))
        trade = cur.fetchone()

        cur.execute(sql.select_trade_cards(trade_id))
        cards = cur.fetchall()

        for i, card in enumerate(cards):
            cards[i]["image_url"] = urllib.unquote(card['image_url'])

        obj = defaultdict(list)
        for card in cards:
            obj[int(card['from_id'])].append(card)

        users = None
        if not trade['accepter_id']:
            cur.execute(sql.get_other_users(g.user))
            users = cur.fetchall()

        if int(g.user) == int(trade['last_edited']):
            counter = False
        else:
            counter = True

        return render_template("propose.html", trade=trade, grouped_cards=obj, users=users, counter=counter)
    else:
        if request.method == "POST":
            cards = request.form['cards'].split(',')
            user_with_cards = request.form['starting_with']
            other_user = user_with_cards if int(g.user) != int(user_with_cards) else None
            cur.execute(sql.initiate_trade(g.user, other_user, last_edited=g.user))
            trade_id = g.db.insert_id()

            # TODO: add a check to see if the user actually owns these cards
            if len(cards):
                for id in cards:
                    cur.execute(sql.insert_trade_cards(trade_id, id, user_with_cards, "0"))
                g.db.commit()

            return redirect(url_for('propose_trade', trade_id=trade_id))


@app.route('/trade/propose/<int:trade_id>/add/<int:user_id>/', methods=['GET', 'POST'])
@app.route('/trade/propose/<int:trade_id>/add/<int:user_id>/sort/<string:sort>/', methods=['GET', 'POST'])
def add_cards_to_trade(trade_id, user_id, sort="team"):
    cur = g.db.cursor()
    cur.execute(sql.select_trade(trade_id))
    trade = cur.fetchone()

    if not (g.user == str(trade['prop_id'] or g.user == str(trade['accepter_id']))):
        # user isn't involved
        return

    if request.method == "POST":

        if not trade['accepter_id']:
            cur.execute(sql.propose_trade(trade_id, user_id))

        cards = request.form['cards'].split(',')
        if len(cards):
            for id in cards:
                try:
                    cur.execute(sql.insert_trade_cards(trade_id, id, user_id, "0"))
                except IntegrityError:
                    pass
                g.db.commit()       

        cur.execute(sql.counter_trade(g.user, trade_id))
        
        return redirect(url_for('propose_trade', trade_id=trade_id))

    user, cards_sorted, is_my_own = cards_logic(user_id, sort)

    return render_template("add_cards.html", trade=trade, sorted=cards_sorted, user=user, is_my_own=is_my_own, sort=sort)

@app.route('/trade/propose/<int:trade_id>/remove', methods=['POST'])
def remove_cards_from_trade(trade_id):
    cur = g.db.cursor()
    # add checks in here to make sure not just anyone can delete from a trade 
    cards = request.form['cards'].split(',')
    if len(cards):
        for id in cards:
            cur.execute(sql.remove_trade_cards(trade_id, id))
        cur.execute(sql.counter_trade(g.user, trade_id))
        g.db.commit()

    return redirect(url_for('propose_trade', trade_id=trade_id))

@app.route('/trade/confirm/<int:trade_id>', methods=['GET'])
def confirm_trade(trade_id):
    cur = g.db.cursor()
    cur.execute(sql.select_trade(trade_id))
    trade = cur.fetchone()

    other_user = int(trade['accepter_id']) if int(g.user) == int(trade['prop_id']) else int(trade['prop_id'])

    #update trade table to include confirm timestamp
    cur.execute(sql.confirm_trade(trade_id))

    cur.execute(sql.select_trade_cards(trade_id))
    trade_results = cur.fetchall()
    for card in trade_results:
        if card['from_id'] == int(g.user):
            cur.execute(sql.trade_card(card['card_id'], other_user))
        else:
            cur.execute(sql.trade_card(card['card_id'], g.user))

    g.db.commit() 

    return redirect(url_for('cards'))


@app.route('/trade/cancel', methods=['GET', 'POST'])
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
