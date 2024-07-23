import MySQLdb

from src import Global
from src import network

# 初始化设定
def init():
    try:
        Global.get_value('DataBase')
    except MySQLdb.Error as e:
        print({e})
        return None

    return True


def main():
    if init() is None:
        return None
    network.get_info("RJ273058")


if '__main__' == __name__:
    main()
