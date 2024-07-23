import os
import re
import src.Global as Global


def is_special_file(filename):
    pattern = r'^(RJ|VJ)\d{6}(\d{2})?$'
    if re.match(pattern, filename):
        return True
    return False


def get(folder_path):
    print('select file ...')
    works = []
    for filename in os.listdir(folder_path):
        if is_special_file(filename):
            works.append(filename)
    works.sort()
    Global.set_value("FileList", works)


get(Global.get_value('RootPath'))
