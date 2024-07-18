import MySQLdb
import json
import src.SqlConnection as SqlConnection

def _init():
    global _global_dict
    _global_dict = {}
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.loads(f.read())
    set_value('DataBaseName', config['DataBaseName'])
    DataBase = SqlConnection.SqlConnection
    DataBase(config)

def set_value(name, value):
    _global_dict[name] = value


def get_value(name, defValue=None):
    try:
        return _global_dict[name]
    except KeyError:
        return defValue
