import json
import os
import MySQLdb

with open('config.json', 'r', encoding='utf-8') as f:
    config = json.loads(f.read())

if config['first']:
    db = MySQLdb.connect(host=config['host'], port=config['port'], user=config['user'], passwd=config['passwd'],
                         charset='utf8')
    cursor = db.cursor()
    cursor.execute("create database " + config['db'])
    cursor.execute("use " + config['db'])
    cursor.execute("create table dlsite("
                   "ID					varchar(15)  							not null primary key,"
                   "Name 				varchar(256),"
                   "URL 				varchar(128),"
                   "Societies           varchar(128),"
                   "SellDay 			date,"
                   "SeriesName 			varchar(128),"
                   "Author				varchar(64),"
                   "Scenario			varchar(64),"
                   "Illustration		varchar(64),"
                   "Music 				varchar(64),"
                   "AgeSpecification 	enum(\"r18\", \"all\", \"r15\", \"unknown\"),"
                   "WorkFormat 			varchar(64),"
                   "FileCapacity 		float,"
                   "Status 				bool 									default false,"
                   "Point 				tinyint);")
    cursor.execute("create table cv(	ID varchar(15),		cv 	varchar(32)	);")
    cursor.execute("create table tag(	ID varchar(15), 	tag varchar(32)	);")
    cursor.close()
    db.close()
    config['first'] = False
    with open('config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f)
    with open(config['data_path'].join('logger.data'), 'w', encoding='utf-8') as file:
        pass

if '__main__' == __name__:
    os.makedirs(config['data_path'], exist_ok=True)
    from bin.get_info import get
    get(config['manager_path'])
