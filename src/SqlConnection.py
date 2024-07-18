import MySQLdb
from src import Global


class SqlConnection:
    def __init__(self, config):
        try:
            print("Connect to the database ...")
            dataBase = MySQLdb.connect(
                host=config['host'],
                port=config['port'],
                user=config['user'],
                passwd=config['passwd'],
                charset='utf8')
            Global.set_value('DataBase', dataBase)
            print("Database connection successful")
        except MySQLdb.Error as e:
            print("mysql connection error, detailed error report is as follows:")
            print({e})
        try:
            print("Initialize database ...")
            with open('SQL/dlsite.sql', 'r', encoding='utf-8') as f:
                createDataBase = f.read()
            self.commit(createDataBase)
            print("Initialize database success")
        except MySQLdb.Error as e:
            print("Initialize database error, detailed error report is as follows:")
            print({e})

    def commit(self, script: str):
        try:
            cursor = Global.get_value('DataBase').cursor()
            for statement in script.split(';'):
                if statement.strip():
                    cursor.execute(statement)
            Global.get_value('DataBase').commit()

        except MySQLdb.Error as e:
            print(f"Error executing SQL script: {e}")
            Global.get_value('DataBase').rollback()
        finally:
            cursor.close()
            Global.get_value('DataBase').close()
