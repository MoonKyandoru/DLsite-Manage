from src import SqlConnection
from src import Global

# 初始化设定

if '__main__' == __name__:
    Global._init()
    DataBase = SqlConnection
    DataBase.SqlConnection()