import MySQLdb
import json


def _init():
    global _global_dict
    _global_dict = {}
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.loads(f.read())
    db = MySQLdb.connect(
        host=config['host'],
        port=config['port'],
        user=config['user'],
        passwd=config['passwd'],
        charset='utf8')
    set_value('dataBase', db)
    set_value('DataBaseName', config['DataBaseName'])

def set_value(name, value):
    _global_dict[name] = value


def get_value(name, defValue=None):
    try:
        return _global_dict[name]
    except KeyError:
        return defValue
