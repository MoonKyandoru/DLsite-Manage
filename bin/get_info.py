# 获取已经下载的音声相关信息
import os
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# 前置url
default_url = 'https://www.dlsite.com/maniax/work/=/product_id/'

# 输出日志
data_success = 'success.log'
data_error = 'error.log'
data = 'data.json'
soup = None


# 获取信息， 在目录下输出 log (不论成功与否)
# 返回 'RJXXXXXX' | 'VJXXXXXX' 的 作品名称, Tag, CV, 系列(如果存在的话), 社团名称; 失败则返回 None
def get_info(idx):
    global soup
    url = default_url + idx + '.html'

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
        except requests.exceptions.SSLError:
            print('no network !!')
        if _i == 2:
            print('get info', idx, 'error')
            return None

    company_item = soup.find('div', class_="error_box_inner")
    if company_item is not None:
        print(idx + ':この作品は現在販売されていません')
        return None

    # 遍历所有超链接，将其替换为<div>块
    links = soup.find_all('a')
    for link in links:
        new_div = soup.new_tag('span')
        if link.string is not None:
            new_div.string = link.string
            link.replace_with(new_div)

    info = {'idx': idx, 'name': soup.find('h1', id='work_name').text}

    # 定位信息框
    soup = soup.find('table', id='work_outline')

    # 处理相关信息
    rows = soup.find_all('tr')
    for row in rows:
        # 找到当前行中的所有表头单元格（th）
        for header in row.find_all('th'):
            info[header.text] = []
            # 找到当前行中的所有数据单元格（td）
            for cell in row.find_all('td'):
                for i in cell.find_all('span'):
                    temp = i.text
                    temp = str(temp)
                    temp = temp.replace('\n', '')
                    temp = temp.replace(' ', '')
                    info[header.text].append(temp)
    with open('logger\\' + idx + '.json', 'w', encoding='UTF-8') as file:
        writer = json.dumps(info, indent=2)
        file.write(writer)

    # 获取当前时间
    datetime_now = datetime.now()
    datetime_now = str(datetime.now())
    with open('logger.data', 'a', encoding='utf-8') as f:
        logger = datetime_now + ':' + idx
        f.write(logger)


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
    return False


def get_series(folder_path):
    print('扫描' + folder_path + '中...')

    for filename in os.listdir(folder_path):

        if is_special_file(filename):
            continue

        if filename[:2] == 'RJ' or filename[:2] == 'VJ':
            get_info(filename)


def get_societies(folder_path):
    print('扫描 ' + folder_path + ' 中')

    for filename in os.listdir(folder_path):
        if is_special_file(filename):
            continue

        if filename[:2] == 'RJ' or filename[:2] == 'VJ':
            get_info(filename)
            continue

        son_folder_path = os.path.join(folder_path, filename)
        if os.path.isdir(son_folder_path):
            get_series(son_folder_path)


# 遍历文件夹 寻找需要添加 tag 的未定义目录
def get(folder_path):
    print('扫描 ' + folder_path + ' 中')

    for filename in os.listdir(folder_path):
        if is_special_file(filename):
            continue

        son_folder_path = os.path.join(folder_path, filename)
        if os.path.isdir(son_folder_path):
            get_societies(son_folder_path)


if __name__ == '__main__':
    get_info('RJ01088358')
