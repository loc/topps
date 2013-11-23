def login(email, password):
	stmt = "SELECT * FROM users WHERE email='{0}' AND password=MD5('{1}');".format(email, password)
	print stmt
	return stmt

def populate_card(player_id):
	stmt = "SELECT * FROM player WHERE id='{0}'".format(player_id)
	print stmt
	return stmt
