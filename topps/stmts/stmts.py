def login(email, password):
    stmt = "SELECT * FROM users WHERE email='{0}' AND password=MD5('{1}');".format(email, password)
    print stmt
    return stmt

def get_user():
    stmt = "SELECT * FROM users WHERE id=%s LIMIT 1;"
    print stmt
    return stmt

def after_login():
    stmt = "UPDATE users SET last_points_given_at=CURRENT_TIMESTAMP, points = points + %s WHERE id = %s;"
    print stmt
    return stmt

def populate_card(player_id):
    stmt = "SELECT * FROM player WHERE id='{0}'".format(player_id)
    print stmt
    return stmt

def initiate_trade(user_id_1, user_id_2):
    stmt = "INSERT INTO trade (prop_id, accepter_id) VALUES ({0}, {1})".format(user_id_1, user_id_2)
    print stmt
    return stmt

def accept_trade(user_id_1, user_id_2):
    stmt = "UPDATE trade SET accepted_at=CURRENT_TIMESTAMP WHERE prop_id={0} AND accepter_id={1}".format(user_id_1,user_id_2) 
    print stmt
    return stmt

def confirm_trade(user_id_1, user_id_2):
    stmt = "UPDATE trade SET confirmed_at=CURRENT_TIMESTAMP WHERE prop_id={0} AND accepter_id={1}".format(user_id_1,user_id_2)
    print stmt
    return stmt

def cancel_trade(user_id_1, user_id_2):
    stmt = "DELETE FROM trade WHERE prop_id={0} AND accepter_id={1}".format(user_id_1, user_id_2)
    print stmt
    return stmt

def select_card(card_id):
    stmt = "SELECT * FROM card WHERE card_id = {0}".format(card_id)
    print stmt
    return stmt

def trade_card(card_id, new_owner_id):
    stmt = "UPDATE card SET current_owner_id={1} WHERE card_id={0}".format(card_id, new_owner_id)
    print stmt
    return stmt

def check_trades(user_id_1, user_id_2):
    stmt = "SELECT * FROM trade WHERE prop_id={0} AND accepter_id={1}".format(user_id_1, user_id_2)
    print stmt
    return stmt

def insert_trade_cards(trade_id, card_id, from_id, desired):
    stmt = "INSERT INTO `trade cards` (`trade_id` ,`card_id` ,`from_id` ,`desired`)VALUES ({0}, {1}, {2}, {3})".format(trade_id, card_id, from_id, desired)
    print stmt
    return stmt

def select_trade_cards(trade_id):
    stmt = "SELECT * FROM `trade cards` WHERE trade_id={0}".format(trade_id)
    print stmt
    return stmt


# (pack_name, points, [player_ids])
insert_pack = "INSERT (NULL, %s, %s) INTO packs;"
# (pack_id, player_id)
insert_pack_player = "INSERT (%s, %s) INTO packs_players;"

# ()
get_packs = """SELECT * FROM packs;"""

# (pack_id,)
get_pack = """SELECT * FROM packs 
                            INNER JOIN packs_players ON packs.pack_id = packs_players.pack_id 
                            INNER JOIN player ON player.id = packs_players.player_id
                       WHERE packs.pack_id = %s; """


# (user_id, pack_id)
purchase_pack = """INSERT INTO card
SELECT NULL, packs_players.player_id, %(user_id)s
FROM packs
INNER JOIN packs_players ON packs.pack_id = packs_players.pack_id
WHERE packs.pack_id = %(pack_id)s
AND (SELECT users.points FROM users WHERE users.id = %(user_id)s) > packs.points;"""

#(user_id, pack_id)
deduct_points = """UPDATE users
SET users.points = users.points - (SELECT packs.points FROM packs WHERE packs.pack_id = %(pack_id)s )
WHERE users.id = %(user_id)s;"""

#(user_id,)
get_user_points = """SELECT points FROM users WHERE id=%(user_id)s;"""

#(pack_id,)
get_pack_points = """SELECT points from packs WHERE pack_id=%(pack_id)s;"""
