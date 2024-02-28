# 获取已经下载的音声相关信息
import json
import os
import requests
from bs4 import BeautifulSoup
from my_class import Item, Info
from datetime import datetime

default_url = 'https://www.dlsite.com/maniax/work/=/product_id/'
datetime_now = datetime.now()
log_time = str(datetime_now.year) + '_' + str(datetime_now.month) + '_' + str(datetime_now.day) + '_' \
           + str(datetime_now.hour)
datetime_now = str(datetime.now())
data_success = 'data_success_' + log_time + '.log'
data_error = 'data_error_' + log_time + '.log'
data = 'data' + '.json'
soup = ''
res = []


# 获取信息， 在目录下输出 log (不论成功与否)
# 返回 'RJXXXXXX' | 'VJXXXXXX' 的 name, tag, cv; 失败则返回 None
def get_info(idx):
    global soup
    url = default_url + idx + '.html'
    info = Info(url=url, idx=idx)

    # 开始获取 尝试三次访问, 超时设定4秒
    for _i in range(3):
        try:
            response = requests.get(url, timeout=4)
            response.encoding = 'utf-8'
            html = response.text
            soup = BeautifulSoup(html, features='html.parser')
            break
        except requests.Timeout:
            pass
            # print('get info', idx, 'error')
        except requests.exceptions.SSLError:
            pass
            # print('no network !!')
        if _i == 2:
            return None

    company_item = soup.find('div', class_="error_box_inner")
    if company_item is not None:
        info.add_error('この作品は現在販売されていません')
        with open(data_error, 'a', encoding='utf-8') as f:
            f.write(str(info))
        return None

    # 从网页获取 name
    try:
        company_item = soup.find('h1', id='work_name')
        info.name = company_item.text.strip()
    except AttributeError:
        info.add_error('get info (name) error')

    # 从网页获取 tag
    try:
        company_item = soup.find('div', class_="main_genre")
        res = company_item.text.strip().split('\n')
        tag = []
        for _i in res:
            tag.append(_i)
        info.tag = tag
    except AttributeError:
        info.add_error('get info (tag) error')

    # 从网页获取 cv
    try:
        # 判断 CV 逻辑
        # 声优返回值 1 , 其他返回 -1 , 否则返回 0.
        def __check_cv(_name):
            if _name == '声優':
                return 1
            if _name == '販売日' or _name == 'シリーズ名' or _name == '作者' \
                    or _name == 'シナリオ' or _name == 'イラスト' or _name == '年齢指定' \
                    or _name == '作品形式' or _name == 'ファイル形式' or _name == 'ジャンル' \
                    or _name == 'ファイル容量' or _name == '音楽':
                return -1
            return 0

        cv = []
        company_item = soup.find('table', id='work_outline').text.split('\n')
        flag = 0
        for _i in company_item:
            for j in _i.split(' '):
                _temp = __check_cv(j)
                if flag == 1 and _temp < 0:
                    flag = None
                    break
                if flag == 1 and len(j) > 1:
                    cv.append(j)
                if _temp > 0:
                    flag = 1
            if flag is None:
                break
        info.cv = cv
    except AttributeError:
        info.add_error('get info (cv) error')

    if info.error_empty():
        with open(data_success, 'a', encoding='utf-8') as f:
            f.write(log_time + ' get info ' + idx + ' success\n')
        return info
    else:
        with open(data_error, 'a', encoding='utf-8') as f:
            f.write(log_time + str(info))
        return None


# 确认传入的路径合法, 或是否是自己能够操作的文件
def is_special_file(filename):
    if filename == 'Temp':
        return True
    if filename[0] == '$':
        return True
    if filename == 'list':
        return True
    if filename == 'Special':
        return True
    if filename == 'System Volume Information':
        return True
    if filename[0] == '.':
        return True
    if filename == 'bootTel.dat':
        return True
    if '字幕' in filename:
        return True
    return False


def get_Series(_folder_path, societies_name, series_name):

    print('扫描' + _folder_path + '中...')

    for filename in os.listdir(_folder_path):
        if is_special_file(filename):
            continue
        if filename[:2] == 'RJ' or filename[:2] == 'VJ':
            item = get_info(filename)
            if item is not None:
                print(str(datetime.now()) + ' get info ' + filename + ' success')
                item = Item(item, societies_name, series_name)
                item = {"idx": filename, "name": item.name, "societies_name": societies_name,
                        "series_name": series_name, "tag": item.tag, "cv": item.cv}
                global res
                res.append(item)
            continue


def get_societies(_folder_path, societies_name):
    print('扫描 ' + _folder_path + ' 中')

    for filename in os.listdir(_folder_path):
        if is_special_file(filename):
            continue

        if filename[:2] == 'RJ' or filename[:2] == 'VJ':
            item = get_info(filename)
            if item is None:
                continue
            item = Item(item, societies_name)
            print(str(datetime.now()) + ' get info ' + filename + ' success')
            with open(data, 'w', encoding='UTF-8') as f:
                item = {"idx": filename, "name": item.name, "societies_name": societies_name,
                        "tag": item.tag, "cv": item.cv}
                global res
                res.append(item)
            continue

        _son_folder_path = os.path.join(_folder_path, filename)
        if os.path.isdir(_son_folder_path):
            get_Series(_son_folder_path, societies_name, filename)


# 遍历文件夹 寻找需要添加 tag 的未定义目录
def get(_folder_path):
    print('扫描 ' + _folder_path + ' 中')

    for filename in os.listdir(_folder_path):
        if is_special_file(filename):
            continue

        _son_folder_path = os.path.join(_folder_path, filename)
        if os.path.isdir(_son_folder_path):
            get_societies(_son_folder_path, filename)

    global res
    with open(data, 'w', encoding='UTF-8') as f:
        res = json.dumps(res, indent=2)
        f.write(res)


if __name__ == '__main__':
    get('E:')
