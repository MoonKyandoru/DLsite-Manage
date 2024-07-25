# Web 处理器

import re
import requests
import MySQLdb
from bs4 import BeautifulSoup
from lxml import etree
from src import Global

error_dict = {1: 'network error',
              2: 'get information error',
              3: "can't get information"
              }
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
headers = ['https://www.dlsite.com/maniax/work/=/product_id/{0}.html']


def checkSeriesName(info):
    if SeriesName not in info.keys():
        info[SeriesName] = None
    else:
        info[SeriesName] = info[SeriesName][0]


def checkSellDay(info):
    if SellDay not in info.keys():
        info[SellDay] = None
    else:
        info[SellDay] = re.sub(r'[^0-9]', '', info[SellDay][0])


def checkAuthor(info):
    if Author not in info.keys():
        info[Author] = None
    else:
        info[Author] = info[Author][0]


def checkScenario(info):
    if Scenario not in info.keys():
        info[Scenario] = None
    else:
        info[Scenario] = info[Scenario][0]


def checkIllustration(info):
    if Illustration not in info.keys():
        info[Illustration] = None
    else:
        info[Illustration] = info[Illustration][0]


def checkMusic(info):
    if Music not in info.keys():
        info[Music] = None
    else:
        info[Music] = info[Music][0]


def checkAgeSpecification(info):
    if AgeSpecification not in info.keys():
        info[AgeSpecification] = 'unknown'
    elif "18" in info[AgeSpecification]:
        info[AgeSpecification] = "r18"
    elif "全" in info[AgeSpecification]:
        info[AgeSpecification] = "all"
    else:
        info[AgeSpecification] = 'unknown'


def checkFileCapacity(info):
    if FileCapacity not in info.keys():
        info[FileCapacity] = None
    elif 'G' in info[FileCapacity][0]:
        info[FileCapacity] = float(re.sub(r'[^0-9.]', '', info[FileCapacity][0])) * 1024
    else:
        info[FileCapacity] = float(re.sub(r'[^0-9.]', '', info[FileCapacity][0]))


def checkWorkFormat(info):
    if WorkFormat not in info.keys() or info[WorkFormat] is None:
        info[WorkFormat] = None
    else:
        info[WorkFormat] = info[WorkFormat][0]
    checkSocieties(info)


def checkSocieties(info):
    if Societies not in info.keys():
        info[Societies] = None


def replaceToSpan(soup):  # 遍历所有<a>以及<div>，将其替换为<span>
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
    return soup


def addToDataBase(name):
    if Global.get_value('SqlConnection').search(name):
        # 已经存在的作品, 非特殊输出格式
        # print('%s' % name, end=',')
        return None

    info = get_url(name)
    if isinstance(info, int):
        print(error_dict[info])
        if info == 3:
            print(name, end=',')
        return None

    update_data = {
        'ID': info.get('ID'),
        'URL': info.get('url'),
        'Name': info.get('name'),
        'SellDay': info.get(SellDay),
        'SeriesName': info.get(SeriesName),
        'Author': info.get(Author),
        'Scenario': info.get(Scenario),
        'Illustration': info.get(Illustration),
        'Music': info.get(Music),
        'AgeSpecification': info.get(AgeSpecification),
        'WorkFormat': info.get(WorkFormat),
        'FileCapacity': info.get(FileCapacity),
        'Societies': info.get(Societies)
    }

    try:
        Global.get_value('SqlConnection').insert('dlsite', update_data)
        pass
    except MySQLdb.connections.Error:
        Global.get_value('dataBase').rollback()  # 发生错误时回滚


def get_url(name):  # 遍历查找正确的url
    for header in headers:
        url = header.format(name)
        res = from_net_get(name, url)
        if isinstance(res, int):
            continue
        return res
    return 3
    # print('未找到此作品')


def netTryConn(url):  # 尝试三次访问, 超时设定4秒
    for _i in range(3):
        try:
            response = requests.get(url, timeout=3)
            response.encoding = 'utf-8'
            html = response.text
            soup = BeautifulSoup(html, features='html.parser')
            return soup
        except requests.Timeout:
            pass
        except requests.exceptions.SSLError:
            return 1
    return 2


def from_net_get(ID, url):
    soup = netTryConn(url)
    if isinstance(soup, int):
        return soup

    if soup.find('div', class_="error_box_inner") is not None:
        pass  # 没有被贩卖的作品, 或者属于别的分区
    else:
        pass  # 这次运行过程中, 自动寻找的作品
    if soup.find('h1', id='work_name') is None:
        return 3
    info = {'ID': ID,
            'url': url,
            'name': soup.find('h1', id='work_name').text,
            Societies: soup.find('span', class_='maker_name').get_text()
            }
    soup = replaceToSpan(soup)
    soup = soup.find('table', id='work_outline')  # 定位信息框

    # 处理相关信息
    rows = soup.find_all('tr')
    for row in rows:

        for header in row.find_all('th'):  # 找到当前行中的所有表头单元格（th)
            info[header.text] = []

            for cell in row.find_all('td'):  # 找到当前行中的所有数据单元格（td）
                for i in cell.find_all('span'):
                    temp = i.text
                    temp = str(temp)
                    temp = temp.replace('\n', '')
                    temp = temp.replace(' ', '')
                    info[header.text].append(temp)

    checkSeriesName(info)  # 获取是否属于某个作品系列
    checkSellDay(info)  # 获取作品的发售日期
    checkAuthor(info)  # 获取作品的作者
    checkScenario(info)
    checkIllustration(info)
    checkMusic(info)  # 获取作品的音乐
    checkAgeSpecification(info)  # 获取作品的年龄分级
    checkFileCapacity(info)  # 获取作品的文件大小
    checkWorkFormat(info)  # 获取作品的文件格式

    return info
