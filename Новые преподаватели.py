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

db_connector, db_cursor = config.db()
db_cursor.execute("SELECT * FROM `teacher`")
teacher_list = db_cursor.fetchall()
dir = {}


for n in teacher_list:
    dir[n[1]] = n[2], n[3], n[4], n[5]

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


class MyThread(Thread):
    """
    A threading example
    """

    def __init__(self, name1, name2, subj, start1, division):
        """Инициализация потока"""
        Thread.__init__(self)
        self.name1 = name1
        self.name2 = name2
        self.subj = subj
        self.start1 = start1
        self.division = division

    def run(self):

        """Запуск потока"""

        # print(self.name1)

        pr = [
            "87.226.213.120:8080",
            "46.63.162.171:8080",
            "91.205.239.120:8080",
            "5.164.202.196:3128",
            "95.167.143.11:8080",
            "178.176.60.215:8080",
            "178.206.225.2:3128",
            "87.225.90.97:3128",
            "195.182.135.237:3128",
            "90.154.107.221:3128",
            "81.30.211.222:3128",
            "213.208.169.253:3128",
            "212.38.127.94:3130",
            "82.114.241.138:8080",
            "37.193.184.95:8080",
            "91.214.70.99:3128",
            "87.254.138.170:4145",
            "185.12.228.110:3128",
            "62.33.207.196:80",
            "62.33.207.196:3128",
            "94.242.58.108:10010",
            "178.44.209.182:8081",
            "91.105.135.181:8081",
            "81.5.103.14:8081",
            "178.162.102.173:8081",
            "62.33.207.197:80",
            "62.33.207.98:80",
            "62.33.207.201:80",
            "62.33.207.201:3128",

            "178.206.225.2:3128",
            "5.164.202.196:3128",
            "78.186.237.196:8080",
            "198.211.108.93:8080",
            "186.249.68.49:38497",
            "118.99.127.88:3128",
            "131.221.178.220:38470"

        ]
        l = len(pr)
        proxy = {
            "http": pr[random.randint(0, l - 1)]
        }

        # print("Использован прокси: %s" % proxy)
        try:
            request = requests.get("https://www.asu.ru/search/persons/?query=%s" % self.name2, proxies=proxy,
                                   timeout=10)
            # request = "https://www.asu.ru/search/persons/?query=Шлыкова"
            b = bs4.BeautifulSoup(request.text, "lxml")
            if b.find('div', class_='msg_simple'):
                newdir[self.name1.lower()] = [self.subj, self.name1, self.name1, self.division]
                # print("В списке нет преподавателя с фамилией {}".format(self.name1))
                # print(self.name1)
                # print(newdir)
            else:
                # Info = b.find_all('span')
                # newInfo = Info[1].text
                # name = Info[1].find('a')

                xm = b.find("ul", class_="proto_persons_list")
                li = xm.find_all('li')
                self.ll = False
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

                    xD = re.search(qq, self.name1)
                    if xD != None:
                        self.ll = True
                        # print(xD[0])
                        newdir[name.lower()] = [self.subj, newInfo, name, self.division]
                if self.ll == False:
                    newdir[self.name1.lower()] = [self.subj, self.name1, self.name1, self.division]
                    # print("В списке нет преподавателя с фамилией {}".format(self.name1))

                # print(newdir)
                db_add_new(newdir)
                # print(time.time() - self.start1)
        except Exception as e:
            time.sleep(random.randint(0, 20))
            print("Ошибка: {} \n{}\n\n".format(self.name1, e.__str__()))
            self.run()


def db_add_new(teacher):
    import config
    str_commit = ""

    db_connector, db_cursor = config.db()
    count_all = 0
    count = 0

    for key in teacher.items():

        str_commit += "(NULL, '%s', '%s', '%s', '%s', '%s')" % (key[0], key[1][0], key[1][1], key[1][2], key[1][3])
        count += 1
        count_all += 1
        if count == 50 or count_all == len(teacher):
            str_commit += ";"
        else:
            str_commit += ", "

        if count == 50 or count_all == len(teacher):
            print(count_all)
            print(len(teacher))
            print(count)
            print("ЗАЛИВАЕМ В БД: \n%s" % str_commit)
            # commit
            db_cursor.execute(
                "INSERT INTO `teacher` (`id`, `Name_Search`, `Teacher_Index`, `Full_Info`, `Teacher_Name`, "
                "`Teacher_Division`) VALUES "
                "%s" % str_commit)
            str_commit = ""
            count = 0
            db_connector.commit()
            continue




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
        my_thread = MyThread(name1, name2, subj, start1, division)
        my_thread.start()
        time.sleep(1)


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

