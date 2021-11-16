from datetime import timedelta, datetime
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

stime = (datetime.now() + timedelta(hours=7)).strftime('%d.%m.%Y')

print(stime)
d = datetime.strptime(stime, "%d.%m.%Y")
pair_time_array = []

c = 0
k = 0
keyboard = VkKeyboard(one_time=True)

while c < 27:
    keyboard.add_button(d.strftime('%d.%m.%Y'), color=VkKeyboardColor.POSITIVE)
    if k == 3:
        k = 0
        keyboard.add_line()
    k += 1
    d = d + timedelta(days=1)
    c += 1

keyboard.add_button("Главное меню", color=VkKeyboardColor.NEGATIVE)


