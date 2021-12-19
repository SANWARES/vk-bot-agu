import requests
from bs4 import BeautifulSoup

agu = 'https://www.asu.ru/timetable/students/'
req = requests.get(agu)
req.encoding = 'utf-8'
src = req.text

soup = BeautifulSoup(src, 'lxml')
groups_class = soup.find_all(class_='link_ptr_left margin_bottom')
groups_href = [i.find('a').get('href') for i in groups_class]

get_id_by_number_group = {}
for i in range(len(groups_href)):
    get_id_by_number_group[str(i + 1)] = groups_href[i][:-1]

group_1_back = {}
full_href = [f'{agu}{i}' for i in groups_href]
for i in full_href:
    req = requests.get(i)
    req.encoding = 'utf-8'
    src = req.text

    soup = BeautifulSoup(src, 'lxml')
    href = soup.find_all(class_='link_ptr_left margin_bottom')

    href_list = {}
    for j in href:
        j_text = j.find('a').text
        j_href = j.find('a').get('href')
        href_list[j_href] = j_text
    group_1_back[i.split('/')[-2]] = href_list

print(group_1_back)
