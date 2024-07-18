# Web 处理器

import re
import requests
import MySQLdb
from bs4 import BeautifulSoup
from lxml import etree
from src import Global

data_success = 'success.log'
data_error = 'error.log'
data = 'data.json'

cursor = Global.get_value('DataBaseName').cursor()
dbName = Global.get_value('DataBaseName')
cursor.execute("use " + dbName)

SellDay = '販売日'
SeriesName = 'シリーズ名'
Author = '作者'
Societies = 'サークル名'
Scenario = "シナリオ"
Illustration = "イラスト"
Music = "音楽"
AgeSpecification = "年齢指定"
FileCapacity = "ファイル容量"
WorkFormat = "作品形式"
header = ['https://www.dlsite.com/maniax/work/=/product_id/']
def from_net_get(idx):
    soup = None
    html = None
    global header, url
    url = header[0] + idx + '.html'

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
        # 没有被贩卖的作品, 或者属于别的分区
        print('\033[1;37;40m\033[37m%s\033[0m\033[0m' % idx, end=',')
        return None
    else:
        # 这次运行过程中, 自动寻找的作品
        print('\033[4;36m%s\033[0m' % idx, end=', ')

    temp = etree.HTML(html).xpath('//span[@class="maker_name"]/a')[0].xpath('string(.)')
    info = {'idx': idx, 'name': soup.find('h1', id='work_name').text, 'url': url,
            Societies: temp}
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
    if AgeSpecification not in info.keys():
        info[AgeSpecification] = 'unknown'
    elif "18" in info[AgeSpecification]:
        info[AgeSpecification] = "r18"
    elif "全" in info[AgeSpecification]:
        info[AgeSpecification] = "all"
    else:
        info[AgeSpecification] = 'unknown'
    if FileCapacity not in info.keys():
        info[FileCapacity] = None
    elif 'G' in info[FileCapacity][0]:
        info[FileCapacity] = float(re.sub(r'[^0-9.]', '', info[FileCapacity][0])) * 1024
    else:
        info[FileCapacity] = float(re.sub(r'[^0-9.]', '', info[FileCapacity][0]))
    if WorkFormat not in info.keys() or info[WorkFormat] is None:
        info[WorkFormat] = None
    else:
        info[WorkFormat] = info[WorkFormat][0]
    if Societies not in info.keys():
        info[Societies] = None


# 获取信息, 在目录下输出 log (不论成功与否) 然后返回 'RJXXXXXX' | 'VJXXXXXX' 的 作品名称, Tag, CV, 系列(如果存在的话), 社团名称; 失败则返回 None
def get_info(idx):
    cursor.execute("select dlsite.id from dlsite where dlsite.id='%s'" % idx)
    output = cursor.fetchone()
    if output is not None:
        # 已经存在的作品, 非特殊输出格式
        print('%s' % idx, end=',')
        return None

    from_net_get(idx)

    try:
        global info
        cursor.execute("insert into dlsite (ID) value (%s) ON DUPLICATE KEY UPDATE ID=ID;", (info['idx'],))

        update_data = [
            ('URL', url),
            ('Name', info['name']),
            ('SellDay', info[SellDay]),
            ('SeriesName', info[SeriesName]),
            ('Author', info[Author]),
            ('Scenario', info[Scenario]),
            ('Illustration', info[Illustration]),
            ('Music', info[Music]),
            ('AgeSpecification', info[AgeSpecification]),
            ('WorkFormat', info[WorkFormat]),
            ('FileCapacity', info[FileCapacity]),
            ('Societies', info[Societies])
        ]
        update_query = "update dlsite set {} WHERE ID=%s;".format(
            ', '.join([f"{col}=%s" for col, val in update_data if val is not None])
        )
        print(update_query)
        # cursor.execute(update_query, tuple(val for col, val in update_data if val is not None) + (info['idx'],))

        cursor.execute("insert into dlsite (ID) value ('" + info['idx'] + "');")
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
            cursor.execute(
                "update dlsite set %s='%s' WHERE ID='%s';" % ('Illustration', info[Illustration], info['idx']))
        if info[Music] is not None:
            cursor.execute("update dlsite set %s='%s' WHERE ID='%s';" % ('Music', info[Music], info['idx']))
        if info[AgeSpecification] is not None:
            cursor.execute(
                "update dlsite set %s='%s' WHERE ID='%s';" % ('AgeSpecification', info[AgeSpecification], info['idx']))
        if info[WorkFormat] is not None:
            cursor.execute("update dlsite set %s='%s' WHERE ID='%s';" % ('WorkFormat', info[WorkFormat], info['idx']))
        if info[FileCapacity] is not None:
            cursor.execute(
                "update dlsite set %s='%s' WHERE ID='%s';" % ('FileCapacity', info[FileCapacity], info['idx']))
        if info[Societies] is not None:
            cursor.execute("update dlsite set %s='%s' WHERE ID='%s';" % ('Societies', info[Societies], info['idx']))
        if '声優' in info.keys():
            for i in info['声優']:
                cursor.execute("insert into cv value('%s', '%s')" % (info['idx'], i))
        if 'ジャンル' in info.keys():
            for i in info['ジャンル']:
                cursor.execute("insert into tag value('%s', '%s')" % (info['idx'], i))
        Global.get_value('dataBase').commit()
    except MySQLdb.connections.Error:
        Global.get_value('dataBase').rollback()  # 发生错误时回滚

    # 输出日志
    # datetime_now = str(datetime.now())
    # with open(config['data_path'] + '/logger.data', 'a', encoding='utf-8') as file:
    #     logger = datetime_now + ':' + idx + '\n'
    #     file.write(logger)