from datetime import datetime
import mysql.connector as db

with open('connect', encoding='utf-8') as f:
    password = f.read().rstrip()

connection = db.connect(
    user='rl_playerinfo',
    password=password,
    host='localhost',
    database='rl_playerinfo')


def db_push_tracker_stats(listy: list):
    now = datetime.now()
    date_created = now.strftime("%d/%m/%Y %H:%M:%S")
    success = []

    for dicty in listy:
        print(dicty)
        if dicty['name'] == 'bogeymanEST' or dicty['name'] == 'poncho':
            continue

        dicty['date_created'] = date_created

        cursor = connection.cursor()
        columns = ', '.join(str(x) for x in dicty.keys())
        values = ', '.join("'" + str(x) + "'" for x in dicty.values())
        stmt = "INSERT INTO %s ( %s ) VALUES ( %s );" % ("tracker_stats", columns, values)

        try:
            cursor.execute(stmt)
            connection.commit()
            success.append(True)
        except db.Error as e:
            print(f'Error adding entry to database: {e}')

    return success
