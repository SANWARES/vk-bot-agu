from vk_api.bot_longpoll import VkBotEventType
import threading
from vk_api.bot_longpoll import VkBotLongPoll
import vk_api
import geo
from image_push import *
from datetime import timedelta, datetime
from BarnaulTime import Time
from schedule_group import *
from DataUsers import facult, ParseNumberGroup, facult_astats
from config import *
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from VK_API_Method import VkKeyboard_new, VkKeyboardButton_new, VkKeyboardColor_new
from utils import find_ref_group_by_name, find_prepod_by_fio

mysql_dir = {}
keyboardDir = {}
connectError = []
close_driver = {
    "1": False,
    "2": False,
    "3": False,
    "4": False
    # "5": False,
    # "6": False,
    # "7": False,
    # "8": False,
    # "9": False,
    # "10": False
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
                                            "intent": "default",
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
                                     user[10], \
                                     user[11], \
                                     user[12], \
                                     user[13]

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
        self.put_id = event.object.message["peer_id"]  # 2000000000
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
        self.last_schedule = self.user_vk[9]
        self.promo_newsletter = self.user_vk[10]
        self.confirmed_notification = self.user_vk[11]
        self.vk = vk
        self.free_req = None
        self.push_prepod = False

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
        while True:
            for c in close_driver.items():
                if c[1] == False:
                    close_driver[c[0]] = True
                    return c[0]
            time.sleep(1)

    def update_data_db(self, division, user_group, role, link_doc, setting, mode, send_msg, buffer,
                       notification_schedule, last_schedule, promo_newsletter, confirmed_notification):
        mysql_dir[self.put_id] = division, user_group, role, link_doc, setting, \
                                 mode, send_msg, buffer, notification_schedule, \
                                 last_schedule, promo_newsletter, confirmed_notification
        try:
            self.db_connector, self.db_cursor = db()
            self.db_cursor.execute(
                "UPDATE `user` SET `division` = '%s', `user_group` = '%s', `role` = '%s',"
                " `setting` = '%s', `mode` = '%s', `send_msg` = '%s',"
                " `buffer` = '%s', `notification_schedule` = '%s', `last_schedule` = '%s',"
                " `promo_newsletter` = '%s',`confirmed_notification` = '%s'"
                "WHERE `user`.`vk_id` = %s;" % (division, user_group, role, setting, mode, send_msg,
                                                buffer, notification_schedule, last_schedule, promo_newsletter,
                                                confirmed_notification, self.put_id))
            self.db_connector.commit()

        except Exception as e:
            self.vk.method("messages.send",
                           {"peer_id": admin_vk_id(),
                            "intent": "default", "message": "У @id%s(пользователя) "
                                                            "произошла ошибка: 2\n%s"
                                                            % (self.put_id, e.__str__()), "random_id": 0})
        return

    def result(self):
        try:
            self.c_begin = time.time()
            handling_message, handling_attachment, handling_keyboard = self.check_mode()
            if handling_message is None:
                return

            self.vk_send(handling_message, handling_attachment, handling_keyboard)
            print("[{}] Сообщение отправлено: {} | Затраченное время:{}".format(Time().brnTime(), self.put_id,
                                                                                round(time.time() - self.c_begin, 9)))

        except Exception as e:
            if self.free_req is not None:
                close_driver[self.free_req] = False
            self.vk_send("Произошла ошибка. Вы вернулись в главное меню.", "",
                         self.keyboard_main)
            self.mode = "main"
            self.setting = 11
            self.buffer = "0"
            self.vk.method("messages.send",
                           {"peer_id": admin_vk_id(), "message": "У @id%s(пользователя) "
                                                                 "произошла ошибка: 1\n%s"
                                                                 % (self.put_id, e.__str__()), "random_id": 0})
        self.update_data_db(self.division, self.group, self.role, self.link_doc, self.setting,
                            self.mode, self.msg, self.buffer, self.notification_schedule, self.last_schedule,
                            self.promo_newsletter,
                            self.confirmed_notification)
        return

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

    def sub_add(self, intent_type, label_name="Подписаться", subscribe_id="0"):
        """
        promo_newsletter для рекламной рассылки  Используется раз в 7 дней
        confirmed_notification - свободные рассылки по тематике
        """

        keyboard = VkKeyboard_new(one_time=False)
        keyboard.subscribe_push_message(self.put_id, intent_type, label_name, subscribe_id)

        return keyboard.get_keyboard()

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
        handling_message = ""
        handling_attachment = ""
        handling_keyboard = self.keyboard_main
        match = re.search(r'(\d+\w)([-+]?)((\s\d+[.|-]\d+[.|-]\d+)?)$', self.message)
        if (self.message == "main" or self.message == "главное меню") and self.mode != "reg":
            if self.check_keyboard_mode == "3":
                handling_message = "Вы вернулись в главное меню\n\nДля работы с ботом без клавиатуры " \
                                   "используйте следующие команды:\n✅ Расписание группы\n" \
                                   "✅ Расписание преподавателя\n" \
                                   "✅ Свободные аудитории\n✅ Заметки\n✅ Панель управления\n⛔ Настройки"

            else:
                handling_message = "Вы вернулись в главное меню"
            self.setting = 11
            self.mode = "main"
            self.buffer = "0"

        elif self.message == "подписаться" and self.mode != "reg":
            self.promo_newsletter = "1"
            handling_message = "Вы вернулись в главное меню"
            handling_keyboard = self.keyboard_main
            self.mode = "main"
            self.setting = 11

        elif self.promo_newsletter == "0" and self.mode != "reg":
            handling_message = "Подпишитесь на рассылку, если вы хотите получать " \
                               "информацию о добавлении, удалении, изменении расписания занятий.\n" \
                               "Отписаться от рассылки можно в любой момент в настройках."
            keyboard = VkKeyboard_new(one_time=False)
            keyboard.subscribe_push_message(self.put_id, "promo_newsletter", "Подписаться", "0")
            handling_keyboard = keyboard.get_keyboard()



        elif self.message == "stats":
            handling_keyboard = ""
            handling_message = "Role: {}\nГруппа: {}\nDivision: {}\n" \
                               "Mode: {}\nSetting: {}\nsend_msg: {}\nbuffer: {}\n" \
                               "notification_schedule: {}\nlast_schedule: {}" \
                               "\npromo_newsletter: {}\nconfirmed_notification: {}" \
                               "".format(self.role,
                                         self.group,
                                         self.division,
                                         self.mode,
                                         self.setting,
                                         self.msg,
                                         self.buffer,
                                         self.notification_schedule,
                                         self.last_schedule, self.promo_newsletter,
                                         self.confirmed_notification)



        elif self.message == "adm" and self.put_id == admin_vk_id():
            handling_message = "Админка выдана"
            self.role = "студент"
            self.msg = "3"
            handling_keyboard = self.read_keyboard("main_admin.json")
            self.update_data_db(self.division, self.group, self.role, self.link_doc, self.setting,
                                self.mode, self.msg, self.buffer, self.notification_schedule, self.last_schedule,
                                self.promo_newsletter,
                                self.confirmed_notification)

        elif self.message == "test":
            result = self.vk.method("users.get", {
                "user_ids": "yeah",
                "fields": "id, first_name, last_name"
            })
            short_name = "id: %s | Name: %s %s" % (result[0]["id"], result[0]["first_name"], result[0]["last_name"])



        elif self.message == "image stats" and self.put_id == admin_vk_id():
            global image_push_of_day
            handling_message = image_push_of_day
            self.vk_send(image_push_of_day)

        elif self.message == "driver" and self.put_id == admin_vk_id():
            handling_message = str(close_driver)

        elif self.message == "reg" or self.mode == "reg":
            if self.message == "reg" or self.message == "назад":
                self.mode = "reg"
                self.setting = 0
            handling_message, handling_attachment, handling_keyboard = self.registration()

        elif self.message == "следующая" or self.message == "предыдущая":
            if self.message == "следующая":
                mode = 1
            else:
                mode = 0
            self.free_req = self.check_open_phantom()
            get_group = re.search(r'students/(.*)/(.*)/', self.last_schedule)  # students/25/2129439635/ 21.02.2021
            if get_group is not None:
                podr = get_group[1]
                ref_group = get_group[2] + "/"
                share_group = Group_1_back()[podr][ref_group]
                mtype = 1
                teacher_info = ""
            else:  # Вроде как получение расписания преподавателя
                share_group = self.group
                mtype = 2
                if self.buffer != "0":
                    teacher_info = self.teacher_dict[self.buffer][1]
                elif self.role == "студент":
                    teacher_info = self.last_schedule
                else:
                    teacher_info = self.teacher_dict[self.group][1]
            self.last_schedule = Push(self.vk, self.free_req, self.put_id, share_group).change_week(self.last_schedule,
                                                                                                    mode, mtype,
                                                                                                    teacher_info)
            close_driver[self.free_req] = False
            handling_message = "Вы вернулись в главное меню"
            handling_keyboard = self.keyboard_main
            self.mode = "main"
            self.setting = 11

        elif match is not None and match[1] in Group_1_back()[
            self.division].values() and self.mode != "msg" and self.mode != "admin" and self.setting != 51:
            self.free_req = self.check_open_phantom()

            reg_group = find_ref_group_by_name(self.division, match[1])
            new_array = [None, reg_group, match[2], match[3]]

            self.last_schedule = Push(self.vk, self.free_req, self.put_id, reg_group).z_student(new_array,
                                                                                                self.division)
            handling_message = "Вы вернулись в главное меню"
            handling_keyboard = self.keyboard_main
            close_driver[self.free_req] = False
            self.setting = 11
            self.buffer = "0"
            self.mode = "main"
            close_driver[self.free_req] = False

        elif self.mode == "main":
            go_keyboard = re.search("kb https://vk.com/(.*)", self.message)

            go_reg = re.search("go reg https://vk.com/(.*)", self.message)  # id first_name last_name
            so_reg = re.search("so reg https://vk.com/(\d+)", self.message)
            freerooms_audiences = re.search(r'^(\w) (\d)((\s\d+[.|-]\d+[.|-]\d+)?)', self.message)

            if go_keyboard is not None and self.msg == "3":
                result = self.vk.method("users.get", {
                    "user_ids": go_keyboard[1],
                    "fields": "id, first_name, last_name",
                    "name_case": "acc"
                })
                # short_name = "idx: %s | Name: %s %s" % (result[0]["id"], result[0]["first_name"], result[0]["last_name"])
                # print(short_name)

                if str(result[0]["id"]) in mysql_dir:
                    self.vk_send("Вы вернули @id%s(%s %s) в главное меню!" % (
                        result[0]["id"], result[0]["first_name"], result[0]["last_name"]))
                    self.put_id = str(result[0]["id"])

                    if self.check_keyboard_mode == "3":
                        handling_message = "Вы вернулись в главное меню\n\nДля работы с ботом без клавиатуры " \
                                           "используйте следующие команды:\n✅ Расписание группы\n✅ Расписание " \
                                           "преподавателя\n✅ Свободные аудитории\n✅ Заметки\n✅ Панель управления\n⛔ " \
                                           "Настройки"
                    else:
                        handling_message = "Вы вернулись в главное меню"

                    self.division = mysql_dir[self.put_id][0]
                    self.group = mysql_dir[self.put_id][1]
                    self.role = mysql_dir[self.put_id][2]
                    self.link_doc = mysql_dir[self.put_id][3]
                    self.setting = 11
                    self.mode = "main"
                    self.msg = mysql_dir[self.put_id][6]
                    self.buffer = "0"
                    self.notification_schedule = mysql_dir[self.put_id][8]
                    self.last_schedule = mysql_dir[self.put_id][9]
                    self.promo_newsletter = mysql_dir[self.put_id][10]
                    self.confirmed_notification = mysql_dir[self.put_id][11]

            elif go_reg is not None and self.msg == "3":
                result = self.vk.method("users.get", {
                    "user_ids": go_reg[1],
                    "fields": "id, first_name, last_name",
                    "name_case": "acc"
                })
                if str(result[0]["id"]) in mysql_dir:
                    self.vk_send("Вы вернули @id%s(%s %s) в меню регистрации!" % (
                        result[0]["id"], result[0]["first_name"], result[0]["last_name"]))
                    handling_message = "%s\n\nВведите номер факультета" % facult

                    self.put_id = str(result[0]["id"])

                    self.division = mysql_dir[self.put_id][0]
                    self.group = mysql_dir[self.put_id][1]
                    self.role = mysql_dir[self.put_id][2]
                    self.link_doc = mysql_dir[self.put_id][3]
                    self.setting = 1
                    self.mode = "reg"


            elif so_reg is not None and self.msg == "3":
                handling_message = "Регистрация!"
                self.put_id = str(so_reg[1])
                self.db_connector, self.db_cursor = db()
                self.mode = "reg"
                self.setting = 0
                self.authorization()

            elif freerooms_audiences is not None and freerooms_audiences[2] in self.schedule_pairs and \
                    freerooms_audiences[1] in self.Housings:
                self.free_req = self.check_open_phantom()
                handling_message, handling_attachment = Push(self.vk, self.free_req, self.put_id,
                                                             self.group).freerooms_audiences(
                    freerooms_audiences)
                close_driver[self.free_req] = False

            elif self.message == "настройки":
                if self.confirmed_notification == "1":
                    push_keyboard = self.read_keyboard("setting.json")
                else:
                    keyboard = VkKeyboard_new(one_time=False)
                    keyboard.subscribe_push_message(self.put_id, "confirmed_notification",
                                                    "Подписаться на изменения в расписании", "0")
                    keyboard.add_line()
                    keyboard.add_button("Регистрация", VkKeyboardColor_new.PRIMARY)
                    keyboard.add_line()
                    keyboard.add_button("Сообщить об ошибке", VkKeyboardColor_new.PRIMARY)
                    keyboard.add_line()
                    keyboard.add_button("Главное меню", VkKeyboardColor_new.NEGATIVE)

                    push_keyboard = keyboard.get_keyboard()

                if self.check_keyboard_mode == "3":
                    handling_message = "Вы перешли в меню настроек\n\nДля работы с ботом без клавиатуры " \
                                       "используйте следующие команды:\n" \
                                       "✅ Уведомление об изменении в расписании\n✅ Регистрация\n" \
                                       "✅ Сообщить об ошибке\n" \
                                       "⛔ Главное меню"
                    handling_keyboard = push_keyboard
                else:
                    handling_message = "Вы перешли в меню настроек"
                    handling_keyboard = push_keyboard

                self.setting = 100
                self.mode = "setting"



            elif self.message == "расписание группы":
                handling_keyboard = self.read_keyboard("schedule_user.json")
                if self.check_keyboard_mode == "3":
                    handling_message = "Вы перешли в меню с получением расписания\n\nДля работы с ботом без клавиатуры " \
                                       "используйте следующие команды:\n✅ <-\n✅ Текущая\n" \
                                       "✅ ->\n✅ Другая группа\n✅ Другая дата\n⛔ Главное меню"
                else:
                    handling_message = "Вы перешли в меню с получением расписания"
                self.setting = 50
                self.mode = "schedule"
                self.buffer = "0"

            elif self.message == "панель управления" and (self.msg == "3" or self.msg == "2"):
                if self.msg == "3":
                    handling_message = "Вы перешли в админ панель"
                    handling_keyboard = self.read_keyboard("admin.json")
                elif self.msg == "2":
                    handling_message = "Вы перешли в панель управления ботом"
                    handling_keyboard = self.read_keyboard("Editor.json")
                self.setting = 70
                self.mode = "admin"

            elif self.message == "расписание преподавателя":
                if self.role == "студент":
                    handling_keyboard = self.read_keyboard("return.json")
                    self.setting = "55"
                    self.mode = "schedule"
                    if self.check_keyboard_mode == "3":
                        handling_message = "Введите инициалы преподавателя. Допускаются любые сокращения, и " \
                                           "даже в фамилии преподавателя\n\n" \
                                           "Для работы с ботом без клавиатуры " \
                                           "используйте следующие команды:\n⛔ Главное меню"
                    else:
                        handling_message = "Введите инициалы преподавателя. Допускаются любые сокращения, " \
                                           "и даже в фамилии преподавателя"

                elif self.role == "преподаватель":
                    handling_message = "Выберите дальнейшее действие"
                    handling_keyboard = self.read_keyboard("mode_teacher_schedule.json")
                    self.setting = "50"
                    self.mode = "schedule"

            elif self.message == "заметки":
                handling_keyboard = self.read_keyboard("advertisement.json")
                if self.check_keyboard_mode == "3":
                    handling_message = "Вы перешли в меню заметок. Здесь вы можете добавлять свои" \
                                       " заметки, и указывать к ним значения\n\n" \
                                       "Для работы с ботом без клавиатуры " \
                                       "используйте следующие команды:\n✅ Список\n✅ Добавить\n✅ Удалить\n⛔ Главное меню"
                else:
                    handling_message = "Вы перешли в меню заметки. Здесь вы можете добавлять свои" \
                                       " заметки, и указывать к ним значения"

                self.setting = 80
                self.mode = "post"

            elif self.message == "свободные аудитории":
                if self.check_keyboard_mode == "3":
                    handling_message = "Выберите корпус из списка предложенных, или отправьте свое " \
                                       "местоположение нажав на соответствующую кнопку, и " \
                                       "мы найдем ближайший корпус к вам\n\n" \
                                       "Для работы с ботом без клавиатуры " \
                                       "используйте следующие команды:\n✅ Д\n✅ К\n✅ Л\n✅ М\n✅ Н\n✅ С\n✅ А\n✅ Э\n" \
                                       "⛔ Главное меню"
                else:
                    handling_message = "Выберите корпус из списка предложенных, или отправьте свое " \
                                       "местоположение нажав на соответствующую кнопку, и " \
                                       "мы найдем ближайший корпус к вам"
                    handling_keyboard = self.read_keyboard("location.json")

                self.setting = 60
                self.mode = "location"

            elif self.message == "расписание аудиторий":
                if self.check_keyboard_mode == "3":
                    handling_message = "Выберите корпус из списка предложенных, или отправьте свое " \
                                       "местоположение нажав на соответствующую кнопку, и " \
                                       "мы найдем ближайший корпус к вам\n\n" \
                                       "Для работы с ботом без клавиатуры " \
                                       "используйте следующие команды:\n✅ Д\n✅ К\n✅ Л\n✅ М\n✅ Н\n✅ С\n✅ А\n✅ Э\n" \
                                       "⛔ Главное меню"
                else:
                    handling_message = "Выберите корпус из списка предложенных, или отправьте свое " \
                                       "местоположение нажав на соответствующую кнопку, и " \
                                       "мы найдем ближайший корпус к вам"
                    handling_keyboard = self.read_keyboard("location.json")

                self.setting = 200
                self.mode = "location_info"

            elif self.message == "расписание групп":
                handling_message = "%s\n\nВведите номер группы" % ParseNumberGroup(self.division)
                handling_keyboard = self.read_keyboard("new_facult.json")
                self.setting = 51
                self.mode = "schedule"

            elif self.message == "объявления":
                handling_message = "Выберите дальнейшее действие!"
                handling_keyboard = self.read_keyboard("advertisement.json")
                self.setting = 40
                self.mode = "note"

            elif self.message == "stats":
                handling_message = "Роль в системе: {}\nГруппа: {}\nСпециальность: {}\n" \
                                   "Мод: {}\nSetting: {}\nОтправка сообщений: {}".format(self.role,
                                                                                         self.group,
                                                                                         self.division,
                                                                                         self.mode,
                                                                                         self.setting,
                                                                                         self.msg)

            elif self.message == "edit":
                self.db_connector, self.db_cursor = db()
                self.db_cursor.execute(
                    "SELECT `vk_id`, `message_id` FROM `notes` WHERE `message_send` LIKE '0'")
                send = ""
                message_id = self.db_cursor.fetchall()
                if len(message_id) == 0:
                    handling_message = "Нет объявлений для редакции"
                else:
                    for note in message_id:
                        send += "{}, ".format(note[1])
                    attach = PostDocument(self.vk, send).send_the_resulting_attach()
                    count = 0
                    for message, investments in attach.items():
                        count += 1
                        self.vk_send("{}. {}".format(count, message),
                                     investments)
                    handling_message = "В данный момент у вас %s объявления ожидают проверки модерацией" % count



        elif self.mode == "setting":
            if self.setting == 100:
                if self.message == "регистрация":
                    self.mode = "reg"
                    self.setting = 0
                    handling_message, handling_attachment, handling_keyboard = self.registration()

                elif self.message == "сообщить об ошибке":
                    handling_message = "Опишите вашу проблему, и если необходимо - прикрепите документ к сообщению"
                    handling_keyboard = self.read_keyboard("return.json")
                    self.setting = 404
                    self.mode = "setting"

                elif self.message == "отписаться от изменении в расписании" \
                        or self.message == "подписаться на изменения в расписании":
                    if self.confirmed_notification == "1":
                        mode = "0"
                        handling_message = "Больше вам не будут приходить уведомления об изменении в расписании занятий"

                        keyboard = VkKeyboard_new(one_time=False)
                        keyboard.subscribe_push_message(self.put_id, "confirmed_notification",
                                                        "Подписаться на изменения в расписании", "0")
                        keyboard.add_line()
                        keyboard.add_button("Регистрация", VkKeyboardColor_new.PRIMARY)
                        keyboard.add_line()
                        keyboard.add_button("Сообщить об ошибке", VkKeyboardColor_new.PRIMARY)
                        keyboard.add_line()
                        keyboard.add_button("Главное меню", VkKeyboardColor_new.NEGATIVE)

                        handling_keyboard = keyboard.get_keyboard()

                        # handling_keyboard = self.read_keyboard("setting_set_schedule.json")
                    else:
                        mode = "1"
                        handling_message = "Вы подписались на получение уведомлений об изменении в расписании"
                        handling_keyboard = self.read_keyboard("setting.json")
                    self.setting = 100
                    self.mode = "setting"
                    self.confirmed_notification = mode

            elif self.setting == 404:
                handling_message = "Ваше обращение передано"
                self.vk.method("messages.send", {
                    "peer_id": admin_vk_id(),
                    "intent": "default",
                    "message": "@id%s(Пользователь) сообщил о проблеме:\n%s"
                               % (self.put_id, self._message),
                    "random_id": 0})
                self.setting = 11
                self.mode = "main"
                self.buffer = "0"

        elif self.mode == "location_info":

            if self.setting == 200:
                corp = ""
                if self.event.object["message"].get("geo") is not None:
                    corp = geo.object_to_object(self.event.object.message["geo"]["coordinates"]["latitude"],
                                                self.event.object.message["geo"]["coordinates"]["longitude"])

                elif self.message == "главное меню":
                    pass

                else:
                    corp = self.message
                if corp not in ("д", "к", "л", "м", "н", "с", "а"):
                    handling_message = "Номер корпуса указан не верно!"
                    handling_keyboard = self.read_keyboard("location.json")
                    return handling_message, handling_attachment, handling_keyboard

                handling_message = "Выбран корпус: %s.\n\n%s\n\nВведите номер аудитории" % (
                    corp.upper(), ParseNumberGroup(Housings()[corp], "audiences_info"))
                self.setting = 201
                self.mode = "location_info"
                self.buffer = Housings()[corp]
                handling_keyboard = self.read_keyboard("return.json")




            elif self.setting == 201:
                audiences_info = self.buffer

                if self.message not in Housing_room()[audiences_info]:
                    handling_keyboard = self.read_keyboard("return.json")
                    handling_message = "%s\n\nВведите номер аудитории" % ParseNumberGroup(audiences_info,
                                                                                          "audiences_info")

                else:
                    if self.check_keyboard_mode == "3":
                        handling_message = "Для получения расписания на определенный день -" \
                                           " используйте клавиатуру или введите дату" \
                                           " в формате: DD.MM.YYYY\n\nНапример: 03.11.2019\n\n" \
                                           "Для работы с ботом без клавиатуры " \
                                           "используйте следующие команды:\n⛔ Главное меню"
                    else:
                        handling_message = "Для получения расписания на определенный день - " \
                                           "используйте клавиатуру или введите дату " \
                                           "в формате: DD.MM.YYYY\n\nНапример: 03.11.2019"
                    self.setting = 202
                    housing_room = Housing_room()
                    self.buffer = "%s/%s" % (audiences_info, housing_room[audiences_info][self.message])
                    keyboard = self.generator_date_keyboard()
                    handling_keyboard = keyboard.get_keyboard()



            elif self.setting == 202:

                m_date = re.search("(\d){2}\.(\d){2}\.(\d){4}", self.message)
                date_short = re.search("(\d{2}).(\d{2}).\d{2}$", self.message)
                if date_short is not None:
                    self.message = "%s.%s.%s" % (date_short[1], date_short[2], datetime.now().year)

                elif m_date is None:
                    keyboard = self.generator_date_keyboard()
                    handling_message = "Дата указана не верно!"
                    handling_keyboard = keyboard.get_keyboard()
                    return handling_message, handling_attachment, handling_keyboard

                self.free_req = self.check_open_phantom()
                room = self.buffer
                handling_message, handling_attachment = Push(self.vk, self.free_req, self.put_id,
                                                             self.group).audiences_info(
                    room, self.message)
                close_driver[self.free_req] = False
                self.setting = 11
                self.mode = "main"
                self.buffer = "0"


        elif self.mode == "schedule":

            if self.setting == 50:
                var = None
                if self.buffer == "0":
                    buffer_group = self.group
                else:
                    buffer_group = self.buffer
                exist_facult = re.search("(\d+) (.*)", buffer_group)
                check_prepod = re.search("^([A-Za-zА-ЯЁа-яё .]+) ([A-Za-zА-ЯЁа-яё .]+)", buffer_group)
                if exist_facult is None:
                    fac = self.division
                else:
                    buffer_group = exist_facult[2]
                    fac = exist_facult[1]
                if self.message not in ["<-", "текущая", "->", "другая группа", "другая дата", "другой преподаватель"]:
                    handling_message = "Номер недели указан не верно"

                    if self.role == "преподаватель":
                        handling_keyboard = self.read_keyboard("mode_teacher_schedule.json")
                    else:
                        handling_keyboard = self.read_keyboard("schedule_user.json")

                elif self.message == "текущая":
                    var = [None, buffer_group, "", ""]

                elif self.message == "<-":  # прошлая неделя
                    var = [None, buffer_group, "-", ""]

                elif self.message == "->":
                    var = [None, buffer_group, "+", ""]


                elif self.message == "другой преподаватель":
                    handling_message = "Введите инициалы преподавателя. Допускаются любые сокращения, и даже в фамилии " \
                                       "преподавателя"
                    handling_keyboard = self.read_keyboard("return.json")
                    self.setting = 55
                    self.mode = "schedule"
                    return handling_message, handling_attachment, handling_keyboard

                elif self.message == "другая дата":
                    keyboard = self.generator_date_keyboard()
                    handling_keyboard = keyboard.get_keyboard()

                    if self.check_keyboard_mode == "3":
                        handling_message = "Для получения расписания на определенный день -" \
                                           " используйте клавиатуру или введите дату" \
                                           " в формате: DD.MM.YYYY\n\nНапример: 03.11.2019\n\n" \
                                           "Для работы с ботом без клавиатуры " \
                                           "используйте следующие команды:\n⛔ Главное меню"
                    else:
                        handling_message = "Для получения расписания на определенный день - " \
                                           "используйте клавиатуру или введите дату " \
                                           "в формате: DD.MM.YYYY\n\nНапример: 03.11.2019"
                    self.setting = 52
                    var = None
                    return handling_message, handling_attachment, handling_keyboard

                elif self.message == "другая группа":
                    handling_message = "%s\n\nВведите номер группы" % ParseNumberGroup(fac)
                    handling_keyboard = self.read_keyboard("new_facult.json")
                    var = None
                    self.setting = 51

                if check_prepod is not None:
                    if self.message in ["текущая", "->", "<-", "другая дата"]:
                        self.push_prepod = True
                        teacher_number = "lecturers/" + self.teacher_dict[buffer_group][0]
                        teacher_info = self.teacher_dict[buffer_group][1]
                        self.free_req = self.check_open_phantom()

                        self.last_schedule = Push(self.vk, self.free_req, self.put_id, self.group).z_student(var,
                                                                                                             teacher_number,
                                                                                                             2,
                                                                                                             teacher_info)

                        handling_message = "Вы вернулись в главное меню"
                        handling_keyboard = self.keyboard_main
                        close_driver[self.free_req] = False
                        self.setting = 11
                        self.mode = "main"
                        self.buffer = "0"

                elif var is not None:
                    self.free_req = self.check_open_phantom()
                    self.last_schedule = Push(self.vk, self.free_req, self.put_id, self.group).z_student(var, fac)
                    handling_message = "Вы вернулись в главное меню"
                    handling_keyboard = self.keyboard_main
                    close_driver[self.free_req] = False
                    self.setting = 11
                    self.buffer = "0"
                    self.mode = "main"



            elif self.setting == 51:
                if self.message == "другой факультет":
                    handling_message = "%s\n\nВведите номер факультета" % facult
                    handling_keyboard = self.read_keyboard("return.json")
                    self.setting = 58
                    return handling_message, handling_attachment, handling_keyboard

                if self.buffer != "0" and self.role == "студент":
                    division = self.buffer
                else:
                    division = self.division

                if self.message not in Group_1_back()[division].values():
                    handling_message = "Не существует %s группы!" % self.message
                    handling_keyboard = self.read_keyboard("new_facult.json")
                    return handling_message, handling_attachment, handling_keyboard

                reg_group = find_ref_group_by_name(division, self.message)

                newstr = "%s %s" % (division, reg_group)
                if self.check_keyboard_mode == "3":
                    handling_message = "Выберите на какую неделю вы хотите получить расписание занятий\n\n" \
                                       "Для работы с ботом без клавиатуры " \
                                       "используйте следующие команды:\n✅ <-\n✅ Текущая\n" \
                                       "✅ ->\n✅ Другая дата\n⛔ Главное меню"
                else:
                    handling_message = "Выберите на какую неделю вы хотите получить расписание занятий"
                handling_keyboard = self.read_keyboard("schedule_user_no_change_group.json")
                self.setting = 50
                self.buffer = newstr

            elif self.setting == 58:
                handling_keyboard = self.read_keyboard("new_facult.json")
                try:
                    if self.message in get_id_by_number_group():
                        handling_message = "%s\n\nВведите номер " \
                                           "группы" % ParseNumberGroup(get_id_by_number_group()[self.message])
                        self.setting = 51
                        self.buffer = get_id_by_number_group()[self.message]
                    else:
                        raise ValueError
                except ValueError:
                    handling_message = "Номер факультета указан не верно!\nИспользуйте целое число.\nНапример: 16"

            elif self.setting == 52:
                m_date = re.search("(\d){2}\.(\d){2}\.(\d){4}", self.message)
                date_short = re.search("(\d{2}).(\d{2}).\d{2}$", self.message)
                if date_short is not None:
                    self.message = "%s.%s.%s" % (date_short[1], date_short[2], datetime.now().year)

                elif m_date is None:
                    keyboard = self.generator_date_keyboard()
                    handling_message = "Дата указана не верно!"
                    handling_keyboard = keyboard.get_keyboard()
                    return handling_message, handling_attachment, handling_keyboard

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
                if check_prepod is not None:
                    self.push_prepod = True
                    teacher_number = "lecturers/" + self.teacher_dict[buffer_group][0]
                    teacher_info = self.teacher_dict[buffer_group][1]
                    self.buffer = buffer_group
                    self.free_req = self.check_open_phantom()

                    self.last_schedule = Push(self.vk, self.free_req, self.put_id, self.group).z_student(var,
                                                                                                         teacher_number,
                                                                                                         2,
                                                                                                         teacher_info)
                    handling_message = "Вы вернулись в главное меню"
                    handling_keyboard = self.keyboard_main
                    close_driver[self.free_req] = False
                    self.setting = 11
                    self.mode = "main"


                else:
                    self.free_req = self.check_open_phantom()

                    self.last_schedule = Push(self.vk, self.free_req, self.put_id, self.group).z_student(var, fac)
                    handling_message = "Вы вернулись в главное меню"
                    handling_keyboard = self.keyboard_main
                    close_driver[self.free_req] = False
                    self.buffer = "0"

                self.setting = 11

                self.mode = "main"

            elif self.setting == 55:

                message, teacher_name = find_prepod_by_fio(self.message)
                if message == "500":
                    handling_message = "Выберите на какую неделю необходимо получить расписание"
                    handling_keyboard = self.read_keyboard("schedule_teacher.json")
                    self.setting = 50
                    self.mode = "schedule"
                    self.buffer = teacher_name

                else:
                    handling_message = message
                    handling_keyboard = self.read_keyboard("return.json")

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
                if corp not in ("д", "к", "л", "м", "н", "с", "а"):
                    handling_message = "Номер корпуса указан не верно!"
                    handling_keyboard = self.read_keyboard("location.json")

                elif self.check_keyboard_mode == "3":
                    handling_message = "Выбран корпус %s. Укажите время и " \
                                       "номер пары\n\n" \
                                       "Для работы с ботом без клавиатуры " \
                                       "используйте следующие команды:\n" \
                                       "✅ 1. 08:00 - 09:30\n" \
                                       "✅ 2. 09:40 - 11:10\n" \
                                       "✅ 3. 11:20 - 12:50\n" \
                                       "✅ 4. 13:20 - 14:50\n" \
                                       "✅ 5. 15:00 - 16:30\n" \
                                       "✅ 6. 16:40 - 18:10\n" \
                                       "✅ 7. 18:20 - 19:50\n" \
                                       "✅ 8. 20:00 - 21:30\n" \
                                       "⛔ Главное меню"
                    handling_keyboard = self.read_keyboard("time_pair.json")
                else:
                    handling_message = "Выбран корпус %s. Укажите время и номер пары" % corp.upper()
                    handling_keyboard = self.read_keyboard("time_pair.json")
                self.setting = 61
                self.mode = "location"
                self.buffer = corp

            elif self.setting == 61:
                """
                Указываем номер пары
                """
                para = re.search("(\d)\. (\d){2}:(\d){2} - (\d){2}:(\d){2}", self.message)
                if para is None:
                    handling_message = "Неверно указано время пары"
                    handling_keyboard = self.read_keyboard("time_pair.json")
                    return handling_message, handling_attachment, handling_keyboard

                new_mes = "%s %s" % (self.buffer, para[1])
                keyboard = self.generator_date_keyboard()
                handling_keyboard = keyboard.get_keyboard()

                if self.check_keyboard_mode == "3":
                    handling_message = "Для получения расписания на определенный день -" \
                                       " используйте клавиатуру или введите дату" \
                                       " в формате: DD.MM.YYYY\n\nНапример: 03.11.2019\n\n" \
                                       "Для работы с ботом без клавиатуры " \
                                       "используйте следующие команды:\n⛔ Главное меню"
                else:
                    handling_message = "Для получения расписания на определенный день - " \
                                       "используйте клавиатуру или введите дату " \
                                       "в формате: DD.MM.YYYY\n\nНапример: 03.11.2019"
                self.setting = 62
                self.mode = "location"
                self.buffer = new_mes

            elif self.setting == 62:
                m_date = re.search("(\d){2}\.(\d){2}\.(\d){4}", self.message)
                date_short = re.search("(\d{2}).(\d{2}).\d{2}$", self.message)
                if date_short is not None:
                    self.message = "%s.%s.%s" % (date_short[1], date_short[2], datetime.now().year)

                elif m_date is None:
                    keyboard = self.generator_date_keyboard()
                    handling_message = "Дата указана не верно!"
                    handling_keyboard = keyboard.get_keyboard()
                    return handling_message, handling_attachment, handling_keyboard

                new_str = "%s %s" % (self.buffer, self.message)
                freerooms_audiences = re.search(r'^(\w) (\d) ((\d+[.|-]\d+[.|-]\d+)?)', new_str)
                self.free_req = self.check_open_phantom()
                handling_message, handling_attachment = Push(self.vk, self.free_req, self.put_id,
                                                             self.group).freerooms_audiences(
                    freerooms_audiences)
                close_driver[self.free_req] = False
                self.setting = 11
                self.mode = "main"
                self.buffer = "0"

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
                    handling_message = "В данный момент у вас %s объявления ожидают проверки модерацией" % count
                    self.setting = 41
                    self.mode = "note"
                elif self.message == "добавить":
                    handling_message = "Введите новое объявление"
                    handling_keyboard = self.read_keyboard("return.json")
                    self.setting = 41
                    self.mode = "note"

                elif self.message == "удалить":
                    handling_message = "Введите номер для удаления"
                    self.setting = 42
                    self.mode = "note"

            elif self.setting == 41:
                self.db_connector, self.db_cursor = db()
                self.db_cursor.execute(
                    "INSERT INTO `notes` (`id`, `vk_id`, `message_id`, `message_send`) "
                    "VALUES (NULL, '{}', '{}', '0');".format(self.put_id, self.message_id))
                handling_message = "Объявление добавлено в очередь на модерацию"
                self.setting = 11
                self.mode = "main"

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
                self.setting = 11
                self.mode = "main"
                self.buffer = "0"
                handling_message = "Введите номер объявления для удаления\n%s"
            self.db_connector.commit()

        elif self.mode == "post":
            if self.setting == 80:
                if self.message == "добавить":
                    handling_message = "Введите заголовок для новой заметки"
                    handling_keyboard = self.read_keyboard("return.json")
                    self.setting = 81
                    self.mode = "post"

                elif self.message == "удалить":
                    result, data_array_of_post = self.exist_list_doc()
                    if result == "У вас нет созданых записей!":
                        handling_message = result
                        handling_keyboard = self.read_keyboard("advertisement.json")
                        self.setting = 80
                        self.mode = "post"
                        self.buffer = "0"
                        return handling_message, handling_attachment, handling_attachment

                    handling_message = "%s\n\nВведите номер заметки для удаления" % result
                    handling_keyboard = self.read_keyboard("return.json")
                    self.setting = 85
                    self.mode = "post"

                elif self.message == "список":
                    result, data_array_of_post = self.exist_list_doc()
                    if result == "У вас нет созданых записей!":
                        handling_message = result
                        handling_keyboard = self.read_keyboard("advertisement.json")
                        self.setting = 80
                        self.mode = "post"
                        self.buffer = "0"
                        return handling_message, handling_attachment, handling_keyboard

                    handling_message = "%s\n\nВведите номер заметки для просмотра ее содержимого" % result
                    handling_keyboard = self.read_keyboard("return.json")
                    self.setting = 83
                    self.mode = "post"

            elif self.setting == 81:
                if len(self.message) > 50:
                    handling_message = "Заголовок сообщения не может превышать 50 символов!"
                    return handling_message, handling_attachment, handling_keyboard

                handling_message = "Прикрепите сюда сообщение"
                handling_keyboard = self.read_keyboard("return.json")
                self.setting = 82
                self.mode = "post"
                self.buffer = self._message

            elif self.setting == 82:
                self.db_connector, self.db_cursor = db()
                self.db_cursor.execute(
                    "INSERT INTO `post` (`id`, `vk_id`, `message_id`, `title`) "
                    "VALUES (NULL, '%s', '%s', '%s');" % (self.put_id, self.message_id, self.buffer))
                self.db_connector.commit()

                handling_message = "Заметка успешно добавлена"
                handling_keyboard = self.read_keyboard("advertisement.json")
                self.setting = 80
                self.mode = "post"
                self.buffer = "0"

            elif self.setting == 83:
                result, data_array_of_post = self.exist_list_doc()
                try:
                    number_of_message = int(self.message) - 1
                    self.vk.method("messages.send",
                                   {"user_ids": self.put_id,
                                    "intent": "default",
                                    "keyboard": self.read_keyboard("advertisement.json"),
                                    "forward_messages": data_array_of_post[number_of_message][1],
                                    "random_id": 0})
                    self.setting = 80
                    self.mode = "post"
                    self.buffer = self._message
                    handling_message = "Вы вернулись в меню заметкок"
                    handling_keyboard = self.read_keyboard("advertisement.json")

                except ValueError:
                    handling_message = "Необходимо указать номер заметки для просмотра ее содержимого"
                    handling_keyboard = self.read_keyboard("return.json")
                except IndexError:
                    handling_message = "Номер заметки указан не верно!"
                    handling_keyboard = self.read_keyboard("return.json")

            elif self.setting == 85:
                result, data_array_of_post = self.exist_list_doc()
                handling_keyboard = self.read_keyboard("advertisement.json")
                try:
                    number_of_message = int(self.message) - 1
                    self.db_connector, self.db_cursor = db()
                    self.db_cursor.execute("DELETE FROM `post` WHERE `post`.`message_id` = '%s'"
                                           % data_array_of_post[number_of_message][1])
                    self.db_connector.commit()
                    handling_message = "Заметка удалена!"
                    self.setting = 80
                    self.mode = "post"
                    self.buffer = self._message

                except ValueError:
                    handling_message = "Необходимо указать номер заметки для просмотра ее содержимого"
                except IndexError:
                    handling_message = "Номер заметки указан не верно!"


        elif self.mode == "msg":
            self.db_connector, self.db_cursor = db()
            if self.setting == 30:
                if self.message == "отдельным группам":
                    handing_message = "\n\n%s\n\nВведите номер группы. Если групп несколько, то разделите их " \
                                      "знаком пробела" % ParseNumberGroup(self.division)
                    handling_keyboard = self.read_keyboard("return.json")
                    self.setting = 31
                    self.mode = "msg"

                elif self.message == "всем группам факультета" or (self.message == "абсолютно всем факультетам"
                                                                   and self.msg == "3"):
                    handling_message = "Введите текст для рассылки"
                    handling_keyboard = self.read_keyboard("return.json")
                    if self.message == "абсолютно всем факультетам" and self.msg == "3":
                        mode = "allAdmin"
                    else:
                        mode = "all"
                    self.setting = 32
                    self.mode = "msg"
                    self.buffer = mode

                else:
                    handling_message = "Неверно выбран режим"


            elif self.setting == 31:
                self.db_connector, self.db_cursor = db()
                number_group = self.message.split(" ")
                handling_keyboard = self.read_keyboard("return.json")
                for num in number_group:
                    if num not in Group_1_back()[self.division].values():
                        handling_message = "Не существует %s группы!" % num
                        return handling_message, handling_attachment, handling_keyboard

                handling_message = "Введите текст для рассылки"
                self.setting = 32
                self.buffer = self.message

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
                    result = self.func_send_msg(self.short_name)  # Отпрака сообщений
                    if result != "USER_DOC":
                        handling_message = "Сообщение разослано!\nОтправлено в личные сообщения: {}\n" \
                                           "В беседы: 0".format(len(self.user_vk_resp))

                else:
                    handling_message = "В данных группах нет участников!"

                self.setting = 11
                self.mode = "main"
                self.buffer = "0"

            self.db_connector.commit()

        if handling_message == "":
            if self.mode == "admin" or self.mode == "msg":
                return None, None, None
            handling_message = "Команда не распознана. Вы вернулись в главное меню."
            handling_keyboard = self.keyboard_main
            self.setting = 11
            self.mode = "main"
            self.buffer = "0"

        return handling_message, handling_attachment, handling_keyboard

    def authorization(self):
        self.put_id = str(self.put_id)
        if mysql_dir.get(self.put_id) is None:  # Проверка vk_id на наличие в словаре
            self.db_connector, self.db_cursor = db()
            self.db_cursor.execute(
                "INSERT INTO `user` (`id`, `vk_id`, `division`, `user_group`, `role`, "
                "`link_doc`, `setting`, `mode`, `send_msg`, `buffer`, `notification_schedule`, "
                "`last_schedule`, `promo_newsletter`, `confirmed_notification`) VALUES (NULL, '%s', '0', '0', '0',"
                "'{\"Образовательный портал\": \"https://portal.edu.asu.ru/\", \"Английский\": \"https://vk.cc/9Krybk\"}',"
                " '0', 'reg', '0', '0', '1', '0', '0', '0');" % self.put_id)
            mysql_dir[self.put_id] = ('0', '0', '0', '{\"Образовательный портал\": \"https://portal.edu.asu.ru/\",'
                                                     ' \"Английский\": \"https://vk.cc/9Krybk\"}',
                                      '0', 'reg', '0', '0', '1', '0', '0', '0', '0', '0')
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
                        "intent": "default",

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
                                "intent": "default",
                                "attachment": values,
                                "random_id": 0})
        return attach

    def push_keyboard_main(self, ids):
        self.vk.method("messages.send",
                       {"user_ids": ids,
                        "intent": "default",
                        "message": "Вы вернулись в главное меню\n\nДля работы с ботом без клавиатуры "
                                   "используйте следующие команды:\n✅ Расписание группы\n✅ Расписание преподавателя\n"
                                   "✅ Свободные аудитории\n✅ Заметки\n✅ Панель управления\n⛔ Настройки",
                        "keyboard": self.read_keyboard("main.json"),
                        "random_id": 0})
        return

    def registration(self):
        handling_attachment = ""
        handling_keyboard = ""
        if self.setting == 0:
            handling_message = "%s\n\nВведите номер факультета" % facult
            handling_keyboard = self.read_keyboard("empty_keyboard.json")

            self.division = "0"
            self.group = "0"
            self.role = "0"
            self.link_doc = '{\"Образовательный портал\": \"https://portal.edu.asu.ru/\", '
            '\"Английский\":'
            ' \"https://vk.cc/9Krybk\"}'
            self.setting = 1
            self.mode = "reg"
            if self.msg != "2" and self.msg != "3":
                self.msg = "0"
            self.buffer = "0"
            self.notification_schedule = "1"
            self.last_schedule = "0"
            if self.promo_newsletter != "1":
                self.promo_newsletter = "0"
            if self.confirmed_notification != "1":
                self.confirmed_notification = "0"

        elif self.setting == 1:
            try:
                if self.message in get_id_by_number_group():
                    handling_message = "Выберите роль\n\n✅ Студент\n✅ Преподаватель"
                    handling_keyboard = self.read_keyboard("reg_role.json")
                    self.setting = 2
                    self.division = get_id_by_number_group()[self.message]
                else:
                    raise ValueError
            except ValueError:
                handling_message = "Номер факультета указан не верно!\nИспользуйте целое число.\n" \
                                   "Например: 16"
                handling_keyboard = self.read_keyboard("cancel.json")
                return handling_message, handling_attachment, handling_keyboard

        elif self.setting == 2:
            if self.message == "студент":
                handling_message = "%s\n\nВведите номер группы" % ParseNumberGroup(self.division)
                handling_keyboard = self.read_keyboard("cancel.json")

            elif self.message == "преподаватель":
                handling_message = "Укажите Фамилию Имя Очество для дальнейшего получения расписания"
                handling_keyboard = self.read_keyboard("cancel.json")

            else:
                handling_message = "Роль указана не верно!"
                handling_keyboard = self.read_keyboard("reg_role.json")
                return handling_message, handling_attachment, handling_keyboard

            self.setting = 3
            self.role = self.message

        elif self.setting == 3:
            if self.role == "преподаватель":

                message, teacher_name = find_prepod_by_fio(self.message)
                if message == "500":
                    reg_group = teacher_name

                else:
                    handling_message = message
                    handling_keyboard = self.read_keyboard("cancel.json")
                    return handling_message, handling_attachment, handling_keyboard

            elif self.message in Group_1_back()[self.division].values() and self.role == "студент":

                reg_group = find_ref_group_by_name(self.division, self.message)

            else:
                handling_message = "Номер группы указан не верно! Попробуйте еще раз!"
                handling_keyboard = self.read_keyboard("cancel.json")
                return handling_message, handling_attachment, handling_keyboard

            handling_message = "Подпишитесь на рассылку, если вы хотите получать " \
                               "информацию о добавлении, удалении, изменении расписания занятий.\n" \
                               "Отписаться от рассылки можно в любой момент в настройках."

            keyboard = VkKeyboard_new(one_time=False)
            keyboard.subscribe_push_message(self.put_id, "confirmed_notification", "Подписаться", "0")
            keyboard.add_line()
            keyboard.add_button("Отписаться", VkKeyboardColor_new.NEGATIVE)

            handling_keyboard = keyboard.get_keyboard()

            self.setting = 4
            self.group = reg_group

        elif self.setting == 4:

            if self.message == "подписаться":
                self.confirmed_notification = "1"

            handling_message = "Вы успешно зарегистрированы в системе. " \
                               "Для дальнейшей работы используйте встроенную клавиатуру"
            handling_keyboard = self.keyboard_main
            self.setting = 11
            self.mode = "main"

        return handling_message, handling_attachment, handling_keyboard

    def vk_send(self, message, attach="", keyboard=""):
        self.vk.method("messages.send",
                       {"peer_id": self.put_id, "message": message,
                        "intent": "default",
                        "attachment": attach, "keyboard": keyboard,
                        "random_id": 0, "dont_parse_links": 1})

    def read_keyboard(self, filename, directory="keyboards/"):
        return open(directory + filename, "r", encoding="UTF-8").read()


class Start:
    def __init__(self):
        pass

    def connect(self):
        vk = vk_api.VkApi(token=group_vk_api_token())
        longpoll = VkBotLongPoll(vk, 208894429)
        return vk, longpoll

    def vk_admin(self, message, attach=''):
        self.vk.method("messages.send",
                       {"peer_id": admin_vk_id(), "intent": "default", "message": message,
                        "attachment": attach,
                        "random_id": 0})

    def mainloop(self, exceptions):
        try:
            self.connect()
            if len(connectError) != 0:
                for message in connectError:
                    self.vk_admin(message)
            self.vk_admin('Произошла критическая ошибка! Бот был перезагружен!')
            self.start()
        except Exception as e:
            print('[{}] {}'.format(Time().brnTime(), e.__str__()))
            print("[{}] Установить соединение с севрером не удалось! Перезапуск скрипта через 15 секунд!".format(
                Time().brnTime()))
            connectError.append("Количество ошибок: {}\nКод ошибки:\n{}".format(exceptions, e.__str__()))
            time.sleep(15)
            print("[{}] Попытка подключиться к серверу".format(Time().brnTime()))
            exceptions += 1
            self.mainloop(exceptions)

    def start(self):
        global exceptions, image_push_of_day
        try:
            self.vk, self.longpoll = self.connect()
            longpoll = VkBotLongPoll(self.vk, 208894429)
            global event
            exceptions = 0
            for event in longpoll.listen():
                if event.type == VkBotEventType.MESSAGE_NEW:
                    if event.object.message["peer_id"] >= 2000000000:
                        continue
                    cVK = VkBot(self.vk, event)
                    t1 = threading.Thread(target=cVK.result)
                    t1.start()
        except Exception as e:
            exceptions += 1
            print('[{}] {}'.format(Time().brnTime(), e.__str__()))
            connectError.append("Количество ошибок: %s\nКод ошибки:\n%s\n\nСтатистика изображений подчищена. "
                                "Всего было отправлено за день: %s изображений" %
                                (exceptions, e.__str__(), image_push_of_day))
            image_push_of_day = 0
            self.mainloop(exceptions)


if __name__ == '__main__':
    exceptions = 0
    PhantomJS()
    GetInformationWithDB()
    Start().start()
    print('[{}] Бот был успешно запущен на сервере!'.format(Time().brnTime()))
