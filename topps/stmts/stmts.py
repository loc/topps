from MySQLdb import escape_string as e

# This makes sure the value looks like an int to start with.
ei = lambda val: e(str(int(val)))

# A decorator so we don't always have to do `print stmt; return stmt` at the end
def print_and_return(func):
    def pr_wrapper(*arg):
        res = func(*arg)
        print res
        return res
    return pr_wrapper

@print_and_return
def login(email, password):
    return "SELECT * FROM users WHERE email='{0}' AND password=MD5('{1}');".format(e(email), e(password))

@print_and_return
def get_user(user_id):
    return "SELECT * FROM users WHERE id={0} LIMIT 1;".format(ei(user_id))

@print_and_return
def after_login(user_id, extra_points):
    return "UPDATE users SET last_points_given_at=CURRENT_TIMESTAMP, points = points + {1} WHERE id = {0};".format(ei(user_id), ei(extra_points))

@print_and_return
def populate_card(player_id):
    return "SELECT * FROM player WHERE id={0} LIMIT 1;".format(ei(player_id))

@print_and_return
def initiate_trade(user_id_1, user_id_2):
    return "INSERT INTO trade (prop_id, accepter_id) VALUES ({0}, {1})".format(ei(user_id_1), ei(user_id_2))

@print_and_return
def accept_trade(user_id_1, user_id_2):
    return "UPDATE trade SET accepted_at=CURRENT_TIMESTAMP WHERE prop_id={0} AND accepter_id={1}".format(ei(user_id_1), ei(user_id_2))

@print_and_return
def confirm_trade(user_id_1, user_id_2):
    return "UPDATE trade SET confirmed_at=CURRENT_TIMESTAMP WHERE prop_id={0} AND accepter_id={1}".format(ei(user_id_1), ei(user_id_2))

@print_and_return
def cancel_trade(user_id_1, user_id_2):
    return "DELETE FROM trade WHERE prop_id={0} AND accepter_id={1}".format(ei(user_id_1), ei(user_id_2))

@print_and_return
def select_card(card_id):
    return "SELECT * FROM card WHERE card_id = {0}".format(ei(card_id))

@print_and_return
def trade_card(card_id, new_owner_id):
    return "UPDATE card SET current_owner_id={1} WHERE card_id={0}".format(ei(card_id), ei(new_owner_id))

@print_and_return
def check_trades(user_id_1, user_id_2):
    return "SELECT * FROM trade WHERE prop_id={0} AND accepter_id={1}".format(ei(user_id_1), ei(user_id_2))

@print_and_return
def insert_trade_cards(trade_id, card_id, from_id, desired):
    raw = "INSERT INTO `trade cards` (`trade_id` ,`card_id` ,`from_id` ,`desired`) VALUES ({0}, {1}, {2}, {3})"
    return raw.format(ei(trade_id), ei(card_id), ei(from_id), e(desired))

@print_and_return
def select_trade_cards(trade_id):
    return "SELECT * FROM `trade cards` WHERE trade_id={0}".format(ei(trade_id))

@print_and_return
def insert_pack(pack_name, points):
    return "INSERT INTO packs VALUES (NULL, {0}, {1});".format(e(pack_name), ei(points))

@print_and_return
def insert_pack_player(pack_id, player_id):
    return "INSERT INTO packs_players VALUES ({0}, {1})".format(ei(pack_id), ei(player_id))

@print_and_return
def get_packs():
    return "SELECT * FROM packs;"

@print_and_return
def get_pack(pack_id):
    return """SELECT *
              FROM packs
                   INNER JOIN packs_players ON packs.pack_id = packs_players.pack_id
                   INNER JOIN player ON player.id = packs_players.player_id
              WHERE packs.pack_id = {0};""".format(ei(pack_id))

@print_and_return
def purchase_pack(user_id, pack_id):
    return """INSERT INTO card
                          SELECT NULL, packs_players.player_id, {0}
                          FROM packs
                               INNER JOIN packs_players ON packs.pack_id = packs_players.pack_id
                          WHERE packs.pack_id = {1}
                          AND (SELECT users.points FROM users WHERE users.id = {0}) > packs.points;""".format(ei(user_id), ei(pack_id))

@print_and_return
def deduct_points(user_id, pack_id):
    return """UPDATE users
              SET users.points = users.points - (SELECT packs.points FROM packs WHERE packs.pack_id = {1} LIMIT 1)
              WHERE users.id = {0}
              LIMIT 1;""".format(ei(user_id), ei(pack_id))

@print_and_return
def get_user_points(user_id):
    return "SELECT points FROM users WHERE id={0};".format(ei(user_id))

@print_and_return
def get_pack_points(pack_id):
    return "SELECT points from packs WHERE pack_id={0};".format(ei(pack_id))
