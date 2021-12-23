import requests
from selenium import webdriver
from PIL import Image
from io import BytesIO

from selenium.webdriver import Proxy
from selenium.webdriver.common.proxy import ProxyType

from BarnaulTime import Time
from schedule_group import *
import os
from datetime import timedelta, datetime
import re
from config import *
import time
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import random


class PhantomJS:
    def __init__(self):
        global driver1, driver2, driver3, driver4, driver5, driver6, driver7, driver8, driver9, driver10
        __DRIVER = "/Users/alexander/Desktop/phantomjs-2.1.1-macosx/bin/phantomjs"

        __Chrome = "/Users/alexander/PycharmProjects/vk-bot-testing/chromedriver_96"

        chrome_options = webdriver.ChromeOptions()
        chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-sandbox")

        driver1 = webdriver.Chrome(executable_path=__Chrome, chrome_options=chrome_options)
        # driver2 = webdriver.Chrome(executable_path=__Chrome, chrome_options=chrome_options)
        # driver3 = webdriver.Chrome(executable_path=__Chrome, chrome_options=chrome_options)
        # driver4 = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)
        # driver5 = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)
        # driver6 = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)
        # driver7 = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)
        # driver8 = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)
        # driver9 = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)
        # driver10 = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)

        print('[{}] PhantomJS Successfully loaded'.format(Time().brnTime()))


class Push:
    def __init__(self, vk, free_req, id, group):
        self.college = college()
        self.teacher_dict = teacher()
        self.schedule_pairs = Number_Pairs()
        self.Housings = Housings()
        self.housing_room = Housing_room()
        self.id = id
        self.vk = vk
        self.free_req = free_req
        self.output_message = ""
        self.attach = ""
        self.group = group

    def screen(self, url, method, save_name, d_nac_bd="", d_kon_bd=""):
        if self.free_req == "1":
            driver = driver1
        elif self.free_req == "2":
            driver = driver2
        elif self.free_req == "3":
            driver = driver3
        # elif self.free_req == "4":
        #     driver = driver4
        # elif self.free_req == "5":
        #     driver = driver5
        # elif self.free_req == "6":
        #     driver = driver6
        # elif self.free_req == "7":
        #     driver = driver7
        # elif self.free_req == "8":
        #     driver = driver8
        # elif self.free_req == "9":
        #     driver = driver9
        else:
            driver = driver3
        driver.set_page_load_timeout(10)
        try:

            #
            # # https://still-mesa-50165.herokuapp.com/screenshot?link=lecturers/21/7/821/
            # schedule_re = re.search(r'http://www.asu.ru/timetable/(.*)', url)
            # print(schedule_re[1])
            # response = requests.get('https://still-mesa-50165.herokuapp.com/screenshot?link=%s' % schedule_re[1])
            # if response.status_code == 200:
            #     attachment = response.json()["attachment"]
            #     print(attachment)
            #     return attachment



            print(url)
            driver.get(url)
        except:
            self.vk.method("messages.send",
                           {"user_ids": self.id,
                            "intent": "default",
                            "message": "Сайт не отвечает на запрос. "
                                       "Потребуется больше времени чем обычно.",
                            "keyboard": """
{
  "inline": true,
  "buttons": [
    [
      {
        "action": {
          "type": "open_link",
          "link": "%s",
          "label": "Открыть через браузер"
        }
      }
    ]
  ]
}
""" % url,
                            "random_id": 0})
            try:
                print("Включено время ожидание 20 секунд")



                print(url)
                driver.set_page_load_timeout(10)
                driver.get(url)
            except:
                self.output_message = 'Сайт временно не доступен. Расписание занятий получить не удалось.'
                if d_nac_bd != "" or d_kon_bd != "":
                    self.output_message = self.schedule_if_no_exit(d_nac_bd, d_kon_bd, self.group)
                return
        time.sleep(0.5)

        S = lambda X: driver.execute_script('return document.body.parentNode.scroll' + X)
        driver.set_window_size(S('Width'), S('Height'))  # May need manual adjustment
        load_page_full = '{}.png'.format(random.randint(1, 1000000))
        driver.find_element_by_tag_name('body').screenshot(load_page_full)

        # png = driver.get_screenshot_as_png()
        im = Image.open(load_page_full)

        try:
            element = driver.find_element_by_class_name(method)
            location = element.location
            size = element.size
            left = location['x']
            top = location['y']
            right = left + size['width']
            bottom = location['y'] + size['height']
            im = im.crop((left, top, right, bottom))
            screen_schedule = '{}.png'.format(random.randint(1, 1000000))
            im.save(screen_schedule)
            # screen_schedule = "%s.png" % save_name
            #     im.save(screen_schedule)

            # driver.save_screenshot(screen_schedule)

            a = self.vk.method("photos.getMessagesUploadServer")
            try:
                b = requests.post(a['upload_url'], files={'photo': open(screen_schedule, 'rb')}, timeout=5).json()
                os.remove(screen_schedule)
                os.remove(load_page_full)
            except requests.exceptions.Timeout:
                self.output_message = self.schedule_if_no_exit(d_nac_bd, d_kon_bd, self.group)
                return
            c = self.vk.method('photos.saveMessagesPhoto',
                               {
                                   'photo': b['photo'],
                                   'server': b['server'],
                                   'hash': b['hash']
                               })[0]
            self.attach = f'photo{c["owner_id"]}_{c["id"]}'

        except Exception as e:
            try:
                driver.find_element_by_class_name("msg_simple")
                self.output_message = 'Расписания на данную неделю нет!'
                return
            except:
                pass
            if re.search("available via screen", e.__str__()) is not None:
                self.output_message = 'Расписания на данную неделю нет!'

            else:
                self.vk.method("messages.send",
                               {"peer_id": admin_vk_id(), "intent": "default", "message": "У @id%s(пользователя) "
                                                                                          "произошла ошибка: 6\n%s"
                                                                                          % (self.id, e.__str__()),
                                "random_id": 0})
                self.output_message = 'Произошла ошибка. Вы вернулись в главное меню!'
            return
        return

    def expense_count(self, var, id_type):
        day_today = datetime.now() + timedelta(hours=7)
        today_count = timedelta(day_today.isoweekday() - 1)
        beginning_of_week = day_today - today_count
        end_of_week = day_today + (timedelta(days=6) - today_count)

        if var[3] != "":
            stime = var[3].replace(" ", "")
            date_short = re.search("(\d{2}).(\d{2}).\d{2}$", stime)
            if date_short is not None:
                stime = "%s.%s.%s" % (date_short[1], date_short[2], datetime.now().year)
            received_user_date = datetime.strptime(stime, "%d.%m.%Y")
            today_count = timedelta(received_user_date.isoweekday() - 1)
            beginning_of_week = received_user_date - today_count
            end_of_week = received_user_date + (timedelta(days=6) - today_count)

            url = "http://www.asu.ru/timetable/%s?date=%s-%s" % (id_type,
                                                                 beginning_of_week.strftime('%Y%m%d'),
                                                                 end_of_week.strftime('%Y%m%d'))
            d_nac = beginning_of_week.strftime('%d.%m.%Y')
            d_kon = end_of_week.strftime('%d.%m.%Y')

        elif var[2] == "+":
            url = "http://www.asu.ru/timetable/%s?date=%s-%s" % (id_type,
                                                                 (beginning_of_week + timedelta(7)).strftime('%Y%m%d'),
                                                                 (end_of_week + timedelta(7)).strftime('%Y%m%d'))
            d_nac = (beginning_of_week + timedelta(7)).strftime('%d.%m.%Y')
            d_kon = (end_of_week + timedelta(7)).strftime('%d.%m.%Y')

        elif var[2] == "-":
            url = "http://www.asu.ru/timetable/%s?date=%s-%s" % (id_type,
                                                                 (beginning_of_week - timedelta(7)).strftime('%Y%m%d'),
                                                                 (end_of_week - timedelta(7)).strftime('%Y%m%d'))
            d_nac = (beginning_of_week - timedelta(7)).strftime('%d.%m.%Y')
            d_kon = (end_of_week - timedelta(7)).strftime('%d.%m.%Y')

        else:
            url = "http://www.asu.ru/timetable/%s" % id_type
            d_nac = beginning_of_week.strftime('%d.%m.%Y')
            d_kon = end_of_week.strftime('%d.%m.%Y')

        return url, d_nac, d_kon

    def freerooms_audiences(self, freerooms_audiences):
        d = datetime.now()
        if freerooms_audiences[3] != "":
            stime = freerooms_audiences[3].replace(" ", "")
            d = datetime.strptime(stime, "%d.%m.%Y")

        url = "http://www.asu.ru/timetable/freerooms/?date=%s%s&building=%s" % (d.strftime('%Y%m%d'),
                                                                                self.schedule_pairs[
                                                                                    freerooms_audiences[2]],
                                                                                self.Housings[
                                                                                    freerooms_audiences[1]])
        method = 'l-content-main'
        self.output_message = "Расписание свободных аудиторий\nКорпус: %s | Номер пары: %s | Дата: %s" % (
            freerooms_audiences[1].upper(), freerooms_audiences[2], d.strftime('%d.%m.%Y'))
        save_name = "%s-%s" % (self.schedule_pairs[freerooms_audiences[2]], self.Housings[freerooms_audiences[1]])
        self.screen(url, method, save_name)
        return [self.output_message, self.attach]

    def audiences_info(self, room, date):
        date_format = datetime.strptime(date, "%d.%m.%Y")

        # https://www.asu.ru/timetable/rooms/6/2107420329/?date=20210208-20210214
        url = "http://www.asu.ru/timetable/rooms/%s?date=%s" % (room, date_format.strftime('%Y%m%d'))
        method = 'l-content-main'
        self.output_message = "Расписание занятий в аудитории\nДата: %s" % date
        save_name = "%s-%s" % (room, date)
        self.screen(url, method, save_name)
        return [self.output_message, self.attach]

    def z_student(self, match, division, mtype=1, teacher_info=""):
        try:
            var = match
            if mtype == 1:
                id_type = "students/%s/%s" % (division, var[1])
                save_name = "%s-%s" % (division, var[1][:-1])

            else:
                id_type = division
                save_name = '{}'.format(random.randint(1, 1000000))

            url, d_nac, d_kon = self.expense_count(var, id_type)
            method = 'shedule_list'
            d_nac_bd = datetime.strptime(d_nac, '%d.%m.%Y').strftime('%Y-%m-%d')
            d_kon_bd = datetime.strptime(d_kon, '%d.%m.%Y').strftime('%Y-%m-%d')
            self.screen(url, method, save_name, d_nac_bd, d_kon_bd)

            if self.attach == "Расписания на данную неделю нет!" \
                    or self.output_message == "Расписания на данную неделю нет!":
                if mtype == 1:
                    self.output_message = "Расписания на данную неделю нет!"
                else:
                    self.output_message = teacher_info + "\n\nРасписания на данную неделю нет!"

                self.attach = ""

            elif self.output_message == "":
                if mtype == 1:
                    self.output_message = "Расписание занятий %s группы с %s по %s" % (
                        Group_1_back()[division][var[1]], d_nac, d_kon)
                else:
                    self.output_message = teacher_info + "\n\nРасписание занятий с %s по %s" % (d_nac, d_kon)

            gen_keyboard = """
                        {"inline": true, "buttons": [[ {"action": {"type": "text", "label": "Предыдущая"},"color": "primary"},{
                        "action": {"type": "text", "label": "Следующая"},"color": "primary"}],[ {"action": 
                        {"type": "open_link","link": "%s","label": "Открыть через браузер"}}]]}
                        """ % url

            self.push_schedule(self.output_message, self.attach, gen_keyboard)
            ret = "%s %s" % (id_type, d_nac)
            return ret
        except Exception as e:
            self.vk.method("messages.send",
                           {"peer_id": admin_vk_id(), "intent": "default", "message": "У @id%s(пользователя) "
                                                                                      "произошла ошибка: 5\n%s"
                                                                                      % (self.id, e.__str__()),
                            "random_id": 0})
            self.push_schedule("Произошла ошибка. Вы вернулись в главное меню", "", self.read_keyboard("main.json"))

    def change_week(self, last_schedule, mode, mtype=1, teacher_info=""):
        data_last_schedule = last_schedule.split()
        id_type = data_last_schedule[0]
        date = data_last_schedule[1]
        received_user_date = datetime.strptime(date, "%d.%m.%Y")

        day_today = received_user_date + timedelta(hours=7)
        today_count = timedelta(day_today.isoweekday() - 1)
        beginning_of_week = day_today - today_count
        end_of_week = day_today + (timedelta(days=6) - today_count)
        if mode == 0:
            url = "http://www.asu.ru/timetable/%s?date=%s-%s" % (id_type,
                                                                 (beginning_of_week - timedelta(7)).strftime('%Y%m%d'),
                                                                 (end_of_week - timedelta(7)).strftime('%Y%m%d'))
            d_nac = (beginning_of_week - timedelta(7)).strftime('%d.%m.%Y')
            d_kon = (end_of_week - timedelta(7)).strftime('%d.%m.%Y')
        else:
            url = "http://www.asu.ru/timetable/%s?date=%s-%s" % (id_type,
                                                                 (beginning_of_week + timedelta(7)).strftime('%Y%m%d'),
                                                                 (end_of_week + timedelta(7)).strftime('%Y%m%d'))
            d_nac = (beginning_of_week + timedelta(7)).strftime('%d.%m.%Y')
            d_kon = (end_of_week + timedelta(7)).strftime('%d.%m.%Y')
        if mtype == 1:
            self.output_message = "Расписание занятий с %s по %s" % (d_nac, d_kon)
        else:
            self.output_message = teacher_info + "\n\nРасписание занятий с %s по %s" % (d_nac, d_kon)

        method = 'shedule_list'
        save_name = '{}'.format(random.randint(1, 1000000))
        d_nac_bd = datetime.strptime(d_nac, '%d.%m.%Y').strftime('%Y-%m-%d')
        d_kon_bd = datetime.strptime(d_kon, '%d.%m.%Y').strftime('%Y-%m-%d')
        self.screen(url, method, save_name, d_nac_bd, d_kon_bd)
        ret = "%s %s" % (id_type, d_kon)

        if self.attach == "" and self.output_message == "" or \
                self.attach == "" and self.output_message == "Расписания на данную неделю нет!":
            if mtype == 1:
                self.output_message = "Расписания на данную неделю нет!"
            else:
                self.output_message = teacher_info + "\n\nРасписания на данную неделю нет!"
            # keyboard = VkKeyboard(inline=True)
            # keyboard.add_button("Главное меню", color=VkKeyboardColor.NEGATIVE)

            # self.push_schedule(self.output_message, self.attach, keyboard)
        gen_keyboard = """
        {"inline": true, "buttons": [[ {"action": {"type": "text", "label": "Предыдущая"},"color": "primary"},{
        "action": {"type": "text", "label": "Следующая"},"color": "primary"}],[ {"action": 
        {"type": "open_link","link": "%s","label": "Открыть через браузер"}}]]}
        """ % url

        self.push_schedule(self.output_message, self.attach, gen_keyboard)
        # self.push_schedule(output_message, attach, self.read_keyboard("schedule_inline.json"))
        return ret

    def push_schedule(self, output_message, attach, keyboard):
        self.vk.method("messages.send",
                       {"peer_id": self.id,
                        "intent": "default", "message": output_message,
                        "attachment": attach, "keyboard": keyboard,
                        "random_id": 0, "dont_parse_links": 1})

    def read_keyboard(self, filename, directory="keyboards/"):
        return open(directory + filename, "r", encoding="UTF-8").read()

    def find_week(self, date):
        WeekDays = ("Ошибка", "Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье")
        # workdate = datetime.strptime(date, "%Y-%m-%d")
        dayName = WeekDays[date.isoweekday()]

        return dayName

    def schedule_if_no_exit(self, date_now, date_end, group):
        send = ""
        self.db_connector, self.db_cursor = db()
        sql_query = "SELECT `Date`, `NumberPair`, `Time`, `Name_Subject`, `Teacher`, `Audience` " \
                    "FROM `schedule_parser` WHERE `User_Group` LIKE '%s' AND `Type` LIKE 'Добавлено' " \
                    "AND Date BETWEEN '%s' AND '%s' ORDER BY Date, NumberPair;" % (group, date_now, date_end)
        self.db_cursor.execute(sql_query)
        schedule_all = self.db_cursor.fetchall()
        if len(schedule_all) == 0:
            send = "Не удалось получить информацию из базы данных"
            return send
        else:
            one_day = ""
            for tab in schedule_all:
                if one_day == "" or one_day != tab[0]:
                    if one_day != tab[0]:
                        send += "\n"
                    one_day = tab[0]
                    week_name = self.find_week(one_day)
                    send += "%s (%s)\n" % (week_name, one_day.strftime('%d.%m.%Y'))

                send += "%s | %s | %s | %s | %s\n" % (tab[1], tab[2], tab[3], tab[4], tab[5])

            return send
