import json
from schedule_group import Group_1_back, Housing_room

from itertools import zip_longest
from math import ceil


def infoUsers():
    with open("JSON/Users.json", "r", encoding='utf-8') as read:
        UsersDir = json.load(read)
        return UsersDir


def saveUsers(UsersDir):
    with open("JSON/Users.json", "w", encoding='utf-8') as write:
        json.dump(UsersDir, write, indent=4, ensure_ascii=False)
        return


def chunkify(items, chunk_size):
    for i in range(0, len(items), chunk_size):
        yield items[i:i + chunk_size]


def ParseNumberGroup(message, type="group_schedule"):
    if type == "group_schedule":
        a = [i for i in Group_1_back()[message].values()]
    elif type == "audiences_info":
        a = [i for i in Housing_room()[message]]

    row_count = ceil(len(a) / 3)
    ma = ""
    for chunk in zip_longest(*chunkify(a, row_count), fillvalue=''):
        # print(chunk)  # 1 символ = 2 пробела
        for el in chunk:
            lesn = len(el)

            if (lesn == 3):
                ma += "{}&#12288;&#12288;&#12288;&#12288;&#12288;".format(el)
            elif (lesn == 4):
                ma += "{} &#12288;&#12288;&#12288;&#12288;".format(el)
            elif (lesn == 5):
                ma += "{}&#12288;&#12288;&#12288;&#12288;".format(el)
            elif (lesn == 6):
                ma += "{} &#12288;&#12288;&#12288;".format(el)
            elif (lesn == 7):
                ma += "{}&#12288;&#12288;&#12288;".format(el)
            elif (lesn == 8):
                ma += "{} &#12288;&#12288;&#12288;".format(el)

            else:
                ma += "{}&#12288;&#12288;".format(el)

        ma += "\n"
    return ma


facult = """
1. &#12288; АСП
2. &#12288; АСП-З
3. &#12288; УРАИС
4. &#12288; ЦППК.
5. &#12288; АЛТГУ
6. &#12288; ФК
7. &#12288; МК
8. &#12288; Биологии и биотехнологии (ИББ)
9. &#12288; Инс.гуманитарных наук (ИГН З)
10.&#12288;Инс.гуманитарных наук (ИГН.)
11.&#12288;Институт географии (ИНГЕО)
12.&#12288;Институт географии заоч. отд. (ИНГ-З)
13.&#12288;Институт гуманитарных наук (ИГН-З)
14.&#12288;Институт социальных наук (ИСН)
15.&#12288;Институт социальных наук ОЗО (ИСН-З)
16.&#12288;Исторический (ИИМО)
17.&#12288;ИФ заочн. отд. (ИИМ-З)
18.&#12288;ИХиХФТ (ИХХФТ)
19.&#12288;ИХиХФТ (ХХФТЗ)
20.&#12288;ИЦТЭФ (ИЦТЭФ)
21.&#12288;Колледж АГУ (СПО)
22.&#12288;Математики и инф.технологий (ИМИИТ)
23.&#12288;МИЭМИС (ЭФ)
24.&#12288;МИЭМИС веч. отд. (ЭФ-В)
25.&#12288;МИЭМИС заочн. отд. (ЭФ-З)
26.&#12288;Общий (ОБЩ)
27.&#12288;Переподготовки кадров (ФПК)
28.&#12288;Филиал г.Славгорода (ФСЛ)
29.&#12288;Юридический (ЮИ)
30.&#12288;Юридический заочн. отд. (ЮИ-З)
"""

facult_astats = ['1. &#12288; АСП', '2. &#12288; АСП-З', '3. &#12288; УРАИС', '4. &#12288; ЦППК.',
                 '5. &#12288; АЛТГУ', '6. &#12288; ФК', '7. &#12288; МК', '8. &#12288; Биологии и биотехнологии (ИББ)',
                 '9. &#12288; Инс.гуманитарных наук (ИГН З)', '10.&#12288;Инс.гуманитарных наук (ИГН.)',
                 '10.&#12288;Инс.гуманитарных наук (ИГН.)', '11.&#12288;Институт географии (ИНГЕО)',
                 '12.&#12288;Институт географии заоч. отд. (ИНГ-З)', '13.&#12288;Институт гуманитарных наук (ИГН-З)',
                 '14.&#12288;Институт социальных наук (ИСН)', '15.&#12288;Институт социальных наук ОЗО (ИСН-З)',
                 '16.&#12288;Исторический (ИИМО)', '17.&#12288;ИФ заочн. отд. (ИИМ-З)', '18.&#12288;ИХиХФТ (ИХХФТ)',
                 '19.&#12288;ИХиХФТ (ХХФТЗ)', '20.&#12288;ИЦТЭФ (ИЦТЭФ)', '21.&#12288;Колледж АГУ (СПО)',
                 '22.&#12288;Математики и инф.технологий (ИМИИТ)', '23.&#12288;МИЭМИС (ЭФ)',
                 '24.&#12288;МИЭМИС веч. отд. (ЭФ-В)', '25.&#12288;МИЭМИС заочн. отд. (ЭФ-З)',
                 '26.&#12288;Общий (ОБЩ)', '27.&#12288;Переподготовки кадров (ФПК)',
                 '28.&#12288;Филиал г.Славгорода (ФСЛ)', '29.&#12288;Юридический (ЮИ)',
                 '30.&#12288;Юридический заочн. отд. (ЮИ-З)']
