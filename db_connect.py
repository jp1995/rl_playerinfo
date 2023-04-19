# from datetime import datetime
# from return_to_monke import dbpass
# import mysql.connector as db


# connection = db.connect(
#     user='rl_playerinfo',
#     password='dbpass',
#     host='localhost',
#     database='rl_playerinfo')


def db_push_tracker_stats(listy: list):
    # now = datetime.now()
    # date_created = now.strftime("%d/%m/%Y %H:%M:%S")
    # errors = ['Unknown to API', 'API Server Error', 'No API Response', ' - AI']
    #
    # for dicty in listy:
    #     # For general player stats, making them actually usable, modify as needed
    #     if dicty['name'] == '' or dicty['name'] == '' or any(errors) in dicty['name']:
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
    #         print(dicty)
    #     except db.Error as e:
    #         print(f'Error adding entry to database: {e}\n{dicty}')

    pass  # remove this
