import twitter
from operator import attrgetter

api = twitter.Api(consumer_key="OytewwBIEg49pI75p4rxng", \
	consumer_secret="8vWStn0kR1OYekDjbzkwbSIpAExmbwz9IRyzRAugLg", \
	access_token_key="64895420-euoZUlFP9AOKSsuGodFdYMCuNuP3kUpoiBw3lORmt", \
	access_token_secret="tpRGcClns8vmZvTGw09F0UJjHxIZ4F4ghBsi663fA1CMH")

# this will probably read from the database. but for now...
players = ["Brett Favre", "Chad Ochocinco", "Reggie Bush", "Arthur Brown", "Jacoby Jones", "Peyton Manning"]

def GetUserWithMostFollowers(users):
	return max(users, key=attrgetter('followers_count'))

def SearchPlayer(term, count=3):
	users = api.GetUsersSearch(term, count)

	if term.lower() in users[0].name.lower():
		return users[0]

	return GetUserWithMostFollowers(users)


for player in players:
	pick = SearchPlayer(player)
	print pick.name, pick.screen_name