def login(email, password):
	stmt = "SELECT * FROM users WHERE email='{0}' AND password=MD5('{1}');".format(email, password)
	print stmt
	return stmt
