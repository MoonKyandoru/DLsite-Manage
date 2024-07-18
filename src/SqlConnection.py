import json
import MySQLdb
from src import Global

# SQL 处理器
class SqlConnection:
    def __init__(self):
        print('Initialize mysql ...')
        with open('SQL/dlsite.sql', 'r', encoding='utf-8') as f:
            createDataBase = f.read()
        self.commit(createDataBase)

    def commit(self, script: str):
        print('try to commit sql script ...')
        try:
            cursor = Global.get_value('dataBase').cursor()
            for statement in script.split(';'):
                if statement.strip():  # 忽略空语句
                    cursor.execute(statement)

            # 提交更改
            info = Global.get_value('dataBase').commit()
            print("SQL script executed successfully.")
            print(info)

        except MySQLdb.Error as e:
            print(f"Error executing SQL script: {e}")
            # 如果出错，回滚更改
            Global.get_value('dataBase').rollback()

        finally:
            # 关闭游标和连接
            cursor.close()
            Global.get_value('dataBase').close()

    def get(self):
        return Global.get_value('dataBase')
