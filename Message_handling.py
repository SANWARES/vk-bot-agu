from vk_api.bot_longpoll import VkBotEventType
import threading
from vk_api.bot_longpoll import VkBotLongPoll
import vk_api
from image_push import *
import geo
import time
import re
from datetime import timedelta, datetime
from BarnaulTime import Time
from schedule_group import *
import json
from DataUsers import facult, ParseNumberGroup, facult_astats
from config import *
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

mysql_dir = {}
keyboardDir = {}
connectError = []
close_driver = {
    "1": False,
    "2": False,
    "3": False,
    "4": False,
    "5": False,
    "6": False,
    "7": False,
    "8": False,
    "9": False,
    "10": False
}

image_push_of_day = 0



class PostDocument:
    def __init__(self, vk, message_id):
        self.attach = ""
        self.vk = vk
        self.message_id = message_id

    def send_the_resulting_attach(self):
        attach_message = self.vk.method("messages.getById",
                                        {
                                            "message_ids": self.message_id,
                                            "preview_length": "0"
                                        })

        text_and_attach = {}
        count = 0

        attach_a = ""
        text_a = attach_message["items"][count]["text"]
        if len(attach_message["items"][count]["attachments"]) == 0:
            attach_a = ""
        else:
            for attach in attach_message["items"][count]["attachments"]:
                attach_type = attach["type"]
                post_id = attach[attach_type]["owner_id"]
                number_id = attach[attach_type]["id"]
                try:
                    access_key = attach[attach_type]["access_key"]

                except:
                    return "USER_DOC"
                attach_a += "{}{}_{}_{},".format(attach_type, post_id, number_id, access_key)

        text_and_attach[text_a] = attach_a
        count += 1

        return text_and_attach


class GetInformationWithDB:
    def __init__(self):
        try:
            global mysql_dir
            self.db_connector, self.db_cursor = db()
            self.db_cursor.execute("SELECT * FROM `user`")
            user_vk = self.db_cursor.fetchall()
            for user in user_vk:
                mysql_dir[user[1]] = user[2], \
                                     user[3], \
                                     user[4], \
                                     user[5], \
                                     user[6], \
                                     user[7], \
                                     user[8], \
                                     user[9], \
                                     user[10]

            print("Подключен к базе данных")

        except Exception as e:
            mysql_connect_error = re.search("MySQL server", e.__str__())
            if mysql_connect_error is not None:
                print("Бот не смог подключиться к базе данных\n%s" % e.__str__())
                GetInformationWithDB()



class VkBot:
    def __init__(self, vk, event):
        global mysql_dir, close_driver, image_push_of_day
        self.message = event.object.message["text"].lower()
        self._message = event.object.message["text"]
        self.event = event
        self.attach = ''
        self.put_id = event.object.message["peer_id"]
        self.attach_message = event.object.message["attachments"]
        self.message_id = event.object.message["id"]
        self.command_cancel = ["reg", "main", "главное меню"]
        self.keyboard_setting = ["Настройки"]
        self.college = college()
        self.teacher_dict = teacher()
        self.schedule_pairs = Number_Pairs()
        self.Housings = Housings()
        self.user_vk = self.authorization()

        self.division = self.user_vk[0]
        self.group = self.user_vk[1]
        self.role = self.user_vk[2]
        self.link_doc = self.user_vk[3]
        self.setting = int(self.user_vk[4])
        self.mode = self.user_vk[5]
        self.msg = self.user_vk[6]
        self.buffer = self.user_vk[7]
        self.notification_schedule = self.user_vk[8]
        self.output_message = ""
        self.vk = vk

        if self.event.object["client_info"].get("inline_keyboard") is not None:
            self.check_keyboard_mode = "1"

        elif self.event.object["client_info"].get("button_actions") is not None:
            if len(self.event.object["client_info"]["button_actions"]) > 1:
                self.check_keyboard_mode = "2"
            else:
                self.check_keyboard_mode = "3"

        else:
            self.check_keyboard_mode = "3"

        if self.msg == "3" or self.msg == "2":
            self.keyboard_main = self.read_keyboard("main_admin.json")
        elif self.msg == "1":
            self.keyboard_main = self.read_keyboard("main_teacher_verified.json")
        elif self.role == "преподаватель":
            self.keyboard_main = self.read_keyboard("main_teacher.json")
        else:
            self.keyboard_main = self.read_keyboard("main.json")

    def check_open_phantom(self):
        for c in close_driver.items():
            if c[1] == False:
                close_driver[c[0]] = True
                return c[0]
        return "1"

    def update_data_db(self, division, user_group, role, link_doc, setting, mode, send_msg, buffer,
                       notification_schedule):
        mysql_dir[self.put_id] = division, user_group, role, link_doc, setting, \
                                 mode, send_msg, buffer, notification_schedule
        try:
            self.db_connector, self.db_cursor = db()
            self.db_cursor.execute(
                "UPDATE `user` SET `division` = '%s', `user_group` = '%s', `role` = '%s',"
                " `setting` = '%s', `mode` = '%s', `send_msg` = '%s',"
                " `buffer` = '%s', `notification_schedule` = '%s' WHERE `user`.`vk_id` = %s;" % (division, user_group,
                                                                                                 role, setting,
                                                                                                 mode, send_msg, buffer,
                                                                                                 notification_schedule,
                                                                                                 self.put_id))
            self.db_connector.commit()

        except Exception as e:
            self.vk.method("messages.send",
                           {"peer_id": admin_vk_id(), "message": "У @id%s(пользователя) "
                                                                 "произошла ошибка:\n%s"
                                                                 % (self.put_id, e.__str__()), "random_id": 0})
        return

    def result(self):
        try:
            self.new_message()
            print("[{}] Сообщение отправлено: {} | Затраченное время:{}".format(Time().brnTime(), self.put_id,
                                                                                round(time.time() - self.c_begin, 9)))
            return

        except Exception as e:
            close_driver[self.free_req] = False
            self.vk_send("Произошла ошибка. Вы вернулись в главное меню", "",
                         self.keyboard_main)
            self.vk.method("messages.send",
                           {"peer_id": admin_vk_id(), "message": "У @id%s(пользователя) "
                                                                 "произошла ошибка:\n%s"
                                                                 % (self.put_id, e.__str__()), "random_id": 0})

            self.update_data_db(self.division, self.group, self.role, self.link_doc, "11", "main", self.msg, "0",
                                self.notification_schedule)

    def funct(self):
        send = ""
        self.db_cursor.execute(
            "SELECT `message_id` FROM `notes` WHERE `vk_id` LIKE %s AND `message_send` LIKE '0'" % self.put_id)
        message_id = self.db_cursor.fetchall()
        if len(message_id) == 0:
            self.output_message = "У вас нет объявлений!"
        else:
            for note in message_id:
                send += "{}, ".format(note[0])
            attach = PostDocument(self.vk, send).send_the_resulting_attach()

            return attach

    def exist_list_doc(self):
        count = 1
        send = ""
        self.db_connector, self.db_cursor = db()
        self.db_cursor.execute(
            "SELECT `title`, `message_id` FROM `post` WHERE `vk_id` = '%s'" % self.put_id)
        title_for_user = self.db_cursor.fetchall()
        if len(title_for_user) == 0:
            output_message = "У вас нет созданых записей!"
        else:
            for title in title_for_user:
                send += "ID: %s | %s\n" % (count, title[0])
                count += 1
            output_message = send
        return output_message, title_for_user

    def generator_date_keyboard(self):
        current_time = (datetime.now() + timedelta(hours=7)).strftime('%d.%m.%Y')
        d = datetime.strptime(current_time, "%d.%m.%Y")
        days_of_keyboard = 0
        separator_of_keyboard = 1
        keyboard = VkKeyboard(one_time=True)

        while days_of_keyboard < 24:
            keyboard.add_button(d.strftime('%d.%m.%Y'), color=VkKeyboardColor.PRIMARY)

            if separator_of_keyboard == 3:
                separator_of_keyboard = 0
                keyboard.add_line()

            d = d + timedelta(days=1)
            separator_of_keyboard += 1
            days_of_keyboard += 1

        keyboard.add_button("Главное меню", color=VkKeyboardColor.NEGATIVE)
        return keyboard

    def check_mode(self):
        if self.message == "main" or self.message == "главное меню":
            if self.check_keyboard_mode == "3":
                self.vk_send("Вы вернулись в главное меню\n\nДля работы с ботом без клавиатуры "
                             "используйте следующие команды:\n✅ Расписание группы\n✅ Расписание преподавателя\n"
                             "✅ Свободные аудитории\n✅ Заметки\n✅ Панель управления\n⛔ Настройки", "",
                             self.keyboard_main)
            else:
                self.vk_send("Вы вернулись в главное меню", "", self.keyboard_main)
            self.update_data_db(self.division, self.group, self.role, self.link_doc, "11", "main", self.msg, "0",
                                self.notification_schedule)
            return

        elif self.message == "рассылка сообщений":
            if self.msg == "0":
                self.vk_send("У вас нет прав для использования данной команды!")
                return

            elif self.role == "студент" and self.msg == "1":
                self.vk_send("Для отправки сообщений авторизуйтесь как преподаватель!")
                return

            elif self.msg == "3":
                self.vk_send("Кому вы хотите отправить сообщение?", "",
                             self.read_keyboard("admin_msg_push.json"))

            else:
                self.vk_send("Кому вы хотите отправить сообщение?", "",
                             self.read_keyboard("teacher_msg_push.json"))
            self.update_data_db(self.division, self.group, self.role, self.link_doc, "30",
                                "msg", self.msg, self.buffer, self.notification_schedule)
            return

        elif self.message == "adm" and self.put_id == admin_vk_id():
            self.vk_send("Админка выдана!")
            self.update_data_db(self.division, self.group, "студент", self.link_doc, self.setting,
                                self.mode, "3", self.buffer, self.notification_schedule)
            return

        elif self.message == "image stats" and self.put_id == admin_vk_id():
            global image_push_of_day
            self.vk_send(image_push_of_day)
            return

        elif self.message == "reg" or self.mode == "reg":
            if self.message == "reg" or self.message == "назад":
                self.mode = "reg"
                self.setting = 0
            self.registration()
            return

        elif self.mode == "main":
            match = re.search(r'(\d+\w)([-+]?)((\s\d+[.|-]\d+[.|-]\d+)?)', self.message)
            go_keyboard = re.search("kb https://vk.com/id(.*)", self.message)  # https://vk.com/69cucumber69

            go_reg = re.search("go reg (\d+)", self.message)
            so_reg = re.search("so reg (\d+)", self.message)
            freerooms_audiences = re.search(r'^(\w) (\d)((\s\d+[.|-]\d+[.|-]\d+)?)', self.message)

            if match is not None and match[1] in Group_1()[self.division]:
                self.free_req = self.check_open_phantom()
                image_push_of_day += 1
                output_message, attach = Push(self.vk, self.free_req, self.put_id).z_student(match, self.division)
                close_driver[self.free_req] = False
                self.vk_send(output_message, attach)
                return

            elif go_keyboard is not None and go_keyboard[1] in mysql_dir and self.msg == "3":
                self.vk_send("Пользователь отправлен на орбиту!")
                self.put_id = str(go_keyboard[1])
                if (self.check_keyboard_mode == "3"):
                    self.vk_send("Вы вернулись в главное меню\n\nДля работы с ботом без клавиатуры "
                                 "используйте следующие команды:\n✅ Расписание группы\n✅ Расписание преподавателя\n"
                                 "✅ Свободные аудитории\n✅ Заметки\n✅ Панель управления\n⛔ Настройки", "",
                                 self.keyboard_main)
                else:
                    self.vk_send("Вы вернулись в главное меню", "", self.keyboard_main)
                self.update_data_db(mysql_dir[self.put_id][0], mysql_dir[self.put_id][1], mysql_dir[self.put_id][2],
                                    mysql_dir[self.put_id][3], "11",
                                    "main", mysql_dir[self.put_id][6], "0", self.notification_schedule)
                return

            elif go_reg is not None and go_reg[1] in mysql_dir and self.msg == "3":
                self.vk_send("Пользователь отправлен на орбиту!")
                self.put_id = str(go_reg[1])
                self.vk_send("%s\n\nВведите номер факультета" % facult)
                self.update_data_db(mysql_dir[self.put_id][0], mysql_dir[self.put_id][1], mysql_dir[self.put_id][2],
                                    mysql_dir[self.put_id][3], "1",
                                    "reg", mysql_dir[self.put_id][6], "0", mysql_dir[self.put_id][8])

                return

            elif so_reg is not None and self.msg == "3":
                self.vk_send("Пользователь отправлен на орбиту!")
                self.put_id = str(so_reg[1])
                self.db_connector, self.db_cursor = db()
                self.mode = "reg"
                self.setting = 0
                self.authorization()
                return

            elif freerooms_audiences is not None and freerooms_audiences[2] in self.schedule_pairs and \
                    freerooms_audiences[1] in self.Housings:
                self.free_req = self.check_open_phantom()
                image_push_of_day += 1
                output_message, attach = Push(self.vk, self.free_req, self.put_id).freerooms_audiences(
                    freerooms_audiences)
                close_driver[self.free_req] = False
                self.vk_send(output_message, attach)
                return

            elif self.message == "настройки":
                if self.notification_schedule == "1":
                    push_keyboard = self.read_keyboard("setting.json")
                else:
                    push_keyboard = self.read_keyboard("setting_set_schedule.json")

                if (self.check_keyboard_mode == "3"):
                    self.vk_send("Вы перешли в меню настроек\n\nДля работы с ботом без клавиатуры "
                                 "используйте следующие команды:\n"
                                 "✅ Уведомление об изменении в расписании\n✅ Регистрация\n✅ Сообщить об ошибке\n"
                                 "⛔ Главное меню", "", push_keyboard)
                else:
                    self.vk_send("Вы перешли в меню настроек", "", push_keyboard)

                self.update_data_db(self.division, self.group, self.role, self.link_doc, "100",
                                    "setting", self.msg, self.buffer, self.notification_schedule)




            elif self.message == "расписание группы":
                if (self.check_keyboard_mode == "3"):
                    self.vk_send("Вы перешли в меню с получением расписания\n\nДля работы с ботом без клавиатуры "
                                 "используйте следующие команды:\n✅ <-\n✅ Текущая\n"
                                 "✅ ->\n✅ Другая группа\n✅ Другая дата\n⛔ Главное меню", "",
                                 self.read_keyboard("schedule_user.json"))
                else:
                    self.vk_send("Вы перешли в меню с получением расписания", "",
                                 self.read_keyboard("schedule_user.json"))
                self.update_data_db(self.division, self.group, self.role, self.link_doc, "50",
                                    "schedule", self.msg, self.buffer, self.notification_schedule)
                return

            elif self.message == "панель управления" and (self.msg == "3" or self.msg == "2"):
                if self.msg == "3":
                    self.vk_send("Вы перешли в админ панель", "", self.read_keyboard("admin.json"))
                elif self.msg == "2":
                    self.vk_send("Вы перешли в панель управления ботом", "", self.read_keyboard("Editor.json"))
                self.update_data_db(self.division, self.group, self.role, self.link_doc, "70",
                                    "admin", self.msg, self.buffer, self.notification_schedule)
                return

            elif self.message == "расписание преподавателя":
                if self.role == "студент":
                    if (self.check_keyboard_mode == "3"):
                        self.vk_send("Введите инициалы преподавателя. Допускаются любые сокращения, и даже в фамилии "
                                     "преподавателя\n\n"
                                     "Для работы с ботом без клавиатуры "
                                     "используйте следующие команды:\n⛔ Главное меню", "",
                                     self.read_keyboard("return.json"))
                    else:
                        self.vk_send("Введите инициалы преподавателя. Допускаются любые сокращения, и даже в фамилии "
                                     "преподавателя", "", self.read_keyboard("return.json"))

                elif self.role == "преподаватель":
                    self.vk_send("Выберите дальнейшее действие", "",
                                 self.read_keyboard("mode_teacher_schedule.json"))
                    self.update_data_db(self.division, self.group, self.role, self.link_doc, "50",
                                        "schedule", self.msg, self.buffer, self.notification_schedule)
                    return
                self.update_data_db(self.division, self.group, self.role, self.link_doc, "55",
                                    "schedule", self.msg, self.buffer, self.notification_schedule)
                return

            elif self.message == "заметки":
                if (self.check_keyboard_mode == "3"):
                    self.vk_send("Вы перешли в меню заметок. Здесь вы можете добавлять свои"
                                 " заметки, и указывать к ним значения\n\n"
                                 "Для работы с ботом без клавиатуры "
                                 "используйте следующие команды:\n✅ Список\n✅ Добавить\n✅ Удалить\n⛔ Главное меню",
                                 "", self.read_keyboard("advertisement.json"))
                else:
                    self.vk_send("Вы перешли в меню заметки. Здесь вы можете добавлять свои"
                                 " заметки, и указывать к ним значения", "", self.read_keyboard("advertisement.json"))
                self.update_data_db(self.division, self.group, self.role, self.link_doc, "80",
                                    "post", self.msg, self.buffer, self.notification_schedule)
                return

            elif self.message == "свободные аудитории":
                if self.check_keyboard_mode == "3":
                    self.vk_send("Выберите корпус из списка предложенных, или отправьте свое местоположение нажав на "
                                 "соответствующую кнопку, и "
                                 "мы найдем ближайший корпус к вам\n\n"
                                 "Для работы с ботом без клавиатуры "
                                 "используйте следующие команды:\n✅ Д\n✅ К\n✅ Л\n✅ М\n✅ Н\n✅ С\n✅ А\n✅ Э\n"
                                 "⛔ Главное меню")
                else:
                    self.vk_send("Выберите корпус из списка предложенных, или отправьте свое местоположение нажав на "
                                 "соответствующую кнопку, и "
                                 "мы найдем ближайший корпус к вам", "", self.read_keyboard("location.json"))
                self.update_data_db(self.division, self.group, self.role, self.link_doc, "60",
                                    "location", self.msg, self.buffer, self.notification_schedule)
                return

            elif self.message == "расписание групп":
                self.vk_send("%s\n\nВведите номер группы" % ParseNumberGroup(self.division), "",
                             self.read_keyboard("new_facult.json"))
                self.update_data_db(self.division, self.group, self.role, self.link_doc, "51",
                                    "schedule", self.msg, self.buffer, self.notification_schedule)
                return

            elif self.message == "объявления":
                self.vk_send("Выберите дальнейшее действие!", "", self.read_keyboard("advertisement.json"))
                self.update_data_db(self.division, self.group, self.role, self.link_doc, "40",
                                    "note", self.msg, self.buffer, self.notification_schedule)
                return



            elif self.message == "stats":
                self.vk_send("Роль в системе: {}\nГруппа: {}\nСпециальность: {}\n" \
                             "Мод: {}\nSetting: {}\nОтправка сообщений: {}".format(self.role,
                                                                                   self.group,
                                                                                   self.division,
                                                                                   self.mode,
                                                                                   self.setting,
                                                                                   self.msg))
                return

            elif self.message == "edit":
                self.db_connector, self.db_cursor = db()
                self.db_cursor.execute(
                    "SELECT `vk_id`, `message_id` FROM `notes` WHERE `message_send` LIKE '0'")
                send = ""
                message_id = self.db_cursor.fetchall()
                if len(message_id) == 0:
                    self.output_message = "Нет объявлений для редакции"
                else:
                    for note in message_id:
                        send += "{}, ".format(note[1])
                    attach = PostDocument(self.vk, send).send_the_resulting_attach()
                    count = 0
                    for message, investments in attach.items():
                        count += 1
                        self.vk_send("{}. {}".format(count, message),
                                     investments)
                    self.output_message = "В данный момент у вас %s объявления ожидают проверки модерацией" % count
                self.vk_send(self.output_message)
                return



            elif self.output_message is None:
                self.vk_send(self._message)
                return

        elif self.mode == "admin":
            if self.setting == 70 and (self.msg == "3" or self.msg == "2"):
                if self.message == "статистика":
                    self.db_connector, self.db_cursor = db()
                    con = 0
                    text = ""
                    for cel in get_id_by_number_group().values():
                        self.db_cursor.execute(
                            "SELECT * FROM `user` WHERE `division` LIKE '%s'" % cel)
                        text += "%s (%s)\n" % (facult_astats[con], len(self.db_cursor.fetchall()))
                        con += 1

                    self.db_cursor.execute("SELECT * FROM `user`")

                    text += "Всего: %s\n" % (len(self.db_cursor.fetchall()))

                    self.vk_send(text + "\n\nВведите номер факультета на который "
                                        "Вы хотите получить списки", "", self.read_keyboard("return.json"))
                    self.update_data_db(self.division, self.group, self.role, self.link_doc, "71",
                                        "admin", self.msg, self.buffer, self.notification_schedule)



                elif self.message == "резервное копирование":
                    self.vk_send("Сообщения сообщества отключены!")
                    self.vk.method("groups.setSettings", {
                        "messages": 0,
                        "group_id": 183787572})
                    sql_update = ""
                    for user in mysql_dir.items():
                        user_id = user[0]
                        division = user[1][0]
                        user_group = user[1][1]
                        role = user[1][2]
                        setting = user[1][4]
                        mode = user[1][5]
                        send_msg = user[1][6]
                        buffer = user[1][7]
                        notification_schedule = user[1][8]

                        sql_update += "UPDATE `user` SET `division` = '%s', `user_group` = '%s', `role` = '%s', " \
                                      "`setting` = '%s', `mode` = '%s', `send_msg` = '%s', " \
                                      "`buffer` = '%s', `notification_schedule` = '%s' WHERE `user`.`vk_id` = %s; " \
                                      % (division, user_group, role,
                                         setting, mode, send_msg,
                                         buffer, notification_schedule, user_id)

                    try:
                        self.db_connector, self.db_cursor = db()
                        self.db_cursor.execute(sql_update)
                        self.db_connector.commit()

                    except Exception as e:
                        self.vk.method("messages.send",
                                       {"peer_id": admin_vk_id(), "message": "Поизошла ошибка:\n%s"
                                                                             % e.__str__(), "random_id": 0})

                    self.vk.method("groups.setSettings", {
                        "messages": 1,
                        "bots_capabilities": 1,
                        "bots_start_button": 1,
                        "group_id": 183787572})

                    self.vk_send("Резервное копирование завершено!", "", self.keyboard_main)
                    self.update_data_db(self.division, self.group, self.role, self.link_doc, "11",
                                        "main", self.msg, self.buffer, self.notification_schedule)



                elif self.message == "отключение сообщений":
                    self.vk_send("Сообщения сообщества отключены!")
                    self.vk.method("groups.setSettings", {
                        "messages": 0,
                        "group_id": 183787572})

                elif self.message == "удаление сообщений":
                    self.vk_send("Перешлите сообщение с которого нужно удалить", "", self.read_keyboard("return.json"))

                    self.update_data_db(self.division, self.group, self.role, self.link_doc, "73",
                                        "admin", self.msg, self.buffer, self.notification_schedule)

            elif self.setting == 71 and (self.msg == "3" or self.msg == "2"):
                try:
                    if self.message in get_id_by_number_group():

                        self.db_connector, self.db_cursor = db()
                        text = ""
                        for cel in Group_1()[get_id_by_number_group()[self.message]]:
                            self.db_cursor.execute("SELECT * FROM `user` WHERE `division` "
                                                   "LIKE '%s' AND `user_group` LIKE '%s'"
                                                   % (get_id_by_number_group()[self.message], cel))

                            text += "%s (%s)\n" % (cel, len(self.db_cursor.fetchall()))
                        if self.msg == "3":

                            self.vk_send(text + "\n\nВведите номер группы", "",
                                         self.read_keyboard("return.json"))
                            self.update_data_db(self.division, self.group, self.role, self.link_doc, "72",
                                                "admin", self.msg, get_id_by_number_group()[self.message],
                                                self.notification_schedule)

                        elif self.msg == "2":
                            self.vk_send(text, "", self.keyboard_main)
                            self.update_data_db(self.division, self.group, self.role, self.link_doc, "11",
                                                "main", self.msg, "0", self.notification_schedule)
                    else:
                        raise ValueError
                except ValueError:
                    self.vk_send("Номер факультета указан не верно!\nИспользуйте целое число.\n"
                                 "Например: 16", "", self.read_keyboard("cancel.json"))
                    return

            elif self.setting == 72 and self.msg == "3":
                if self.message not in Group_1()[self.division]:
                    self.vk_send("Номер группы указан не верно!")
                    return

                self.db_connector, self.db_cursor = db()
                self.db_cursor.execute("SELECT `vk_id` FROM `user` WHERE `division` "
                                       "LIKE '%s' AND `user_group` LIKE '%s'" % (self.buffer, self.message))
                user_vk = self.db_cursor.fetchall()
                output_string = ""
                for user in user_vk:
                    output_string += "%s," % user

                user_response = self.vk.method("users.get", {
                    "user_ids": output_string})

                user_name = ""
                count = 1
                for current_user in user_response:
                    user_name += "%s. [id%s|%s %s]\n" % (count, current_user["id"], current_user["first_name"],
                                                         current_user["last_name"])
                    count += 1

                self.vk_send(user_name, "", self.keyboard_main)
                self.update_data_db(self.division, self.group, self.role, self.link_doc, "11",
                                    "main", self.msg, "0", self.notification_schedule)

            elif self.setting == 73 and self.msg == "3":
                current_id = self.message_id
                before_id = event.object.message["fwd_messages"][0]["id"]
                message_delete = ""
                message_delete_array = []
                scount = 0
                message_id_info = ""
                result_all = ""
                while before_id < current_id:
                    message_delete += "%s," % before_id
                    message_delete_array.append(before_id)
                    before_id += 1

                for i in message_delete_array:
                    message_id_info += "%s," % i
                    scount += 1
                    if scount == 99:
                        result = self.vk.method("messages.getById", {
                            "message_ids": message_id_info})
                        scount = 0
                        for user in result["items"]:
                            user_id_msg = user["from_id"]
                            if user_id_msg != -183787572:
                                continue
                            result_all += "%s," % user["id"]
                        try:
                            self.vk.method("messages.delete", {
                                "message_ids": result_all,
                                "delete_for_all": 1})
                            self.vk_send("Сообщение удалены!")
                            result_all = ""

                        except:
                            self.vk_send("Произошла ошибка! Сообщения не удалены!", "", self.keyboard_main)
                            self.update_data_db(self.division, self.group, self.role, self.link_doc, "11",
                                                "main", self.msg, self.buffer, self.notification_schedule)

                result = self.vk.method("messages.getById", {
                    "message_ids": message_id_info})
                for user in result["items"]:
                    user_id_msg = user["from_id"]
                    if user_id_msg != -183787572:
                        continue
                    result_all += "%s," % user["id"]

                try:
                    self.vk.method("messages.delete", {
                        "message_ids": result_all,
                        "delete_for_all": 1})

                    self.vk_send("Сообщения удалены!", "", self.keyboard_main)

                except:
                    self.vk_send("Произошла ошибка! Сообщения не удалены!", "", self.keyboard_main)
                self.update_data_db(self.division, self.group, self.role, self.link_doc, "11",
                                    "main", self.msg, self.buffer, self.notification_schedule)

        elif self.mode == "setting":
            if self.setting == 100:
                if self.message == "регистрация":
                    self.mode = "reg"
                    self.setting = 0
                    self.registration()

                elif self.message == "сообщить об ошибке":
                    self.vk_send("Опишите вашу проблему, и если необходимо - прикрепите документ к сообщению", "",
                                 self.read_keyboard("return.json"))
                    self.update_data_db(self.division, self.group, self.role, self.link_doc, "404",
                                        "setting", self.msg, self.buffer, self.notification_schedule)

                elif self.message == "уведомление об изменении в расписании":
                    if self.notification_schedule == "1":
                        mode = "0"
                        mode_message = "Вы отключили получение уведомлений"
                        keyboard = self.read_keyboard("setting_set_schedule.json")
                    else:
                        mode = "1"
                        mode_message = "Вы включили получение уведомлений"
                        keyboard = self.read_keyboard("setting.json")
                    self.vk_send(mode_message, "", keyboard)
                    self.update_data_db(self.division, self.group, self.role, self.link_doc, "100",
                                        "setting", self.msg, self.buffer, mode)

            elif self.setting == 404:
                self.vk_send("Ваше обращение передано", "", self.keyboard_main)
                self.vk.method("messages.send", {
                    "peer_id": admin_vk_id(),
                    "message": "@id%s(Пользователь) сообщил о проблеме:\n%s"
                               % (self.put_id, self._message),
                    "random_id": 0})
                self.update_data_db(self.division, self.group, self.role, self.link_doc, "11",
                                    "main", self.msg, "0", self.notification_schedule)



        elif self.mode == "schedule":
            if self.setting == 50:
                if self.buffer == "0":
                    buffer_group = self.group
                else:
                    buffer_group = self.buffer
                exist_facult = re.search("(\d+) (.*)", buffer_group)
                if exist_facult is None:
                    fac = self.division
                else:
                    buffer_group = exist_facult[2]
                    fac = exist_facult[1]

                if self.message == "текущая":
                    var = [None, buffer_group, "", ""]

                elif self.message == "<-":  # прошлая неделя
                    var = [None, buffer_group, "-", ""]

                elif self.message == "->":
                    var = [None, buffer_group, "+", ""]

                elif self.message == "другой преподаватель":
                    self.vk_send("Введите инициалы преподавателя. Допускаются любые сокращения, и даже в фамилии "
                                 "преподавателя", "",
                                 self.read_keyboard("return.json"))

                    self.update_data_db(self.division, self.group, self.role, self.link_doc, "55",
                                        "schedule", self.msg, self.buffer, self.notification_schedule)
                    return

                elif self.message == "другая дата":
                    keyboard = self.generator_date_keyboard()
                    if (self.check_keyboard_mode == "3"):
                        self.vk_send("Для получения расписания на определенный день -"
                                     " используйте клавиатуру или введите дату"
                                     " в формате: DD.MM.YYYY\n\nНапример: 03.11.2019\n\n"
                                     "Для работы с ботом без клавиатуры "
                                     "используйте следующие команды:\n⛔ Главное меню", "", keyboard.get_keyboard())
                    else:
                        self.vk_send("Для получения расписания на определенный день -"
                                     " используйте клавиатуру или введите дату"
                                     " в формате: DD.MM.YYYY\n\nНапример: 03.11.2019", "", keyboard.get_keyboard())
                    self.update_data_db(self.division, self.group, self.role, self.link_doc, "52",
                                        self.mode, self.msg, self.buffer, self.notification_schedule)
                    return

                elif self.message == "другая группа":
                    self.vk_send("%s\n\nВведите номер группы" % ParseNumberGroup(fac), "",
                                 self.read_keyboard("new_facult.json"))
                    self.update_data_db(fac, self.group, self.role, self.link_doc, "51",
                                        self.mode, self.msg, self.buffer, self.notification_schedule)
                    return

                else:
                    self.vk_send("Номер недели указан не верно. Используйте клавиатуру.", "",
                                 self.read_keyboard("schedule_teacher.json"))
                    return
                check_prepod = re.search("(\w+) (\w+)", buffer_group)
                # if len(buffer_group) > 6:
                if check_prepod is not None:
                    teacher_number = "lecturers/" + self.teacher_dict[buffer_group][0]
                    teacher_info = self.teacher_dict[buffer_group][1]
                    self.free_req = self.check_open_phantom()
                    image_push_of_day += 1
                    url, d_nac, d_kon = Push(self.vk, self.free_req, self.put_id).expense_count(var, teacher_number)
                    method = 'shedule_list'
                    teacher_id = re.sub("/", "-", self.teacher_dict[buffer_group][0])
                    self.attach = Push(self.vk, self.free_req, self.put_id).screen(url, method, teacher_id)
                    if self.attach == "Расписания на данную неделю нет!":
                        self.output_message = teacher_info + "\n\nРасписания на данную неделю нет!"

                    else:

                        self.output_message = teacher_info + "\n\nРасписание занятий с %s по %s" % (d_nac, d_kon)
                    close_driver[self.free_req] = False

                    self.vk_send(self.output_message, self.attach, self.keyboard_main)

                else:
                    self.free_req = self.check_open_phantom()
                    image_push_of_day += 1
                    output_message, attach = Push(self.vk, self.free_req, self.put_id).z_student(var, fac)
                    close_driver[self.free_req] = False
                    self.vk_send(output_message, attach, self.keyboard_main)

                self.update_data_db(self.division, self.group, self.role, self.link_doc, "11",
                                    "main", self.msg, "0", self.notification_schedule)

            elif self.setting == 51:
                if self.message == "другой факультет":
                    self.vk_send("%s\n\nВведите номер факультета" % facult, "", self.read_keyboard("return.json"))
                    self.update_data_db(self.division, self.group, self.role, self.link_doc, "58",
                                        self.mode, self.msg, self.buffer, self.notification_schedule)

                    return
                if self.buffer != "0":
                    division = self.buffer
                else:
                    division = self.division

                if self.message not in Group_1()[division]:
                    self.vk_send("Не существует %s группы!" % self.message)
                    return

                newstr = "%s %s" % (division, self.message)
                if (self.check_keyboard_mode == "3"):
                    self.vk_send("Выберите на какую неделю вы хотите получить расписание занятий\n\n"
                                 "Для работы с ботом без клавиатуры "
                                 "используйте следующие команды:\n✅ <-\n✅ Текущая\n"
                                 "✅ ->\n✅ Другая дата\n⛔ Главное меню", "",
                                 self.read_keyboard("schedule_user_no_change_group.json"))
                else:
                    self.vk_send("Выберите на какую неделю вы хотите получить "
                                 "расписание занятий", "", self.read_keyboard("schedule_user_no_change_group.json"))
                self.update_data_db(self.division, self.group, self.role, self.link_doc, "50",
                                    self.mode, self.msg, newstr, self.notification_schedule)

            elif self.setting == 58:
                try:
                    if self.message in get_id_by_number_group():
                        self.vk_send("%s\n\nВведите номер группы" %
                                     ParseNumberGroup(get_id_by_number_group()[self.message]), "",
                                     self.read_keyboard("return.json"))
                        self.update_data_db(self.division, self.group,
                                            self.role, self.link_doc, "51", self.mode, self.msg,
                                            get_id_by_number_group()[self.message], self.notification_schedule)
                    else:
                        raise ValueError
                except ValueError:
                    self.vk_send("Номер факультета указан не верно!\nИспользуйте целое число.\n"
                                 "Например: 16", "", self.read_keyboard("return.json"))
                    return
                return

            elif self.setting == 52:
                m_date = re.search("(\d){2}\.(\d){2}\.(\d){4}", self.message)
                date_short = re.search("(\d{2}).(\d{2}).\d{2}$", self.message)
                if date_short is not None:
                    self.message = "%s.%s.%s" % (date_short[1], date_short[2], datetime.now().year)

                elif m_date is None:
                    keyboard = self.generator_date_keyboard()
                    self.vk_send("Дата указана не верно!", "", keyboard.get_keyboard())
                    return

                if self.buffer == "0":
                    buffer_group = self.group
                else:
                    buffer_group = self.buffer

                exist_facult = re.search("(\d+) (.*)", buffer_group)
                if exist_facult is None:
                    fac = self.division
                else:
                    buffer_group = exist_facult[2]
                    fac = exist_facult[1]

                var = [None, buffer_group, "", self.message]

                check_prepod = re.search("(\w+) (\w+)", buffer_group)
                # if len(buffer_group) > 6:
                if check_prepod is not None:

                    teacher_number = "lecturers/" + self.teacher_dict[buffer_group][0]
                    teacher_info = self.teacher_dict[buffer_group][1]
                    self.free_req = self.check_open_phantom()
                    url, d_nac, d_kon = Push(self.vk, self.free_req, self.put_id).expense_count(var, teacher_number)
                    method = 'shedule_list'
                    teacher_id = re.sub("/", "-", self.teacher_dict[buffer_group][0])
                    image_push_of_day += 1
                    self.attach = Push(self.vk, self.free_req, self.put_id).screen(url, method, teacher_id)
                    if self.attach == "Расписания на данную неделю нет!":
                        self.output_message = teacher_info + "\n\nРасписания на данную неделю нет!"

                    else:
                        self.output_message = teacher_info + "\n\nРасписание занятий с %s по %s" % (d_nac, d_kon)

                    close_driver[self.free_req] = False
                    self.vk_send(self.output_message, self.attach, self.keyboard_main)

                else:
                    self.free_req = self.check_open_phantom()
                    image_push_of_day += 1

                    output_message, attach = Push(self.vk, self.free_req, self.put_id).z_student(var, fac)
                    close_driver[self.free_req] = False
                    self.vk_send(output_message, attach, self.keyboard_main)

                self.update_data_db(self.division, self.group, self.role, self.link_doc, "11",
                                    "main", self.msg, "0", self.notification_schedule)

            elif self.setting == 55:
                schedule_teacher = re.search(r'([A-Za-zА-ЯЁа-яё .]+)',
                                             self.message)

                if schedule_teacher is None:
                    self.vk_send("Не найдено ни одного преподавателя. Если преподаватель с данными инициалами "
                                 "действительно существует, то попробуйте сократить запрос. Обратите внимание, что "
                                 "фамилию тоже можно писать не всю")
                    # self.update_data_db(self.division, self.group, self.role, self.link_doc, "11",
                    #                          "main", self.msg, self.buffer, self.notification_schedule)
                    return

                if schedule_teacher is not None:
                    count = 0
                    teachers = ""
                    for i in self.teacher_dict:
                        xD = re.search("^%s.*" % schedule_teacher[1], i)
                        if xD is not None:
                            count += 1
                            teachers += "-> " + self.teacher_dict[xD[0]][2] + " (%s)" % \
                                        self.teacher_dict[xD[0]][3] + "\n"
                            teacher_name = xD[0]
                    if count == 0:
                        self.vk_send("Не найдено ни одного преподавателя. Если преподаватель с данными инициалами"
                                     " действительно существует, то попробуйте сократить запрос. Обратите внимание, что"
                                     " фамилию тоже можно писать не всю")

                    elif count != 1:
                        try:
                            self.vk_send("Слишком много преподавателей по вашему запросу. Сократите "
                                         "поиск до одного преподавателя\n\n" + teachers,
                                         "", self.read_keyboard("return.json"))
                        except:
                            self.vk_send("Попробуйте изменить свой запрос указав более "
                                         "полные инициалы преподавателя")

                    else:
                        self.vk_send("Выберите на какую неделю необходимо получить расписание", "",
                                     self.read_keyboard("schedule_teacher.json"))
                        self.update_data_db(self.division, self.group, self.role, self.link_doc, "50",
                                            "schedule", self.msg, teacher_name, self.notification_schedule)

                    return

        elif self.mode == "location":
            if self.setting == 60:
                """
                Получение номера корпуса
                """
                corp = ""
                if self.event.object["message"].get("geo") is not None:
                    corp = geo.object_to_object(self.event.object.message["geo"]["coordinates"]["latitude"],
                                                self.event.object.message["geo"]["coordinates"]["longitude"])

                elif self.message == "главное меню":
                    pass

                else:
                    corp = self.message
                if corp not in ("д", "к", "л", "м", "н", "с", "а", "э"):
                    self.vk_send("Номер корпуса указан не верно!", "", self.read_keyboard("location.json"))
                    return

                if self.check_keyboard_mode == "3":
                    self.vk_send("Выбран корпус %s. Укажите время и "
                                 "номер пары\n\n"
                                 "Для работы с ботом без клавиатуры "
                                 "используйте следующие команды:\n"
                                 "✅ 1. 08:00 - 09:30\n"
                                 "✅ 2. 09:40 - 11:10\n"
                                 "✅ 3. 11:20 - 12:50\n"
                                 "✅ 4. 13:20 - 14:50\n"
                                 "✅ 5. 15:00 - 16:30\n"
                                 "✅ 6. 16:40 - 18:10\n"
                                 "✅ 7. 18:20 - 19:50\n"
                                 "✅ 8. 20:00 - 21:30\n"
                                 "⛔ Главное меню", "", self.read_keyboard("time_pair.json"))
                else:
                    self.vk_send("Выбран корпус %s. Укажите время и "
                                 "номер пары" % corp.upper(), "", self.read_keyboard("time_pair.json"))
                self.update_data_db(self.division, self.group, self.role, self.link_doc, "61",
                                    "location", self.msg, corp, self.notification_schedule)
                return

            elif self.setting == 61:
                """
                Указываем номер пары
                """
                para = re.search("(\d)\. (\d){2}:(\d){2} - (\d){2}:(\d){2}", self.message)
                if para is None:
                    self.vk_send("Неверно указано время пары", "", self.read_keyboard("time_pair.json"))
                    return

                new_mes = "%s %s" % (self.buffer, para[1])
                keyboard = self.generator_date_keyboard()
                if (self.check_keyboard_mode == "3"):
                    self.vk_send("Для получения расписания на определенный день -"
                                 " используйте клавиатуру или введите дату"
                                 " в формате: DD.MM.YYYY\n\nНапример: 03.11.2019\n\n"
                                 "Для работы с ботом без клавиатуры "
                                 "используйте следующие команды:\n⛔ Главное меню", "", keyboard.get_keyboard())
                else:
                    self.vk_send("Для получения расписания на определенный день -"
                                 " используйте клавиатуру или введите дату"
                                 " в формате: DD.MM.YYYY\n\nНапример: 03.11.2019", "", keyboard.get_keyboard())
                self.update_data_db(self.division, self.group, self.role, self.link_doc, "62",
                                    "location", self.msg, new_mes, self.notification_schedule)

            elif self.setting == 62:
                m_date = re.search("(\d){2}\.(\d){2}\.(\d){4}", self.message)
                date_short = re.search("(\d{2}).(\d{2}).\d{2}$", self.message)
                if date_short is not None:
                    self.message = "%s.%s.%s" % (date_short[1], date_short[2], datetime.now().year)

                elif m_date is None:
                    keyboard = self.generator_date_keyboard()
                    self.vk_send("Дата указана не верно!", "", keyboard.get_keyboard())
                    return

                new_str = "%s %s" % (self.buffer, self.message)
                freerooms_audiences = re.search(r'^(\w) (\d) ((\d+[.|-]\d+[.|-]\d+)?)', new_str)
                self.free_req = self.check_open_phantom()
                image_push_of_day += 1
                output_message, attach = Push(self.vk, self.free_req, self.put_id).freerooms_audiences(
                    freerooms_audiences)
                close_driver[self.free_req] = False
                self.vk_send(output_message, attach, self.keyboard_main)
                self.update_data_db(self.division, self.group, self.role, self.link_doc, "11",
                                    "main", self.msg, "0", self.notification_schedule)

        elif self.mode == "note":
            if self.setting == 40:
                if self.message == "список":
                    self.db_connector, self.db_cursor = db()
                    attach = self.funct()
                    count = 0
                    for message, investments in attach.items():
                        count += 1
                        self.vk_send("{}. {}".format(count, message),
                                     investments)
                    self.vk_send("В данный момент у вас %s объявления ожидают проверки модерацией" % count, "",
                                 self.keyboard_main)
                    self.update_data_db(self.division, self.group, self.role, self.link_doc, "41",
                                        "main", self.msg, self.buffer, self.notification_schedule)
                elif self.message == "добавить":
                    self.vk_send("Введите новое объявление", "", self.read_keyboard("return.json"))

                    self.update_data_db(self.division, self.group, self.role, self.link_doc, "41",
                                        "note", self.msg, self.buffer, self.notification_schedule)

                elif self.message == "удалить":
                    self.vk_send("Введите номер для удаления")

                    self.update_data_db(self.division, self.group, self.role, self.link_doc, "42",
                                        "note", self.msg, self.buffer, self.notification_schedule)

                else:
                    return

            elif self.setting == 41:
                self.db_connector, self.db_cursor = db()
                self.db_cursor.execute(
                    "INSERT INTO `notes` (`id`, `vk_id`, `message_id`, `message_send`) "
                    "VALUES (NULL, '{}', '{}', '0');".format(self.put_id, self.message_id))
                self.vk_send("Объявление добавлено в очередь на модерацию", "", self.keyboard_main)
                self.update_data_db(self.division, self.group, self.role, self.link_doc, "11",
                                    "main", self.msg, self.buffer, self.notification_schedule)

            elif self.setting == 42:
                self.db_connector, self.db_cursor = db()
                attach = self.funct()
                count = 0
                for message, investments in attach.items():
                    count += 1
                    if count == int(self.message):
                        self.db_connector, self.db_cursor = db()
                        self.db_cursor.execute(
                            "UPDATE `notes` SET `message_send` = '2' WHERE `notes`.`message_id` "
                            "= %s;" % message)
                    self.vk_send("{}. {}".format(count, message),
                                 investments)
                self.vk_send("В данный момент у вас %s объявления ожидают проверки модерацией" % count)
                self.update_data_db(self.division, self.group, self.role, self.link_doc, "11",
                                    "main", self.msg, "0", self.notification_schedule)
                self.vk_send("Введите номер объявления для удаления\n%s")
            self.db_connector.commit()
            return

        elif self.mode == "post":
            if self.setting == 80:
                if self.message == "добавить":
                    self.vk_send("Введите заголовок для новой заметки", "", self.read_keyboard("return.json"))

                    self.update_data_db(self.division, self.group, self.role, self.link_doc, "81",
                                        "post", self.msg, self.buffer, self.notification_schedule)

                elif self.message == "удалить":

                    result, data_array_of_post = self.exist_list_doc()
                    if result == "У вас нет созданых записей!":
                        self.vk_send(result, "", self.read_keyboard("advertisement.json"))
                        self.update_data_db(self.division, self.group, self.role, self.link_doc, "80",
                                            "post", self.msg, "0", self.notification_schedule)
                        return

                    self.vk_send("%s\n\nВведите номер заметки для удаления" % result, "",
                                 self.read_keyboard("return.json"))
                    self.update_data_db(self.division, self.group, self.role, self.link_doc, "85",
                                        "post", self.msg, self.buffer, self.notification_schedule)


                elif self.message == "список":

                    result, data_array_of_post = self.exist_list_doc()
                    if result == "У вас нет созданых записей!":
                        self.vk_send(result, "", self.read_keyboard("advertisement.json"))
                        self.update_data_db(self.division, self.group, self.role, self.link_doc, "80",
                                            "post", self.msg, "0", self.notification_schedule)
                        return

                    self.vk_send("%s\n\nВведите номер заметки для просмотра ее содержимого" % result, "",
                                 self.read_keyboard("return.json"))
                    self.update_data_db(self.division, self.group, self.role, self.link_doc, "83",
                                        "post", self.msg, self.buffer, self.notification_schedule)
                return



            elif self.setting == 81:
                if len(self.message) > 50:
                    self.vk_send("Заголовок сообщения не может превышать 50 символов!")
                    return

                self.vk_send("Прикрепите сюда сообщение", "", self.read_keyboard("return.json"))
                self.update_data_db(self.division, self.group, self.role, self.link_doc, "82",
                                    "post", self.msg, self._message, self.notification_schedule)




            elif self.setting == 82:
                self.db_connector, self.db_cursor = db()
                self.db_cursor.execute(
                    "INSERT INTO `post` (`id`, `vk_id`, `message_id`, `title`) "
                    "VALUES (NULL, '%s', '%s', '%s');" % (self.put_id, self.message_id, self.buffer))
                self.db_connector.commit()

                self.vk_send("Заметка успешно добавлена", "", self.read_keyboard("advertisement.json"))
                self.update_data_db(self.division, self.group, self.role, self.link_doc, "80",
                                    "post", self.msg, "0", self.notification_schedule)
                return


            elif self.setting == 83:
                result, data_array_of_post = self.exist_list_doc()
                try:
                    number_of_message = int(self.message) - 1
                    self.vk.method("messages.send",
                                   {"user_ids": self.put_id,
                                    "keyboard": self.read_keyboard("advertisement.json"),
                                    "forward_messages": data_array_of_post[number_of_message][1],
                                    "random_id": 0})
                    self.update_data_db(self.division, self.group, self.role, self.link_doc, "80",
                                        "post", self.msg, self._message, self.notification_schedule)

                except ValueError:
                    self.vk_send("Необходимо указать номер заметки для просмотра ее содержимого")

                return


            elif self.setting == 85:
                # DELETE FROM `post` WHERE `post`.`id` = 9
                result, data_array_of_post = self.exist_list_doc()
                try:
                    number_of_message = int(self.message) - 1
                    self.db_connector, self.db_cursor = db()
                    self.db_cursor.execute("DELETE FROM `post` WHERE `post`.`message_id` = '%s'"
                                           % data_array_of_post[number_of_message][1])
                    self.db_connector.commit()
                    self.vk_send("Заметка удалена!", "", self.read_keyboard("advertisement.json"))
                    self.update_data_db(self.division, self.group, self.role, self.link_doc, "80",
                                        "post", self.msg, self._message, self.notification_schedule)


                except ValueError:
                    self.vk_send("Необходимо указать номер заметки для просмотра ее содержимого")

            return

        elif self.mode == "msg":
            self.db_connector, self.db_cursor = db()
            if self.setting == 30:
                if self.message == "отдельным группам":
                    self.vk_send("\n\n%s\n\nВведите номер группы. Если групп несколько, то разделите их "
                                 "знаком пробела" % ParseNumberGroup(self.division), "",
                                 self.read_keyboard("return.json"))
                    self.update_data_db(self.division, self.group, self.role, self.link_doc, "31",
                                        "msg", self.msg, self.buffer, self.notification_schedule)

                elif self.message == "всем группам факультета" or (self.message == "абсолютно всем факультетам"
                                                                   and self.msg == "3"):

                    self.vk_send("Введите текст для рассылки", "", self.read_keyboard("return.json"))
                    if self.message == "абсолютно всем факультетам" and self.msg == "3":
                        mode = "allAdmin"
                    else:
                        mode = "all"

                    self.update_data_db(self.division, self.group, self.role, self.link_doc, "32", "msg",
                                        self.msg, mode, self.notification_schedule)

                else:
                    self.vk_send("Неверно выбран режим")

            elif self.setting == 31:
                self.db_connector, self.db_cursor = db()
                number_group = self.message.split(" ")
                for num in number_group:
                    if num not in Group_1()[self.division]:
                        self.vk_send("Не существует %s группы!" % num)
                        return

                self.vk_send("Введите текст для рассылки", "", self.read_keyboard("return.json"))
                self.update_data_db(self.division, self.group, self.role, self.link_doc, "32",
                                    self.mode, self.msg, self.message, self.notification_schedule)

            elif self.setting == 32:
                self.db_connector, self.db_cursor = db()
                if self.msg == "3":
                    self.db_cursor.execute("SELECT `VK_ID` FROM `user`")
                    self.user_vk_resp = self.db_cursor.fetchall()
                    result = self.vk.method("users.get", {
                        "user_ids": self.put_id,
                        "fields": "first_name, last_name"
                    })
                    self.short_name = result[0]["first_name"] + " " + result[0]["last_name"]


                elif self.msg == "1" or self.msg == "2":
                    self.short_name = self.group

                if self.buffer == "all":

                    self.db_cursor.execute(
                        "SELECT `vk_id` FROM `user` WHERE `division` LIKE %s" % self.division)
                    self.user_vk_resp = self.db_cursor.fetchall()

                # elif self.buffer == "allAdmin":
                #     self.db_cursor.execute("SELECT `VK_ID` FROM `user`") # SELECT `vk_id` FROM `user`
                #     self.user_vk_resp = self.db_cursor.fetchall()
                #     result = self.vk.method("users.get", {
                #         "user_ids": self.put_id,
                #         "fields": "first_name, last_name"
                #     })
                #     self.short_name = result[0]["first_name"] + " " + result[0]["last_name"]

                else:
                    count = 0
                    all_group = self.buffer.split(" ")
                    ids = ""
                    for vk_id in all_group:
                        count += 1
                        if len(all_group) != count:
                            ids += "`user_group` LIKE '{}' OR ".format(vk_id)

                        elif len(all_group) == count:
                            ids += "`user_group` LIKE '{}'".format(vk_id)

                    if self.buffer == "allAdmin":
                        self.db_cursor.execute("SELECT `vk_id` FROM `user`")

                    else:
                        self.db_cursor.execute(
                            "SELECT `vk_id` FROM `user` WHERE (`division` LIKE %s) "
                            "AND %s" % (self.division, ids))
                    self.user_vk_resp = self.db_cursor.fetchall()

                if len(self.user_vk_resp) != 0:
                    result = self.func_send_msg(self.short_name)  # sОтпрака сообщений
                    if result != "USER_DOC":
                        self.vk_send("Сообщение разослано!\nОтправлено в личные сообщения: {}\n"
                                     "В беседы: 0".format(len(self.user_vk_resp)), "",
                                     self.keyboard_main)

                else:
                    self.vk_send("В данных группах нет участников!", "", self.keyboard_main)

                self.update_data_db(self.division, self.group, self.role, self.link_doc, "11",
                                    "main", self.msg, "0", self.notification_schedule)

            self.db_connector.commit()
            return

    def authorization(self):
        self.put_id = str(self.put_id)
        if mysql_dir.get(self.put_id) is None:  # Проверка vk_id на наличие в словаре
            self.db_connector, self.db_cursor = db()
            self.db_cursor.execute(
                "INSERT INTO `user` (`id`, `vk_id`, `division`, `user_group`, `role`, "
                "`link_doc`, `setting`, `mode`, `send_msg`, `buffer`, notification_schedule) VALUES (NULL, "
                "'%s', '0', '0', '0',"
                "'{\"Образовательный портал\": \"https://portal.edu.asu.ru/\", \"Английский\": \"https://vk.cc/9Krybk\"}',"
                " '0', 'reg', '0', '0', '1');" % self.put_id)
            mysql_dir[self.put_id] = ('0', '0', '0', '{\"Образовательный портал\": \"https://portal.edu.asu.ru/\",'
                                                     ' \"Английский\": \"https://vk.cc/9Krybk\"}',
                                      '0', 'reg', '0', '0', '1')
            self.db_connector.commit()
        user_vk = mysql_dir[self.put_id]
        return user_vk

    def func_send_msg(self, short_name):
        ids = ""
        count = 0
        for vk_id in self.user_vk_resp:
            ids += vk_id[0]
            count += 1
            if count != 99:
                ids += ", "

            elif count == 99:
                if self.buffer == "allAdmin":
                    self.send_mass_massages(ids, self.put_id, short_name)
                else:
                    self.send_rassilka(ids)
                # self.send_mass_massages(ids, self.put_id, short_name)
                count = 0
                ids = ""

        if self.buffer == "allAdmin":
            result = self.send_mass_massages(ids, self.put_id, short_name)

        else:
            result = self.send_rassilka(ids)
        return result

    def send_rassilka(self, ids):
        self.vk.method("messages.send",
                       {"user_ids": ids,

                        "forward_messages": self.message_id,
                        "random_id": 0})
        return "Ok"

    def send_mass_massages(self, ids, author, short_name):
        attach = PostDocument(self.vk, self.message_id).send_the_resulting_attach()
        if attach == "USER_DOC":
            self.vk_send("Невозможно отправить личные документы!\nИспользуйте для этого загрузчик.")
        else:
            for key, values in attach.items():
                self.vk.method("messages.send",
                               {"user_ids": ids,
                                "message": key,
                                "attachment": values,
                                "random_id": 0})
        return attach

    def push_keyboard_main(self, ids):
        self.vk.method("messages.send",
                       {"user_ids": ids,
                        "message": "Вы вернулись в главное меню\n\nДля работы с ботом без клавиатуры "
                                   "используйте следующие команды:\n✅ Расписание группы\n✅ Расписание преподавателя\n"
                                   "✅ Свободные аудитории\n✅ Заметки\n✅ Панель управления\n⛔ Настройки",
                        "keyboard": self.read_keyboard("main.json"),
                        "random_id": 0})
        return

    def registration(self):
        if self.setting is 0:
            self.vk_send("%s\n\nВведите номер факультета" % facult)
            mysql_dir[self.put_id] = ('0', '0', '0', '{\"Образовательный портал\": \"https://portal.edu.asu.ru/\", '
                                                     '\"Английский\":'
                                                     ' \"https://vk.cc/9Krybk\"}',
                                      '1', 'reg', '0', '0', '1')
            self.db_connector, self.db_cursor = db()
            self.db_cursor.execute("UPDATE `user` SET `setting` = '1', `mode` = 'reg', "
                                   "`role` = 'студент', `link_doc` "
                                   "= '{\"Образовательный портал\": \"https://portal.edu.asu.ru/\", "
                                   "\"Английский\": \"https://vk.cc/9Krybk\"}', "
                                   "`send_msg` = '0', "
                                   "`buffer` = '0' WHERE `user`.`vk_id` "
                                   "= %s;" % self.put_id)

        elif self.setting == 1:
            try:
                if self.message in get_id_by_number_group():
                    self.vk_send("Выберите роль\n\n✅ Студент\n✅ Преподаватель", "", self.read_keyboard("reg_role.json"))
                    self.update_data_db(get_id_by_number_group()[self.message], self.group,
                                        self.role, self.link_doc, "2", self.mode, self.msg, self.buffer,
                                        self.notification_schedule)

                else:
                    raise ValueError
            except ValueError:
                self.vk_send("Номер факультета указан не верно!\nИспользуйте целое число.\n"
                             "Например: 16", "", self.read_keyboard("cancel.json"))
                return

        elif self.setting == 2:
            if self.message == "студент":
                self.vk_send("%s\n\nВведите номер группы" % ParseNumberGroup(self.division), "",
                             self.read_keyboard("cancel.json"))

            elif self.message == "преподаватель":
                self.vk_send("Укажите Фамилию Имя Очество для дальнейшего получения расписания", "",
                             self.read_keyboard("cancel.json"))

            else:
                self.vk_send("Роль указана не верно!", "", self.read_keyboard("reg_role.json"))
                return
            self.update_data_db(self.division, self.group, self.message, self.link_doc, "3",
                                self.mode, self.msg, self.buffer, self.notification_schedule)

        elif self.setting == 3:
            if self.role == "преподаватель":
                if self.teacher_dict.get(self.message) is None:
                    self.vk_send("Преподаватель в системе не найден.\nПример: Фамилия Имя Отчество", "",
                                 self.read_keyboard("cancel.json"))
                    return
                reg_group = self.message

            elif self.message in Group_1()[self.division] and self.role == "студент":
                reg_group = self.message

            else:
                self.vk_send("Номер группы указан не верно! Попробуйте еще раз!", "",
                             self.read_keyboard("cancel.json"))
                return

            self.vk_send("Вы успешно зарегистрированы в системе. "
                         "Для дальнейшей работы используйте встроенную клавиатуру", "", self.keyboard_main)

            self.update_data_db(self.division, reg_group, self.role, self.link_doc, "11",
                                "main", self.msg, self.buffer, self.notification_schedule)
        self.db_connector.commit()
        return

    def new_message(self):
        self.c_begin = time.time()
        self.check_mode()
        # if self.output_message is not None:
        #     self.vk_send(self.output_message)
        #     return
        return

    def vk_send(self, message, attach="", keyboard=""):
        self.vk.method("messages.send",
                       {"peer_id": self.put_id, "message": message,
                        "attachment": attach, "keyboard": keyboard,
                        "random_id": 0, "dont_parse_links": 1})

    def read_keyboard(self, filename, directory="keyboards/"):
        return open(directory + filename, "r", encoding="UTF-8").read()

