# DLsite-Auto-Get-Tag

## 使用条件:
* 需要有一个专门用来存储数据的固定路径
* 只能够对DLsite中的ASMR分区文件进行重命名,添加标签的操作
* 需要添加标签的文件路径, 必须名为 'RJXXXXXX' (6-7位数字) 或者 'VJXXXXXX' (6-7位数字)
* 安装mysql

## 使用步骤:
### 0x00 运行以下代码获取包
`pip install -r requirements.txt`

### 0x01 在config.json中修改参数
需要一些mysql基础 (后序可能再修改,把数据库内置, 但现在还在学习中)
  "host": "127.0.0.1",
  "port": 3306,
  "user": "",
  "passwd": "",

db: 数据库的名字(可以取一个你自己喜欢的)
  "db": "DLsite",
manager_path: DLsite作品所在的目录
  "manager_path": "E:\\",
data_path: 输出日志的地址
  "data_path": "logger",
first: 是否为第一次运行的判断
  "first": false
### 0x02 运行:
`get_tag.py`
