#!/usr/bin/env python
# -*- coding: utf-8 -*-
from gevent import monkey
import gevent
from lxml import etree
import time
import sys
import hashlib
import re
import requests
from pymongo import MongoClient
from flask import request, jsonify, current_app
from . import sc_verify_api_bp
from datetime import datetime, timedelta
import logging
monkey.patch_all()
logger = logging.getLogger('flask.app')
# client = MongoClient('mongodb://192.168.1.140:27020/')  # 本地测试
client = MongoClient('mongodb://ip:port/')
db = client.mongoair
db.authenticate('name', 'passwd')


@sc_verify_api_bp.route('sc')
def sc_verify():
    start = time.time()
    context = {}
    dep = request.args.get('dep', '')
    arr = request.args.get('arr', '')
    date = request.args.get('date', '')
    flight_no_query = request.args.get('flight_no', '')
    # 双程航班或单程航班
    flight_no_query = flight_no_query.split('/') if flight_no_query else ''
    current_app.logger.debug('Arguments: {}-{}-{}-{}'.format(dep, arr, date, flight_no_query))
    if not (dep and arr and date and flight_no_query):
        result = {
            'message': 'error arguments',
            'code': '1004',
            'data': ''
        }
        return jsonify(result)
    url = 'http://sc.travelsky.com/scet/queryAvInternational.do'
    # 并发爬虫数
    for i in range(3):
        time.sleep(0.2)
        gevent.spawn(get_html, url, dep, arr, date, flight_no_query, context)
    while not context:
        if 6 < time.time() - start <= 7:
            # 备用内部代理追加请求
            # gevent.spawn(get_html, url, dep, arr, date, flight_no_query, context, flag=1)
            gevent.spawn(get_html, url, dep, arr, date, flight_no_query, context)
        elif time.time() - start >= 13:
            break
        gevent.sleep(1)
        # current_app.logger.debug('等待1秒')
    if context.get('save'):
        res_result = context.get('save')
    else:
        res_result = {
            'code': '2002',
            'message': 'Time out',
            'data': ''
        }
    current_app.logger.debug('返回页面')
    return jsonify(res_result)


def get_html(url, dep, arr, date, flight_no_query, context, flag=0):
    result = {}
    logger.debug('开始获取html({})'.format(flag))
    # proxies = get_proxy(flag)

    headers = {
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
        'Origin': 'http://sc.travelsky.com',
        'Upgrade-Insecure-Requests': '1',
        'DNT': '1',
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Referer': 'http://sc.travelsky.com/scet/queryAvInternational.do',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9'
    }
    data = {
        'countrytype': '1',
        'usefor': '1',
        'travelType': '0',
        'cityNameOrg': '',  # '%BC%C3%C4%CF',
        'cityCodeOrg': dep,  # 'TNA',
        'cityNameDes': '',  # '%BD%F0%B1%DF',
        'cityCodeDes': arr,  # 'PNH',
        'takeoffDate': date,  # '2018-10-31',
        'returnDate': ''
    }
    # 第三方代理加入头验证
    # if flag == 0:
    #     headers.update({
    #         'Proxy-Authorization': get_auth()
    #     })

    try:
        # 备用内部代理
        # r = requests.post(url, headers=headers, data=data, proxies=proxies, timeout=12, verify=False, allow_redirects=False)
        r = requests.post(url, headers=headers, data=data, timeout=12, verify=False, allow_redirects=False)
        # logger.debug(data)
    except TimeoutError as e:
        logger.debug('超时 {}'.format(e))
    except Exception as e:
        logger.debug('发生了未知异常\n{}'.format(e))
        # ---- #
    else:
        # 明确空航班 - 1
        if '很抱歉，没有符合条件的查询结果' in r.text:
            # 更新数据库
            push_mongo(dep, arr, date)
            logger.debug('空航班')
            result.update({
                'message': 'ok',
                'code': '1102',
                'data': ''
            })
        # 明确没有航线 - 2
        elif '操作失败' in r.text:
            # 更新数据库
            # push_mongo(dep, arr, date)
            logger.debug('没有航线')
            result.update({
                'message': 'ok',
                'code': '1102',
                'data': ''
            })
        elif '对不起，由于查询过于频繁，请稍后重试' in r.text or '访问受限，需要帮助请拨打山航客服热线95369' in r.text:
            logger.debug("过于频繁，已封IP")
        # else:
        #     logger.debug(r.text)
        #     logger.debug("抓取异常")
        else:
            html = etree.HTML(r.text)
            data = fetch_data(html)
            if data:
                # 数据入库
                push_mongo(dep, arr, date, data)
                logger.debug('抓取到数据')
                for flight_item in data:
                    flight_no = flight_item.get('flight_no').split('/')
                    flag = False
                    # 筛选航班
                    for i in flight_no_query:
                        if i not in flight_no:
                            flag = True
                            break
                    if flag or len(flight_no_query) != len(flight_no):
                        continue
                    cabin = sorted(flight_item['cabin_infolist'], key=lambda k: float(k['price']))[0]
                    # 明确当天有校验的航班号 - 2
                    result = {
                        'code': '1111',
                        'message': 'ok',
                        'data': {
                            'status': True,
                            'price': cabin['price'],
                            'base_price': cabin['base_price'],
                            'tax_fees': cabin['tax_fees'],
                            'currency': cabin['currency'],
                            'ticket_remain': cabin['ticket_remain']
                        }
                    }
                if not result:
                    # 明确当天航班中没有校验的航班号 - 3
                    result.update({
                        'code': '1102',
                        'message': 'ok',
                        'data': ''
                    })
            else:
                logger.debug('未知异常 - {}'.format(r.text))
    if not context.get('save') and result:
        context['save'] = result
        logger.debug('获取到了结果 {}'.format(context))


def fetch_data(html):
    data = []
    flight_list = html.xpath('.//td[@class="pd-sx airplane-prise-info"]')
    for flight_item in flight_list:
        flight_info = {
            'carrier': '',
            'flight_no': '',
            'dep': '',
            'arr': '',
            'plane_style': '',
            'depdate': '',
            'deptime': '',
            'arrdate': '',
            'arrtime': '',
            'main_flight_no': '',
            'cabin_infolist': []
        }
        input_taglist = flight_item.xpath(".//input[@name='select0']")
        price_list = flight_item.xpath(".//span[@class='flow0_chaxun_tab06_list06']")
        for input_tag, price_cur in zip(input_taglist, price_list):
            price = price_cur.xpath('./text()')[0][1:]
            currency = price_cur.xpath('./sup/text()')[0]
            value_list = input_tag.get('value').split(',')
            carrier = value_list[0]
            flight_no = carrier + value_list[1]
            dep = value_list[2]
            arr = value_list[3]
            # 航班经过的城市数量（包括出发地/目的地）
            # over_flag = value_list[4]
            dep_datetime = value_list[5]
            depdate, deptime = dep_datetime.split()
            arr_datetime = value_list[6]
            arrdate, arrtime = arr_datetime.split()
            plane_style = value_list[7]
            cabin_tic = value_list[-1].split('@')
            cabin = cabin_tic[2]
            ticket_remain = cabin_tic[3]
            if ticket_remain == 'A':
                ticket_remain = '99'
            if not flight_info.get('carrier'):
                print('dict')
                flight_info.update({
                    'carrier': carrier,
                    'flight_no': flight_no,
                    'plane_style': plane_style,
                    'dep': dep,
                    'depdate': depdate,
                    'deptime': deptime,
                    'arr': arr,
                    'arrdate': arrdate,
                    'arrtime': arrtime
                })
            flight_info['cabin_infolist'].append({
                'cabin': cabin,
                'cabin_type': '',
                'price': price,  # 总售价 float string
                'base_price': '',  # 不含税价
                'surcharges_adt': '',  # 附加费
                'tax_adt': '',  # 税
                'ticket_remain': ticket_remain,  # 余票数
                'tax_fees': '',  # 税费总额
                'currency': currency,  # 币种
            })
        data.append(flight_info)
    return data

# def get_proxy(flag=0):  # 代理类型，非0：自己的代理；0：第三方代理
#     if flag == 0:
#         ip = ''
#         port = ''
#         proxies = {
#             'http': 'http://' + ip + ':' + port,
#             'https': 'https://' + ip + ':' + port,
#         }
#     else:
#         proxies = {
#             'http': 'http://ip:port',
#             'https': 'http://ip:port'
#         }
#     return proxies


def push_mongo(dep, arr, date, data=None, data2=None):
    sc_data = db.scair.find({'dep': dep, 'arr': arr, 'date': date, 'update': {
        '$gte': datetime.utcnow() + timedelta(hours=8) - timedelta(minutes=30)
    }})
    sc_data = list(sc_data)
    if sc_data:
        re_data = sc_data[0]
        re_data.update({
            'data': data if data else [],
            'data2': data2 if data2 else [],
            'code': '1111' if data or data2 else '9999',
            'message': 'ok' if data or data2 else '当天没有航班',
            "update": datetime.utcnow() + timedelta(hours=8)
        })
        db.scair.update({'_id': re_data.get('_id')}, re_data)
    else:
        db.scair.insert({
            # 根据该任务抓取优先级判断航线类型
            "airline_country_type": "",
            "carrier": "sc",
            "dep": dep,
            "arr": arr,
            "date": date,
            "data": data if data else [],
            "data2": data2 if data2 else [],
            "message": "ok" if data or data2 else '当天没有航班',
            "code": "1111" if data or data2 else '9999',
            "update": datetime.utcnow() + timedelta(hours=8)
        })


# def get_auth():
#     _version = sys.version_info
#     is_python3 = (_version[0] == 3)
#     orderno = '****'
#     secret = '****'
#     timestamp = str(int(time.time()))
#     string = "orderno=" + orderno + "," + "secret=" + secret + "," + "timestamp=" + timestamp
#     if is_python3:
#         string = string.encode()
#     md5_string = hashlib.md5(string).hexdigest()
#     sign = md5_string.upper()
#     auth = "sign=" + sign + "&" + "orderno=" + orderno + "&" + "timestamp=" + timestamp
#     return auth

