import bs4 as bs4
import requests
import re

import time
import config
import lxml.html
import requests
import bs4 as bs4
import requests
import re
import random


exceptions = []

dir = {}



print(dir)
newdir = {}

def prepod_all():
    st = time.time()
    start = "http://www.asu.ru/timetable/lecturers/"
    main = requests.get(start)
    b = bs4.BeautifulSoup(main.text, "lxml")
    facults = b.find_all('div', class_='link_ptr_left margin_bottom')
    Group_2 = {}

    ma = []

    for facult in facults:
        hrefF = facult.find('a').get('href')
        NameF = facult.find('a').text
        division = requests.get(start + hrefF)
        b = bs4.BeautifulSoup(division.text, "lxml")
        bs4Division = b.find_all('div', class_='link_ptr_left margin_bottom')
        for div in bs4Division:
            hrefDiv = div.find('a').get('href')
            NameDivision = div.find('a').text
            teacher = requests.get(start + hrefF + hrefDiv)
            b = bs4.BeautifulSoup(teacher.text, "lxml")
            bs4Teacher = b.find_all('div', class_='link_ptr_left margin_bottom')
            for teacher in bs4Teacher:
                gIndex = teacher.find('a').get('href')
                Index = hrefF + hrefDiv + gIndex
                gName = teacher.find('a').text #.lower()
                Division = "%s -> %s" % (NameF, NameDivision)
                onlySurname = re.search("(\w+)", gName)
                print("Name: %s Индекс препода: %s Подразделение: %s" % (gName, Index, Division))
                ma.append(onlySurname[1])
                Group_2[gName] = [onlySurname[1], Index, Division]

        # print(start + hrefF)
    print(Group_2)
    print(time.time() - st)

    print(ma)

    return Group_2


from threading import Thread


def FindInfoPrepod(name1, name2, subj, start1, division):
    try:
        request = requests.get("https://www.asu.ru/search/persons/?query=%s" % name2,
                               timeout=10)
        # request = "https://www.asu.ru/search/persons/?query=Шлыкова"
        b = bs4.BeautifulSoup(request.text, "lxml")
        if b.find('div', class_='msg_simple'):
            newdir[name1.lower()] = [subj, name1, name1, division]
            print(newdir[name1.lower()])
            print("В списке нет преподавателя с фамилией {}".format(name1))
            # print(name1)
            # print(newdir)
        else:
            # Info = b.find_all('span')
            # newInfo = Info[1].text
            # name = Info[1].find('a')

            xm = b.find("ul", class_="proto_persons_list")
            li = xm.find_all('li')
            ll = False
            for i in li:
                Info = i.find_all('span')
                newInfo = Info[1].text
                name = Info[1].find('a').text

                newstr = re.search("(.*) (\w)?(\w+)? (\w)?(\w+)?", name)
                if newstr[4] == None:
                    kostul = ""
                else:
                    kostul = newstr[4]
                qq = newstr[1] + " " + newstr[2] + "." + kostul

                xD = re.search(qq, name1)
                if xD != None:
                    ll = True
                    print(xD[0])
                    newdir[name.lower()] = [subj, newInfo, name, division]
                    print(newdir[name.lower()])
            if ll == False:
                newdir[name1.lower()] = [subj, name1, name1, division]
                print("В списке нет преподавателя с фамилией {}".format(name1))

            print(newdir)
            # print(time.time() - start1)
    except Exception as e:
        time.sleep(random.randint(10))
        print("Ошибка: {} \n{}\n\n".format(name1, e.__str__()))






def create_threads():
    """
    Создаем группу потоков
    """
    start1 = time.time()

    ldir = len(new_sp)
    lcount = 0
    scount = 0
    for i in new_sp.items():
        # print(i)
        if lcount == 100:
            scount += 100
            lcount = 0
            print("%s из %s" % (scount, ldir))
        lcount += 1
        name1 = i[0]
        name2 = i[1][0]
        subj = i[1][1]
        division = i[1][2]
        FindInfoPrepod(name1, name2, subj, start1, division)

    print("КОНЕЦ")

    print(newdir)
    print(time.time() - start1)

    # for i in range(5):
    #        name = "Thread #%s" % (i + 1)
    #        my_thread = MyThread(name)
    #        my_thread.start()




new_prepod = prepod_all()

new_sp = {}

for z in new_prepod.items():
    table = False
    for old_dir in dir.values():

        if old_dir[0] == z[1][1]:
            table = True
            # print("Преподаватель %s есть " % i)
            break

    if table == False:
        print("Преподавателя %s нет в списке!" % z[0])
        new_sp[z[0]] = z[1][0], z[1][1], z[1][2]

print(new_sp)
print(len(new_sp))
create_threads()

