import mechanize
import lxml
from lxml.etree import HTML
from lxml import html
from lxml.cssselect import CSSSelector as css
from urlparse import urljoin
from topps import app
from math import floor
from topps import util

db = util.connect_db()

cursor = db.cursor()

br = mechanize.Browser()

index_tree = html.fromstring(br.open("http://www.nfl.com/players").read())

get_team_links = css("#byTeamRosterTable a")
get_divisions = css("#byTeamRosterTable .bold")
team_links = [(anchor.text, anchor.get('href')) for anchor in get_team_links(index_tree)]

divisions = [div.text.split(" ") for div in get_divisions(index_tree)]
conferences = set([div[0] for div in divisions])
conference_ids = []

# for conf in conferences: 
#     cursor.execute("""INSERT INTO conference (name) VALUES ("{0}");""".format(conf))
#     print cursor.fetchall()

# for division in divisions:
#     print division[0], division[1]
#     cursor.execute("""INSERT INTO division (name, conference_name) VALUES ("{1}", "{0}");""".format(division[0], " ".join(division)))
#     db.commit()

def get_tree(url):
    return HTML(br.open(url).read())

def print_tree(tree):
    return lxml.etree.tostring(tree.getroottree(), pretty_print=True, method="html")

def absolute_url(relative):
    return urljoin(br.geturl(), relative)


get_players_row = css("#searchResults tbody:nth-child(2) tr")
get_td = css("td")


for index, (team_name, team_link) in enumerate(team_links):
    print team_name
    cursor.execute("""INSERT INTO team (name, division) VALUES ("{0}", "{1}");""".format(team_name, " ".join(divisions[int(floor(index / 4))])))
    players_tree = get_tree(absolute_url(team_link))
    rows = get_players_row(players_tree)
    for row in rows:
        data = [txt.strip() for txt in row.itertext() if len(txt.strip())]
        print data
        try:
            int(data[1])
        except ValueError:
            print "error"
            continue

        name = data[2].split(",")
        
        #print("""INSERT INTO player VALUES ("{0}", "{1}", {2}, "{3}", "{4}");""".format(name[1].strip(), name[0].strip(), int(data[1]), team_name, data[0]))
        cursor.execute("""INSERT INTO player VALUES ("{0}", "{1}", {2}, "{3}", "{4}");""".format(name[1].strip(), name[0].strip(), int(data[1]), team_name, data[0]))
    db.commit()

db.close()

