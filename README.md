# fofa-dump
Fofa Pro Api 下载工具，通过 api 进行下载数据，将数据保存为 csv 文件。

可自定义配置导出字段名称、每页数量以及批量下载数据。

## 用法

- 环境要求：Python 3

- **使用之前需要配置用户名和密码覆盖 `fofa_name` 和 `fofa_key` 替换为用户自用信息**
- 使用 `pip install -r requirements.txt` 安装依赖

```python
~ python fofa_dump.py
usage: fofa_dump.py [-h] [-q FOFA_SQL] [-r FILE_PATH] [-s SIZE] [-f FIELDS]
                    [-l FULL]

FOFA 数据下载工具

optional arguments:
  -h, --help            show this help message and exit
  -q FOFA_SQL, --fofa_sql FOFA_SQL
                        FOFA 查询语句
  -r FILE_PATH, --file_path FILE_PATH
                        批量查询 FOFA 语句,txt文本
  -s SIZE, --size SIZE  每页数量，默认为 10000
  -f FIELDS, --fields FIELDS
                        字段，默认为ip,host,port,protocol,country,region,city,title,
                        domain,latitude,longitude
  -l FULL, --full FULL  是否为获取历史数据，默认为False
```

## 案例

使用 fofa-dump 进行下载 Solr 数据：

```python
python fofa_dump.py -q 'app="Solr"'
```

