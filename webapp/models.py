#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
from sqlalchemy.ext.hybrid import hybrid_property
from webapp.ext import db
import datetime

# 机场三字码 中文名  英文名
class AirPorts(db.Model):
    """
    机场信息
    """
    __tablename__ = "airports"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    iata = db.Column(db.String(4), unique=True)
    icao = db.Column(db.String(4), default='')
    # 少数城市拥有和机场三至码不一样的城市代码，部分航司查询航线用的是城市码而非三字码，大部分情况下可以混用
    city_iata_code = db.Column(db.String(4), default='')
    c_airport = db.Column(db.String(64), default='')
    e_airport = db.Column(db.String(128), default='')
    c_city = db.Column(db.String(64), default='')
    e_city = db.Column(db.String(64), default='')
    country = db.Column(db.String(32), default='')
    country_iata_code = db.Column(db.String(4), default='')
    timezone = db.Column(db.String(32), default='')
    address = db.Column(db.String(256), default='')
    note = db.Column(db.String(256), default='')
    

# 航线
class AirLines(db.Model):
    """
    所有航司的所有航线信息，主要用于根据航司，国家等条件提取航线
    """
    __tablename__ = "airlines"
    __table_args__ = (db.UniqueConstraint('dep', 'arr', 'carrier', name='unx_airlines'),)
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    dep = db.Column(db.String(4), default='')
    arr = db.Column(db.String(4), default='')
    carrier = db.Column(db.String(4), default='')
    # 状态：0、未启用    1、已启用
    status = db.Column(db.Integer, default=1)
    # 出发到达站点机场所属国家
    dep_country = db.Column(db.String(16), default='')
    arr_country = db.Column(db.String(16), default='')
    def __repr__(self):
        return "[dep: {} - arr: {}]".format(self.dep, self.arr)


# 官网政策
class AirLineFlights(db.Model):
    """
    航司-航线-航班，用于提取AK（或其他航司）所有单程和双程航线信息这种需求
    """
    __tablename__ = "airlineflights"
    __table_args__ = (db.UniqueConstraint('first_dep', 'first_flight_no', 'first_arr', 'second_dep', 'second_flight_no', 'second_arr', name='unx_airline_flights'),)
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_carrier = db.Column(db.String(4), nullable=False)
    first_flight_no = db.Column(db.String(32), nullable=False)
    first_dep = db.Column(db.String(4), nullable=False)
    first_arr = db.Column(db.String(4), nullable=False)
    first_dep_time = db.Column(db.String(32), default='')
    first_arr_time = db.Column(db.String(32), default='')
    # 出发到达站点机场所属国家
    first_dep_country = db.Column(db.String(16), default='')
    first_arr_country = db.Column(db.String(16), default='')
    second_carrier = db.Column(db.String(4), default='')
    second_flight_no = db.Column(db.String(32), default='')
    second_dep = db.Column(db.String(4), default='')
    second_arr = db.Column(db.String(4), default='')
    second_dep_time = db.Column(db.String(32), default='')
    second_arr_time = db.Column(db.String(32), default='')
    second_dep_country = db.Column(db.String(16), default='')
    second_arr_country = db.Column(db.String(16), default='')
    referer = db.Column(db.String(32), default='')

    # 备用
    status = db.Column(db.Integer, default=1)
    last_update = db.Column(db.String(32), default='')
    
    def __repr__(self):
        return "[dep: {} - arr: {}]".format(self.dep, self.arr)



class Flights(db.Model):
    """
    航班信息
    """
    __tablename__ = 'flights'
    __table_args__ = (db.UniqueConstraint('flight_no', 'dep', 'arr', name='unx_flight'), {})
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    carrier = db.Column(db.String(4), default='')
    main_carrier = db.Column(db.String(4), default='')
    flight_no = db.Column(db.String(32), default='')
    main_flight_no = db.Column(db.String(32), default='')
    dep_time = db.Column(db.String(32), default='')
    arr_time = db.Column(db.String(32), default='')
    dep = db.Column(db.String(8), default='')
    arr = db.Column(db.String(8), default='')
    plane_style = db.Column(db.String(16), default='')
    plane_style_name = db.Column(db.String(64), default='')
    dep_country = db.Column(db.String(16), default='')
    arr_country = db.Column(db.String(16), default='')
    last_update = db.Column(db.String(32), default='')


# ip白名单
class Whitelist(db.Model):
    """
    ip白名单设置，用自动化脚本更新到nginx配置，计划废弃，使用阿里云api Gateway管理接口授权和限流
    """
    __tablename__ = 'whitelist'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(64), default='')
    ip = db.Column(db.String(32), default='')
    desription = db.Column(db.String(256), default='')
    expiration = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    created_on = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    # created_on = db.Column(db.TIMESTAMP, server_default = db.func.now())
    

class Carriers(db.Model):
    """
    航司信息
    """
    __tablename__ = "carriers"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    iata = db.Column(db.String(4), unique=True, nullable=False)
    icao = db.Column(db.String(4), default='', nullable=False)
    name = db.Column(db.String(128), default='', nullable=False)
    e_name = db.Column(db.String(128), default='', nullable=False)
    e_country = db.Column(db.String(128), default='', nullable=False)
    country = db.Column(db.String(128), default='', nullable=False)
    country_iata_code = db.Column(db.String(4), default='', nullable=False)
    call_sign = db.Column(db.String(64), default='', nullable=False)
    website = db.Column(db.String(128), default='', nullable=False)
    referer = db.Column(db.String(128), default='', nullable=False)
    note = db.Column(db.String(256), default='', nullable=False)
    

class SpiderAirLines(db.Model):
    """
    记录爬虫所用的队列，爬虫从默认的current取列表初始化抓取
    """
    __tablename__ = 'spiderairlines'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    carrier = db.Column(db.String(4), default='', nullable=False)
    first_list = db.Column(db.Text, nullable=False, default='')
    second_list = db.Column(db.Text, nullable=False, default='')
    third_list = db.Column(db.Text, nullable=False, default='')
    note1 = db.Column(db.Text, default='', nullable=False)
    note2 = db.Column(db.Text, default='', nullable=False)
    note3 = db.Column(db.Text, default='', nullable=False)
    

class ProxyConfig(db.Model):
    """代理配置，提供代理接口供爬虫和校验接口使用"""
    __tablename__ = 'proxy_config'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(128), default='', nullable=False)
    order_no = db.Column(db.String(64), default='', nullable=False)
    secret = db.Column(db.String(64), default='', nullable=False)
    proxy_type = db.Column(db.String(64), default='', nullable=False)
    expired = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    switch = db.Column(db.Integer, default=0, nullable=False)
    note = db.Column(db.Text, default='', nullable=False)
