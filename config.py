import mysql.connector

def admin_vk_id():
    my_id = "549944532"
    return my_id


def group_vk_api_token():
    token = "f207f4392b9d1b3dbee8340e1154ce8a8ad78d0c1063da19859a319a677945821f29f5b086c357ba452d1"
    return token


def db_config() -> list:
    login = "f0600435.xsph.ru"
    user = "f0600435_agu_bot"
    password = "Test123123"
    db_name = "f0600435_agu_bot"
    return [login, user, password, db_name]

def db():
    db_connect = mysql.connector.connect(
        host=db_config()[0],
        user=db_config()[1],
        passwd=db_config()[2],
        database=db_config()[3]
    )
    db_cursor = db_connect.cursor()
    return db_connect, db_cursor
