#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/02/28
# @Author  : r4v3zn
import sys
import requests
import sys
import time
import json
import base64
import traceback
import os
import argparse
import csv
# 禁用安全请求警告
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
import coloredlogs,logging
logger = logging.getLogger(os.path.basename(__file__))
coloredlogs.install(level='INFO',milliseconds=True,fmt='[%(asctime)s] :%(levelname)s: %(message)s')
import datx
c = datx.City('mydata4vipday3.datx')
# FOFA 用户名
fofa_name = ''
# FOFA 用户key
fofa_key = ''
session = requests.session()
# 请求头
headers = {
    'Upgrade-Insecure-Requests': '1',
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36'
}

'''
提取ip位置信息
@param ip ip
'''
def get_ip_info(ip):
    try:
        ip_info = c.find(ip)
        country_name = ip_info[0]
        region_name = ip_info[1]
        city_name = ip_info[2]
        isp_domain = ip_info[4]
    except Exception as e:
        return [ip,'','','','']
    return [ip,country_name,region_name,city_name,isp_domain]

'''
请求中心，控制程序所有HTTP请求，如果请求发生错误进行尝试再次连接
@param url 请求连接
@return 请求响应结果
'''
def fofa_requests(url):
    rs_content = ''
    error_content = ''
    while True:
        try:
            logger.debug(url)
            rs = session.get(url, verify=False,headers=headers)
            rs_text = rs.text
            error_content = rs_text
            results = json.loads(rs_text)
            error = results['error']
            if error:
                errmsg = results['errmsg']
                if '401 Unauthorized' in errmsg:
                    info = u'fofa 错误: 用户名或API 无效！'
                    logger.error(info)
                    break
                else:
                    info = u'fofa 错误:'+errmsg+u' 休眠30s'
                    logger.error(info)
                    time.sleep(30)
            else:
                rs_content = results
                break
        except Exception as e:
            logger.error(error_content)
            logger.error(u'fofa 错误:'+str(e.message)+u' 休眠30s')
            time.sleep(30)
    return rs_content

'''
文件存储
:param fields_list 字段名称
:param data_list 数据内容信息
:param csv_writer csv对象
:param fofa_sql fofa查询语句
'''
def save_file(fields_list,data_list,csv_writer,fofa_sql):
    ip_index = -1
    country_index = -1
    region_index = -1
    city_index = -1
    for index,field_name in enumerate(fields_list):
        if 'ip' == field_name and ip_index == -1:
            ip_index = index
        elif 'country' == field_name and country_index == -1:
            country_index = index
        elif 'region' == field_name and region_index == -1:
            region_index = index
        elif 'city' == field_name and city_index == -1:
            city_index = index
    if ip_index == -1:
        return
    for data in data_list:
        if str == type(data):
            tmp_data = [data]
        else:
            tmp_data = data
        ip = data[ip_index]
        ip_info = get_ip_info(ip)
        if country_index != -1:
            tmp_data[country_index] = ip_info[1]
        if region_index != -1:
            tmp_data[region_index] = ip_info[2]
        if city_index != -1:
            tmp_data[city_index] = ip_info[3]
        tmp_data.append(fofa_sql)
        if len(tmp_data) > 0:
            csv_writer.writerow(tmp_data)

'''
FOFA 数据内容保存
:param fofa_sql fofa查询语句
:param fields_list 字段名称
:param page_size 每页数量
:param full 是否为历史所有数据
:param csv_writer csv对象
'''
def dump_fofa_data(fofa_sql,fields_list,page_size,full,csv_writer):
    current_page = 1
    total_page = 1
    total_size = 0
    while current_page <= total_page:
        base64_str = base64.b64encode(fofa_sql.encode())
        api_url = 'http://fofa.so/api/v1/search/all?email=%s&key=%s&fields=%s&size=%s&page=%s&qbase64=%s&full=%s'%(fofa_name,fofa_key,','.join(fields_list),str(page_size),str(current_page),str(base64_str)[2:-1],str(full))
        rs = fofa_requests(api_url)
        if not rs:
            break
        total_size = rs['size']
        results = rs['results']
        total_page = int(total_size / page_size) + 1 if total_size % page_size != 0 else int(total_size / page_size)
        save_file(fields_list=fields_list,data_list=results,csv_writer=csv_writer,fofa_sql=fofa_sql)
        logger.info('dump data fofa sql --> %s ,page --> %s/%s status --> ok'%(fofa_sql,current_page,total_page))
        current_page += 1

'''
FOFA 数据内容保存
:param fofa_sql fofa查询语句
:param fields_list 字段名称
:param page_size 每页数量
:param full 是否为历史所有数据
'''
def dump_main(fofa_sql_list,fields,page_size,full=False):
    split_fields = list(fields.split(','))
    fields_list = []
    for field in split_fields:
        if field in fields_list:
            continue
        fields_list.append(field)
    fields_list.append('fofa_sql')
    if 'ip' not in fields_list:
        fields_list.insert(0,'ip')
        fields = ','.join(fields_list)
    csv_file_name = '%s.csv'%(time.strftime('%Y%m%d%H%M%S',time.localtime(time.time())),)
    logger.info('file save name --> %s'%(csv_file_name))
    logger.info('dump data fields --> [%s] ,page size --> %s'%(fields,page_size))
    csv_file = open(csv_file_name,'w',newline='')
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(fields_list)
    for fofa_sql in fofa_sql_list:
        logger.info('start dump data fofa sql --> %s '%(fofa_sql))
        dump_fofa_data(fofa_sql=fofa_sql,fields_list=fields_list,page_size=page_size,full=full,csv_writer=csv_writer)
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='FOFA 数据下载工具')
    parser.add_argument('-q','--fofa_sql',help='FOFA 查询语句')
    parser.add_argument('-r','--file_path',help='批量查询 FOFA 语句,txt文本')
    parser.add_argument('-s','--size', help='每页数量，默认为 10000', type=int, default=10000)
    parser.add_argument('-f','--fields', help='字段，默认为ip,host,port,protocol,country,region,city,title,domain,latitude,longitude',default='ip,host,port,protocol,country,region,city,title,domain,latitude,longitude')
    parser.add_argument('-l','--full', help='是否为获取历史数据，默认为False',default='false')
    args = parser.parse_args()
    fofa_sql = args.fofa_sql
    fields = args.fields
    file_path = args.file_path
    page_size = args.size
    full = str(args.full)
    if not file_path and not fofa_sql:
        parser.print_help()
        sys.exit(1)
    fofa_sql_list = []
    if fofa_sql:
        fofa_sql_list.append(fofa_sql)
    elif file_path:
        with open(file_path,'r') as f:
            for fofa_sql in f.readlines():
                fofa_sql = fofa_sql.strip()
                fofa_sql_list.append(fofa_sql)
    dump_main(fofa_sql_list=fofa_sql_list,fields=fields,full=full,page_size=page_size)


