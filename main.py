import MySQLdb

from src import Global
from src import network
from src import spider


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
    filelist = Global.get_value('FileList')
    for i in filelist:
        network.get_info(i)


if '__main__' == __name__:
    main()
