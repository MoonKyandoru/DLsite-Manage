import json
import MySQLdb


class SqlConnection:
    def createDataBase(self):
        print('Initialize mysql ...')
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.loads(f.read())
        dataBase = MySQLdb.connect(
            host=config['host'],
            port=config['port'],
            user=config['user'],
            passwd=config['passwd'],
            charset='utf8')
        cursor = dataBase.cursor()

        with open('SQL/dlsite.sql', 'r', encoding='utf-8') as f:
            createDataBase = f.read()

        try:
            for statement in createDataBase.split(';'):
                if statement.strip():  # 忽略空语句
                    cursor.execute(statement)

            # 提交更改
            dataBase.commit()
            print("SQL script executed successfully.")

        except MySQLdb.Error as e:
            print(f"Error executing SQL script: {e}")
            # 如果出错，回滚更改
            dataBase.rollback()

        finally:
            # 关闭游标和连接
            cursor.close()
            dataBase.close()

    def __init__(self):
        self.createDataBase()


if '__main__' == __name__:
    DataBase = SqlConnection()