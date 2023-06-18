# from return_to_monke import dbpass
from datetime import datetime
from logging_setup import log
import mysql.connector as db


credentials = {'user': 'rl_playerinfo',
               'password': 'password',
               'host': 'localhost',
               'database': 'rl_playerinfo'}


def db_push_tracker_stats(listy: list):
    now = datetime.now()
    date_created = now.strftime("%d/%m/%Y %H:%M:%S")

    for dicty in listy:
        # You may want to avoid constantly pushing yourself and teammates into the database
        ignore = ['', '']
        if dicty['name'] in ignore:
            continue

        dicty['date_created'] = date_created

        columns = ', '.join(str(x) for x in dicty.keys())
        values = ', '.join("'" + str(x) + "'" for x in dicty.values())
        stmt = "INSERT INTO %s ( %s ) VALUES ( %s );" % ("tracker_stats", columns, values)

        try:
            connection = db.connect(**credentials)
        except db.Error as err:
            if err.errno == db.errorcode.ER_ACCESS_DENIED_ERROR:
                log.error("Access denied, check credentials")
            elif err.errno == db.errorcode.ER_BAD_DB_ERROR:
                log.error('Database defined in credentials does not exist')
            else:
                log.error(err)
        else:
            cursor = connection.cursor()
            cursor.execute(stmt)
            connection.commit()
            connection.close()
