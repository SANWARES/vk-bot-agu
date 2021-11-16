from datetime import timedelta, datetime


class Time:
    def brnTime(self):
        brnTime = datetime.now() + timedelta(hours=7)
        return datetime.strftime(brnTime, "%d.%m.%Y %H:%M:%S")
