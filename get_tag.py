import os
import shutil
from bs4 import BeautifulSoup
import requests

defult_url = 'https://www.dlsite.com/maniax/work/=/product_id/'

# if you add a tag, and want rebuild
add_tag = False

# if you want to decide each operate about the file
debug = False

error = []


"""
change the string i, let i can be rename as a filepath
"""
def to_accpet_name(i):
    i = i.replace('!', '！')
    i = i.replace('?', '？')
    i = i.replace('\'', '')
    i = i.replace('\"', '')
    i = i.replace('/', '、')
    i = i.replace(':', '：')
    i = i.replace('+', ' and ')
    i = i.replace(' ', '')
    i = i.replace('[', '「')
    i = i.replace(']', '」')
    return i

"""
use this to delete all tag and cv, but reserve number
careful to use this function
"""
def delete(folder_path):
    for filename in os.listdir(folder_path):
        if not is_special_file(filename):
            continue

        if filename == 'tag' or filename == 'cv':
            shutil.rmtree(os.path.join(folder_path, filename))
            continue

        if os.path.isdir(os.path.join(folder_path, filename)):
            delete(os.path.join(folder_path, filename))

"""
when debug==True, it's can let you decide each operate about the file
"""
def check():
    # debug
    a = input('push enter to continue, or push [N/n] to pass')
    if a == 'N' or a == 'n':
        print()
        return False
    return True


def is_special_file(filename):
    if filename == 'System Volume Information':
        return True
    if filename[0] == '.':
        return True
    if filename == 'bootTel.dat':
        return True
    if '字幕' in filename:
        return True

    return False

"""
return RJ tag&name
"""
def get_info(idx):
    url = defult_url + idx + '.html'
    try:
        response = requests.get(url)
        response.encoding = 'utf-8'
        html = response.text
        soup = BeautifulSoup(html, features='html.parser')
        company_item = soup.find('div', class_="main_genre")
        res = company_item.text.strip().split('\n')
        tag = []
        for i in res:
            i = to_accpet_name(i)
            for j in i.split('/'):
                tag.append(j)

        name = ''
        company_item = soup.find('h1', id='work_name')
        name = company_item.text
        name = to_accpet_name(name)

        cv = []
        company_item = soup.find('table', id='work_outline').text.split('\n')
        flag = 0
        for i in company_item:
            for j in i.split(' '):
                company_item.append(j)
                if j == '音楽' or j == '年齢指定':
                    flag = 2
                    break
                if flag == 1 and len(j) > 1:
                    cv.append(j)
                if j == '声優':
                    flag = 1
            if flag > 1:
                break

        print('get info', idx, 'success')
        return name, tag, cv
    except:
        print('get info', idx, 'error')
        error.append(idx)
        return None

"""
添加 tag 并且 修改 name
"""
def change_info(folder_path, filename):
    try:
        print('change info', filename)
        if debug:
            if not check():
                return

        print('get info', filename, 'begin...')
        name, tag, cv = get_info(filename)

        # 修改文件名
        old_filepath: str
        new_filepath: str
        old_filepath = os.path.join(folder_path, filename)
        new_filepath = os.path.join(folder_path, name)
        if os.path.exists(new_filepath):
            print(filename, 'exists')
        else:
            shutil.move(old_filepath, new_filepath)
            print('change', filename, 'to', name)

        # 创建 idx
        file = open(os.path.join(new_filepath, filename), 'w')
        file.close()
        print(filename, 'add idx')

        # 创建 tag 文件夹
        ifdir = os.path.join(new_filepath, 'tag')
        if not os.path.exists(ifdir):
            os.mkdir(ifdir)
        # 添加 tag
        print(filename, 'add tag', tag)
        for i in tag:
            filepath = os.path.join(ifdir, i)
            file = open(filepath, 'w')
            file.close()

        # 创建 cv 文件夹
        ifdir = os.path.join(new_filepath, 'cv')
        if not os.path.exists(ifdir):
            os.mkdir(ifdir)
        # 添加 cv
        print(filename, 'add cv ', cv)
        for i in cv:
            filepath = os.path.join(ifdir, i)
            file = open(filepath, 'w')
            file.close()
        print()
    except:
        print('set', filename, 'error')
        print('')
        error.append(filename)



"""
find if son has 'RJXXXXXX'
"""
def find_idx_at_next_path(filepath):
    if not os.path.isdir(filepath):
        return True

    idx = ''
    for i in os.listdir(filepath):
        if i[:2] == 'RJ' and os.path.isdir(os.path.join(filepath, i)):
            idx = i
    if idx != '':
        return idx
    return None

"""
遍历文件夹 寻找需要添加 tag 的未定义目录
"""
def get_url(folder_path):
    for filename in os.listdir(folder_path):
        if is_special_file(filename):
            continue

        # normal
        if filename[:2] == 'RJ' and os.path.isdir(os.path.join(folder_path, filename)):
            print('change info', filename)
            change_info(folder_path, filename)
            print()

            continue

        filepath = os.path.join(folder_path, filename)
        flag = None
        if add_tag:
            flag = find_idx_at_next_path(filepath)
        if flag is not None:
            change_info(folder_path, filename)
            continue
        if os.path.isdir(filepath):
            get_url(filepath)


if '__main__' == __name__:
    folder_path = "/media/moonkyandoru/Voice"
    get_url(folder_path)
    for i in error:
        print(i, end=', ')
