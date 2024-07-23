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
    # template = input("please input {0}, defult={1}, blank to select default :".format(i, config[i]))
    # if template != '':
    #     set_value(i, config[i])
    # else:
    #     set_value(i, template)
    set_value(i, config[i])
sql = SqlConnection(config)
set_value('SqlConnection', sql)