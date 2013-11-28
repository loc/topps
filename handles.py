import twitter
from operator import attrgetter
from topps import app, util
import urllib

db = util.connect_db()
cursor = db.cursor()

api = twitter.Api(consumer_key="OytewwBIEg49pI75p4rxng", \
	consumer_secret="8vWStn0kR1OYekDjbzkwbSIpAExmbwz9IRyzRAugLg", \
	access_token_key="64895420-euoZUlFP9AOKSsuGodFdYMCuNuP3kUpoiBw3lORmt", \
	access_token_secret="tpRGcClns8vmZvTGw09F0UJjHxIZ4F4ghBsi663fA1CMH")


cursor.execute("SELECT id, first_name, last_name, team_name FROM player WHERE image_url IS NOT NULL AND twitter IS NULL ORDER BY RAND() LIMIT 180;")
players = cursor.fetchall()

def GetUserWithMostFollowers(users):
	return max(users, key=attrgetter('followers_count'))

def SearchPlayer(term, count=3):
	users = api.GetUsersSearch(term, count)

	if not len(users):
		return

	if term.lower() in users[0].name.lower():
		return users[0]

	return GetUserWithMostFollowers(users)


for player in players:
	pick = SearchPlayer(player['first_name'] + " " + player['last_name'])
	if not pick:
		continue
	print pick.name, pick.screen_name
	cursor.execute("UPDATE player SET twitter='{0}' WHERE id={1};".format(pick.screen_name, int(player["id"])))
	db.commit()

db.close()
	