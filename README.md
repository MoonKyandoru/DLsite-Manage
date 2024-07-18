正在恢复原本的功能, 本项目暂时不可用

# DLsite-Manage

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

```
localhost
"host": "127.0.0.1",

mysql设置的port
"port": 3306,

mysql的用户名以及密码
"user": "",
"passwd": "",

db: 数据库的名字(可以取一个你自己喜欢的)
"db": "DLsite",

manager_path: DLsite作品所在的目录, 需要自行填入
"manager_path": "",

data_path: 输出日志的地址, 一般为代码相对路径,可自行调整
"data_path": "logger",

first: 是否为第一次运行的判断
"first": false
```
### 0x02 运行:
使用代码`python main.py`, 或直接再编译器中执行`mian.py`文件

输出说明:
  * 白色字体默认背景色, 表示当前作品已经存在于数据库当中
  * 绿色字体默认背景色, 表示这次加入数据库当中的作品
  * 灰色字体褐色背景色, 表示此作品可能 分区/已经下架

### 0x03 特殊形式的作品
当前还没有提供支持的作品
1. 所有 `電撃G's magazine` 公司的作品
2. 可能存在的其他...