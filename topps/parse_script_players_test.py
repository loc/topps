from bs4 import BeautifulSoup
#file_name = raw_input("Enter Filename: ")
soup=BeautifulSoup(open("redskins.html"))
contents = soup.find_all('a')
for element in contents:
	if 'href' in element.attrs :
		#print(element)
		if element.get('href')[1:8] == 'players' :
			number = element.find_parent().find_previous().string
			name = element.string
			position = element.find_next().string
			games_played = element.find_next().find_next().string
			games_started = element.find_next().find_next().find_next().string
			birthday = element.find_next().find_next().find_next().find_next().string
			college = element.find_next().find_next().find_next().find_next().find_next().string
			print(number)			
			print(name)
			print(position)
			print(games_played)
			print(games_started)
			print(birthday)
			print(college)
