#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

DEBUG = False

BASEDIR = os.path.abspath(os.path.dirname(__file__))

# 数据库配置
# SQLALCHEMY_DATABASE_URI = "postgresql://name:passwd@ip:port/py_api"
SQLALCHEMY_DATABASE_URI = "mysql://name:passwd@ip:port/py_api"

# MongoDB配置
MONGO_URI = "mongodb://name:passwd@ip:port/mongoair"

# redis
REDIS_SERVER = '127.0.0.1'
REDIS_PORT = '6379'
REDIS_DB = 3

# Flask Security Setting
SECRET_KEY = 'super-secret-key'
SECURITY_TRACKABLE = True
SECURITY_REGISTERABLE = True
SECURITY_SEND_REGISTER_EMAIL = False
# SECURITY_PASSWORD_HASH = 'sha512_crypt'
SECURITY_PASSWORD_SALT = 'salt'
# 令牌过期时间
SECURITY_TOKEN_MAX_AGE = 3600 * 1

SECURITY_POST_LOGIN_VIEW = '/admin'
SECURITY_POST_LOGOUT_VIEW = '/login'
SECURITY_RECOVERABLE = True
SECURITY_CHANGEABLE = True
SECURITY_REGISTERABLE = True
SECURITY_CONFIRMABLE = False



# 测试环境设置，正式环境删除local_settings.py文件即可
try:
    from local_setting import *
except ImportError:
    pass
