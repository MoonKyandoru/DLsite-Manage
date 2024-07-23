import json
from src.SqlConnection import SqlConnection


def set_value(name, value):
    _global_dict[name] = value


def get_value(name, defValue=None):
    try:
        return _global_dict[name]
    except KeyError:
        return defValue


global _global_dict
_global_dict = {}
with open('config.json', 'r', encoding='utf-8') as f:
    config = json.loads(f.read())
for i in config:
    set_value(i, config[i])
sql = SqlConnection(config)
set_value('SqlConnection', sql)
