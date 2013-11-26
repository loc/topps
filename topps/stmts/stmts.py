def login(email, password):
	stmt = "SELECT * FROM users WHERE email='{0}' AND password=MD5('{1}');".format(email, password)
	print stmt
	return stmt

def get_user(user_id):
	stmt = "SELECT * FROM users WHERE id={0} LIMIT 1;".format(user_id)
	print stmt
	return stmt

def after_login(id, current_ts, extra_points):
    stmt = "UPDATE users SET last_points_given_at={1}, points = points + {2} WHERE id = {0};".format(id, current_ts, extra_points)
    print stmt
    return stmt
