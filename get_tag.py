import os
import shutil
from bs4 import BeautifulSoup
import requests

default_url = 'https://www.dlsite.com/maniax/work/=/product_id/'

# 如果你希望增加标签的种类, 那么可以在修改标签的类之后将此字段调成 True, 运行之后将会重新获取一次所有需要的字段
add_tag = False

# 是否启动 debug 模式
# 如果启动, 那么每一个查找到的需要修改的文件, 都能够手动控制是否修改
debug = False

# 储存操作日志的位置
# 必填
change_info_path = '/home/moonkyandoru/Documents/loger.dat'

# 数据库的路径
# 必填
_folder_path = '/media/moonkyandoru/Voice'

error = []


# 查看某一个名字是否是规定的某个标签
def is_item_info(_path):
    name = _path.split('/')[-1:]
    if name == 'cv' or name == 'tag':
        return True
    return False


# 确认传入的路径合法, 或是否是自己能够操作的文件
def is_special_file(filename):
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


# 将传入的字符串转换成能够作为路径名的字符串
def to_accept_name(name):
    name = name.replace('!', '！')
    name = name.replace('?', '？')
    name = name.replace('\'', '')
    name = name.replace('\"', '')
    name = name.replace('/', '、')
    name = name.replace(':', '：')
    name = name.replace('+', ' and ')
    name = name.replace(' ', '_')
    name = name.replace('[', '「')
    name = name.replace(']', '」')
    return name


# 使用此程序, 用以删除所有的标签, 请小心使用
def delete(_folder_path):
    for filename in os.listdir(_folder_path):
        if not is_special_file(filename):
            continue

        if filename == 'tag' or filename == 'cv':
            shutil.rmtree(os.path.join(_folder_path, filename))
            continue


# 处理键盘输入
def check(_idx):
    # debug
    _cmd = str(input('change info ' + _idx))
    if _cmd == 'N' or _cmd == 'n':
        print()
        return False
    return True


# 寻找子目录是否存在 idx 标签
def find_idx_at_next_path(filepath):
    if not os.path.isdir(filepath):
        return None

    idx = ''
    for _i in os.listdir(filepath):
        _i_path = os.path.join(filepath, _i)
        if (_i[:2] == 'RJ' or _i[:2] == 'VJ') and ('.' not in _i) \
                and (not os.path.isdir(_i_path)):
            idx = _i
    if idx != '':
        return idx
    return None


class error_item_info:
    def __init__(self, _idx, _path, _name):
        self._idx = _idx
        self._path = _path
        self._name = _name

    def display(self):
        return str(self._idx)

    def get_idx(self):
        return self._idx

    def get_path(self):
        return self._path

    def get_name(self):
        return self._name


# 返回 'RJXXXXXX' | 'VJXXXXXX' 的 name, tag, cv
def get_info(_idx):
    url = default_url + _idx + '.html'

    # 开始获取
    try:
        response = requests.get(url, timeout=4)
        response.encoding = 'utf-8'
        html = response.text
        soup = BeautifulSoup(html, features='html.parser')
    except requests.Timeout:
        print('get info', _idx, 'error')
        return None
    except requests.exceptions.SSLError:
        print('has no network !!')
        check('NULL')
        return None

    try:
        # 从网页获取 name
        company_item = soup.find('h1', id='work_name')
        name = company_item.text.strip()
        name = to_accept_name(name)
    except AttributeError:
        print('get info', _idx, 'name error')
        return None

    try:
        # 从网页获取 tag
        company_item = soup.find('div', class_="main_genre")
        res = company_item.text.strip().split('\n')
        tag = []
        for _i in res:
            _i = to_accept_name(_i)
            for j in _i.split('/'):
                tag.append(j)
    except AttributeError:
        print('get info', _idx, 'tag error')
        return None

    # 判断 CV 逻辑
    def __check_cv(_name):
        if _name == '声優':
            return 1
        if _name == '販売日' or _name == 'シリーズ名' or _name == '作者' \
                or _name == 'シナリオ' or _name == 'イラスト' or _name == '年齢指定' \
                or _name == '作品形式' or _name == 'ファイル形式' or _name == 'ジャンル' \
                or _name == 'ファイル容量':
            return -1
        return 0

    try:
        # 从网页获取 cv
        cv = []
        company_item = soup.find('table', id='work_outline').text.split('\n')
        flag = 0
        for _i in company_item:
            for j in _i.split(' '):
                _temp = __check_cv(j)
                if flag == 1 and _temp < 0:
                    flag = 2
                    break
                if flag == 1 and len(j) > 0:
                    cv.append(j)
                if _temp > 0:
                    flag = 1
            if flag > 1:
                break
    except AttributeError:
        print('get info', _idx, 'cv error')
        return None

    print('get info', _idx, 'success')
    return name, tag, cv


# 增加标签, 并添加编号
def change_info(_folder_path, _idx, _filename=None):
    global change_info_path

    try:
        _info = 'change info ' + _idx + '\n'
        if debug and (not check(_idx)):
            return
        _all_info = get_info(_idx)
        if _all_info is None:
            error.append({error_item_info(_idx=_idx, _path=_folder_path, _name=_filename)})
            return
        name, tag, CV = _all_info
    except ValueError:
        print('set', _filename, 'error')
        error.append({error_item_info(_idx=_idx, _path=_folder_path, _name=_filename)})
        return

    # 修改文件名(如果需要的话)
    old_filepath = str(os.path.join(_folder_path, _idx))
    new_filepath = str(os.path.join(_folder_path, name))

    # 重建索引
    if _filename is None:
        # 处理已经存在的文件
        if os.path.exists(new_filepath):
            print(new_filepath, 'was exists')
            error.append({error_item_info(_idx=_idx, _path=_folder_path, _name=_filename)})
            return
        try:
            shutil.move(old_filepath, new_filepath)
            _info = _info + 'change ' + _idx + ' to ' + name + '\n'
        except shutil.Error:
            print(old_filepath, 'can\'t find or', new_filepath, 'was  ')
            error.append({error_item_info(_idx=_idx, _path=_folder_path, _name=_filename)})
    else:
        new_filepath = str(os.path.join(_folder_path, _filename))

    # 创建 idx
    idx_path = str(os.path.join(new_filepath, _idx))
    file = open(idx_path, 'w')
    file.close()
    _info = _info + _idx + ' add idx' + '\n'

    # 创建 tag 文件夹
    _tag_dir = str(os.path.join(new_filepath, 'tag'))
    if not os.path.exists(_tag_dir):
        os.mkdir(_tag_dir)
    # 添加 tag
    _info = _info + _idx + ' add tag ' + str(tag) + '\n'
    for _i in tag:
        _tag_name = to_accept_name(_i)
        label_path = str(os.path.join(_tag_dir, _tag_name))
        file = open(label_path, 'w')
        file.close()

    # 创建 cv 文件夹
    _cv_dir = str(os.path.join(new_filepath, 'cv'))
    if not os.path.exists(_cv_dir):
        os.mkdir(_cv_dir)
    # 添加 cv
    _info = _info + _idx + ' add cv ' + str(CV) + '\n\n'
    for _i in CV:
        _cv_name = to_accept_name(_i)
        label_path = os.path.join(_cv_dir, _cv_name)
        file = open(label_path, 'w')
        file.close()

    f = open(change_info_path, 'a')
    f.write(_info)


# 遍历文件夹 寻找需要添加 tag 的未定义目录
def get_url(_folder_path):
    for filename in os.listdir(_folder_path):
        if is_special_file(filename):
            continue

        # 通常情况, 编号就是路径名
        if (filename[:2] == 'RJ' or filename[:2] == 'VJ') and os.path.isdir(os.path.join(_folder_path, filename)):
            change_info(_folder_path=_folder_path, _idx=filename)
            continue

        # 如果有子目录 或者 需要添加更多标签
        _son_folder_path = os.path.join(_folder_path, filename)
        _flag = None
        if add_tag:
            _flag = find_idx_at_next_path(_son_folder_path)
        if _flag is not None:
            # 清除子节点已经添加的所有标签
            delete(_son_folder_path)

            # 重新填写标签
            change_info(_folder_path=_folder_path, _filename=filename, _idx=_flag)
            continue
        if os.path.isdir(_son_folder_path):
            get_url(_son_folder_path)


if '__main__' == __name__:
    while True:
        get_url(_folder_path)
        if len(error) == 0:
            break

        for _i in error:
            print(_i.display(), end=', ')
        print()
        a = input('restart ? [y/n]')
        if a[0] == 'n':
            break

        t = error
        error = []
        for _i in t:
            _idx = _i.get_idx()
            _name = _i.get_name()
            _path = _i.get_path()
            change_info(_folder_path=_path, _idx=_idx, _filename=_name)
