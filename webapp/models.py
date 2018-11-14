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
    

# 航线
class AirLines(db.Model):
    """
    所有航司的所有航线信息，主要用于根据航司，国家等条件提取航线
    """
    __tablename__ = "airlines"


# 官网政策
class AirLineFlights(db.Model):
    """
    航司-航线-航班，用于提取AK（或其他航司）所有单程和双程航线信息这种需求
    """
    __tablename__ = "airlineflights"



class Flights(db.Model):
    """
    航班信息
    """
    __tablename__ = 'flights'


# ip白名单
class Whitelist(db.Model):
    """
    ip白名单设置，用自动化脚本更新到nginx配置，计划废弃，使用阿里云api Gateway管理接口授权和限流
    """
    __tablename__ = 'whitelist'
    

class Carriers(db.Model):
    """
    航司信息
    """
    __tablename__ = "carriers"
    

class SpiderAirLines(db.Model):
    """
    记录爬虫所用的队列，爬虫从默认的current取列表初始化抓取
    """
    __tablename__ = 'spiderairlines'
    

class ProxyConfig(db.Model):
    """代理配置，提供代理接口供爬虫和校验接口使用"""
    __tablename__ = 'proxy_config'
