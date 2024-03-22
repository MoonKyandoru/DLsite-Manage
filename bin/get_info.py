# 获取已经下载的音声相关信息
import json
import os
import re
import requests
import MySQLdb
from bs4 import BeautifulSoup
from datetime import datetime

# 输出日志
data_success = 'success.log'
data_error = 'error.log'
data = 'data.json'
soup = None

with open('config.json', 'r', encoding='utf-8') as f:
    config = json.loads(f.read())
db = MySQLdb.connect(host=config['host'], port=config['port'], user=config['user'], db=config['db'],
                     passwd=config['passwd'],
                     charset='utf8')
cursor = db.cursor()
cursor.execute("use " + config['db'])


# 获取信息, 在目录下输出 log (不论成功与否) 然后返回 'RJXXXXXX' | 'VJXXXXXX' 的 作品名称, Tag, CV, 系列(如果存在的话), 社团名称; 失败则返回 None
def get_info(idx):
    print(idx, end=', ')
    global soup
    url = 'https://www.dlsite.com/maniax/work/=/product_id/' + idx + '.html'

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
            return None
        if _i == 2:
            print('get info', idx, 'error')
            return None

    company_item = soup.find('div', class_="error_box_inner")
    if company_item is not None:
        print(idx + ':この作品は現在販売されていません')
        return None

    # 遍历所有<a>以及<div>，将其替换为<span>

    links = soup.find_all('a')
    for link in links:
        new_div = soup.new_tag('span')
        if link.string is not None:
            new_div.string = link.string
            link.replace_with(new_div)
    links = soup.find_all('div')
    for link in links:
        new_div = soup.new_tag('span')
        if link.string is not None:
            new_div.string = link.string
            link.replace_with(new_div)

    info = {'idx': idx, 'name': soup.find('h1', id='work_name').text, 'url': url}

    # 定位信息框

    soup = soup.find('table', id='work_outline')

    # 处理相关信息

    rows = soup.find_all('tr')
    for row in rows:

        # 找到当前行中的所有表头单元格（th)

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

    SellDay = '販売日'
    SeriesName = 'シリーズ名'
    Author = '作者'
    Scenario = "シナリオ"
    Illustration = "イラスト"
    Music = "音楽"
    AgeSpecification = "年齢指定"
    FileCapacity = "ファイル容量"
    WorkFormat = "作品形式"
    CircleName = "サークル名"

    if SeriesName not in info.keys():
        info[SeriesName] = None
    else:
        info[SeriesName] = info[SeriesName][0]

    if SellDay not in info.keys():
        info[SellDay] = None
    else:
        info[SellDay] = re.sub(r'[^0-9]', '', info[SellDay][0])

    if Author not in info.keys():
        info[Author] = None
    else:
        info[Author] = info[Author][0]
    if Scenario not in info.keys():
        info[Scenario] = None
    else:
        info[Scenario] = info[Scenario][0]

    if Illustration not in info.keys():
        info[Illustration] = None
    else:
        info[Illustration] = info[Illustration][0]
    if Music not in info.keys():
        info[Music] = None
    else:
        info[Music] = info[Music][0]
    if "18" in info[AgeSpecification]:
        info[AgeSpecification] = "r18"
    elif "全" in info[AgeSpecification]:
        info[AgeSpecification] = "all"
    else:
        info[AgeSpecification] = 'unknown'
    if 'G' in info[FileCapacity][0]:
        info[FileCapacity] = float(re.sub(r'[^0-9.]', '', info[FileCapacity][0])) * 1024
    else:
        info[FileCapacity] = float(re.sub(r'[^0-9.]', '', info[FileCapacity][0]))
    if WorkFormat not in info.keys():
        info[WorkFormat] = None
    else:
        info[WorkFormat] = info[WorkFormat][0]
    if CircleName not in info.keys():
        info[CircleName] = None
    else:
        info[CircleName] = info[CircleName][0]

    try:
        cursor.execute("select dlsite.id from dlsite where dlsite.id='%s'" % (info['idx']))
        output = cursor.fetchone()
        if output is None:
            cursor.execute("insert into dlsite (ID) value ('" + info['idx'] + "');")
        else:
            raise ValueError("")
        cursor.execute("update dlsite set %s='%s' WHERE ID='%s';" % ('URL', url, info['idx']))
        if info['name'] is not None:
            cursor.execute("update dlsite set %s='%s' WHERE ID='%s';" % ('Name', info['name'], info['idx']))
        if info[SellDay] is not None:
            cursor.execute("update dlsite set %s='%s' WHERE ID='%s';" % ('SellDay', info[SellDay], info['idx']))
        if info[SeriesName] is not None:
            cursor.execute("update dlsite set %s='%s' WHERE ID='%s';" % ('SeriesName', info[SeriesName], info['idx']))
        if info[Author] is not None:
            cursor.execute("update dlsite set %s='%s' WHERE ID='%s';" % ('Author', info[Author], info['idx']))
        if info[Scenario] is not None:
            cursor.execute("update dlsite set %s='%s' WHERE ID='%s';" % ('Scenario', info[Scenario], info['idx']))
        if info[Illustration] is not None:
            cursor.execute("update dlsite set %s='%s' WHERE ID='%s';" % ('Illustration', info[Illustration], info['idx']))
        if info[Music] is not None:
            cursor.execute("update dlsite set %s='%s' WHERE ID='%s';" % ('Music', info[Music], info['idx']))
        if info[AgeSpecification] is not None:
            cursor.execute("update dlsite set %s='%s' WHERE ID='%s';" % ('AgeSpecification', info[AgeSpecification], info['idx']))
        if info[WorkFormat] is not None:
            cursor.execute("update dlsite set %s='%s' WHERE ID='%s';" % ('WorkFormat', info[WorkFormat], info['idx']))
        if info[FileCapacity] is not None:
            cursor.execute("update dlsite set %s='%s' WHERE ID='%s';" % ('FileCapacity', info[FileCapacity], info['idx']))
        if info[CircleName] is not None:
            cursor.execute("update dlsite set %s='%s' WHERE ID='%s';" % ('CircleName', info[CircleName], info['idx']))

        for i in info['声優']:
            cursor.execute("insert into cv value('%s', '%s')" % (info['idx'], i))
        for i in info['ジャンル']:
            cursor.execute("insert into tag value('%s', '%s')" % (info['idx'], i))
        db.commit()
    except MySQLdb.connections.Error:
        db.rollback()  # 发生错误时回滚
    except ValueError:
        pass

    # 输出日志
    datetime_now = str(datetime.now())
    with open('logger.data', 'a', encoding='utf-8') as file:
        logger = datetime_now + ':' + idx + '\n'
        file.write(logger)


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


# 遍历文件夹 寻找需要添加 tag 的未定义目录
def get(folder_path):
    print('扫描 ' + folder_path + ' 中')

    i = 0
    for filename in os.listdir(folder_path):
        if is_special_file(filename):
            continue
        get_info(filename)
        i += 1
        if i % 10 == 0:
            print('')
        if i >= 10:
            return None


if __name__ == '__main__':
    get_info('RJ01002989')
    cursor.close()
    db.close()
