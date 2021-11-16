import bs4 as bs4
import requests
import re

import time
import requests
import bs4 as bs4
import requests
import re
import random


st = time.time()
start = "https://www.asu.ru/timetable/rooms/"
main = requests.get(start)
b = bs4.BeautifulSoup(main.text, "html.parser")
facults = b.find_all('div', class_='link_ptr_left margin_bottom')
Group_2 = {}
count = 0
ma = []

for facult in facults:
    facultGroupRef = facult.find('a').get('href')
    facultId = re.match("(\d+)", facultGroupRef)
    facultNameFull = facultId[1]
    print(facultNameFull)
    Group_2[facultNameFull] = {}
    print(facultGroupRef)
    facultName = facult.find('a').text
    division = requests.get(start + facultGroupRef)
    print(start + facultGroupRef)
    b = bs4.BeautifulSoup(division.text, "html.parser")
    bs4Division = b.find_all('div', class_='link_ptr_left margin_bottom')
    for div in bs4Division:
        count += 1
        numberGroupRef = div.find('a').get('href')
        numberName = div.find('a').text
        Group_2[facultNameFull][numberName.lower()] = numberGroupRef

    print(Group_2)

        # teacher = requests.get(start + facultGroupRef + numberGroupRef)
        # print(start + facultGroupRef + numberGroupRef)
        # b = bs4.BeautifulSoup(teacher.text, "html5lib")
        # bs4Teacher = b.find_all('div', class_='link_ptr_left margin_bottom')

    # print(start + facultGroupRef)

replace_find = {}


print(time.time() - st)
print(count) # 1187


