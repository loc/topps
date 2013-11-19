from bs4 import BeautifulSoup
#file_name = raw_input("Enter Filename: ")
soup=BeautifulSoup(open("redskins.html"))
contents = soup.find_all('a')
for element in contents:
	if 'href' in element.attrs:
		if element.get('href')[1:8] == 'players':
			number = element.parent.find_previous().string[:-1]
			name = element.string
			position = element.find_next().string
			games = element.find_next().find_next().string
			games_started = element.find_next().find_next().find_next().string
			birthdate = element.find_next().find_next().find_next().find_next().string
			college = element.find_next().find_next().find_next().find_next().find_next().string
			#print(element.parent.find_previous().string)
			#print(element.string)
			#print(element.find_next().string)
			#print(element.find_next().find_next().string)
			#print(element.find_next().find_next().find_next().string)
			#print(element.find_next().find_next().find_next().find_next().string)
			#print(element.find_next().find_next().find_next().find_next().find_next().string)
			print (number+", "+name+", "+position+", "+games+", "+games_started+", "+birthdate+", "+college)

	

