# from return_to_monke import dbpass
# from datetime import datetime
# from logging_setup import log
# import mysql.connector as db
#
#
# connection = db.connect(
#     user='rl_playerinfo',
#     password=dbpass,
#     host='localhost',
#     database='rl_playerinfo')


def db_push_tracker_stats(listy: list):
    # now = datetime.now()
    # date_created = now.strftime("%d/%m/%Y %H:%M:%S")
    #
    # for dicty in listy:
    #     # You may want to avoid constantly pushing yourself and teammates into the database
    #     if dicty['name'] == '' or dicty['name'] == '':
    #         continue
    #
    #     dicty['date_created'] = date_created
    #
    #     cursor = connection.cursor()
    #     columns = ', '.join(str(x) for x in dicty.keys())
    #     values = ', '.join("'" + str(x) + "'" for x in dicty.values())
    #     stmt = "INSERT INTO %s ( %s ) VALUES ( %s );" % ("tracker_stats", columns, values)
    #
    #     try:
    #         cursor.execute(stmt)
    #         connection.commit()
    #     except db.Error as e:
    #         log.error(f'Error adding entry to database: {e}\n{dicty}')

    pass  # REMOVE THIS
