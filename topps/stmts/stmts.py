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
