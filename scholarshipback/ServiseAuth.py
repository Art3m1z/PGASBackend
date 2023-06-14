import psycopg2
import json

import pyodbc
import requests
import csv
from requests.auth import HTTPBasicAuth
import datetime
import uuid


STATUS = ['Является ординатором', 'Является студентом-стажёром', 'Является аспирантом', 'Является студентом',
          'Является аспирантом в ВУЗе-партнёре', 'Является студентом в ВУЗе-партнёре', 'Является экстерном']
DICT_COURSE = {"Первый": 1,
               "Второй": 2,
               "Третий": 3,
               "Четвертый": 4,
               "Пятый": 5,
               "Шестой": 6}

def auth_elephant2_db(login, password):
    SERVER = 'elephant2.int.kantiana.ru'
    DATABASE = 'IKBFU'
    USERNAME = 'ptest'
    PASSWORD = 'qazxswedc'
    try:
        smss = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};'
                              'SERVER=' + SERVER + ';'
                                                   'DATABASE=' + DATABASE + ';'
                                                                            'UID=' + USERNAME + ';PWD=' + PASSWORD)
        cursor = smss.cursor()

        tsql = f"select cp.LastName, cp.FirstName, cp.PatrName from  core_Persons cp" \
               f" inner join core_Credentials cc on cc.PersonId = cp.id   " \
               f"where Login='{login}' and Password='{password}'"
        with cursor.execute(tsql):
            rows = cursor.fetchall()
            print(rows, sep='\n')
            if len(rows[0]) == 3 and (rows[0][2]!='' or rows[0][2].strip()!='-'):
                return f"{rows[0][0].strip()} {rows[0][1].strip()} {rows[0][2].strip()}"
            elif rows[0][2]=='' or rows[0][2].strip()=='-':
                return f"{rows[0][0].strip()} {rows[0][1].strip()}"
    except Exception as e:
        print(e)
        return None

def get_info_from_1C():
    url = "http://10.99.99.205/UniDB/hs/StudentServices/AllStudents"
    resp = requests.get(url, auth=HTTPBasicAuth('WebAPI', 'webAPI'))
    data = resp.json()
    json.dump(data, open("student.json", "w", encoding='utf-8-sig'), ensure_ascii=False)
    return data

def get_data_1c(fio):
    with open('student.json', 'r', encoding='utf-8-sig') as stud_json:
        data_json = json.load(stud_json)
        data = []
        student=None
        for el in data_json:
            if el['ФизическоеЛицо'] == fio.strip() and el['Статус'] in STATUS and DICT_COURSE[el["Курс"].strip()] > 1:
                return el
    return None

def insert_into_pgas(login, password, student):
    DATABASE = "pgas"
    USER = "postgres"
    PASSWORD = "postgres"
    HOST = "10.99.99.146"
    PORT = "5432"
    id = None
    token = str(uuid.uuid4())
    table = 'scholarshipback_student(login, "password", "token", lastname, firstname, patronymic, birthday, phone, ' \
            'institut, profile, form, source_finance, "level", course, date_create_profile, "isDeleted", avatar, ' \
            '"learningPlan")'

    arr = [login,
           password,
           token,
           student['Фамилия'],
           student['Имя'],
           student['Отчество'],
           datetime.datetime.strptime(student['ДатаРождения'], '%d.%m.%Y 0:00:00').strftime('%Y-%m-%d'),
           student["Телефон"],
           student["Институт"],
           student["Направление"],
           student["ФормаОбучения"],
           student["Основа"],
           student["УровеньПодготовки"],
           DICT_COURSE[student["Курс"].strip()],
           datetime.datetime.now(),
           False,
           str("https://www.mikrox.com.tr/wp-content/uploads/2020/07/canlidestek.jpeg"),
           student["Направление"]]
    try:
        sql = f'insert into {table} values ({str(len(arr) * "%s,")[:-1]}) returning id'
        print(sql)
        conn = psycopg2.connect(dbname=DATABASE, user=USER,
                                password=PASSWORD, host=HOST, port=PORT)
        cur = conn.cursor()
        cur.execute(sql, tuple(arr))
        id = cur.fetchone()[0]
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as err:
        print(err)
    finally:
        conn.close()
    return id

def isLogin(login, password):
    pass



def main():
    login = 'ASeteikina'
    password = 'wAgqwJg'
    fio = auth_elephant2_db(login,password)
    print(fio)
    student = get_data_1c(fio)
    print(student)
    id = 0 #insert_into_pgas(login, password, student)
    if id:
        print('Success!')


if __name__ == '__main__':
    get_info_from_1C()
    main()