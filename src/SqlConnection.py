import MySQLdb
from src import Global


class SqlConnection:
    def __init__(self, config):
        try:
            print("Connect to the database ...")
            self.dataBase = MySQLdb.connect(
                host=config['host'],
                port=config['port'],
                user=config['username'],
                passwd=config['password'],
                charset='utf8')
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
            cursor = self.dataBase.cursor()
            for statement in script.split(';'):
                if statement.strip():
                    cursor.execute(statement)
            self.dataBase.commit()
        except MySQLdb.Error as e:
            print(f"Error executing SQL script: {e}")
            self.dataBase.rollback()
        finally:
            cursor.close()

    def insert(self, tableName, info):
        table = Global.get_value('DataBaseName') + '.' + tableName
        columns = ', '.join(info.keys())
        placeholders = ', '.join(['%s'] * len(info))
        sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        try:
            cursor = self.dataBase.cursor()
            cursor.execute(sql, tuple(info.values()))
            self.dataBase.commit()
        except MySQLdb.Error as e:
            print(f'insert information error, detailed error report is as follows: {e}')
            self.dataBase.rollback()
        finally:
            cursor.close()

    def search(self, name: str):
        try:
            cursor = self.dataBase.cursor()
            script = "SELECT id FROM " + Global.get_value('DataBaseName') + ".dlsite WHERE id = %s"
            cursor.execute(script, (name,))
            output = cursor.fetchone()
        except MySQLdb.Error as e:
            print({e})
            return
        if output is None:
            return False
        return True
