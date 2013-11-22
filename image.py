import requests
from topps import app, util
import urllib

api_key = "AIzaSyCLwU-GzxT2dNPJb_MVN9siT2XDt9i6PVU"
cx = "000360205876112400002:4wuw1ts2yh4"

db = util.connect_db()
cursor = db.cursor()

def url(q):
	return "https://www.googleapis.com/customsearch/v1?key={1}&cx={2}&q={0}&searchType=image".format(q, api_key, cx)


# there's a 100 requests per day limit from google. have to fill this data in incrementally.

cursor.execute("SELECT id, first_name, last_name, team_name FROM player WHERE image_url IS NULL ORDER BY RAND() LIMIT 1;")

rows = cursor.fetchall()

for row in rows:
	query = " ".join([v for k, v in row.items() if k != "id"])
	result = requests.get(url(query))
	json = result.json()
	max_ratio = 0
	pick = None

	for item in json['items']:
		height, width, link = item['image']['height'], item['image']['width'], item['link']
		if height > width and height/width > max_ratio:
			pick, max_ratio = link, height/width

	if pick:
		print query, pick, int(row["id"])
		cursor.execute("UPDATE player SET image_url='{0}' WHERE id={1};".format(urllib.quote(pick), int(row["id"])))
		db.commit()
