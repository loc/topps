def login(email, password):
	stmt = "SELECT * FROM users WHERE email='{0}' AND password=MD5('{1}');".format(email, password)
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
