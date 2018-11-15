#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask_restful.utils import cors
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore
from flask_pymongo import PyMongo
from flask_admin import Admin

api = Api()
api.decorators = [cors.crossdomain(origin='*')]
db = SQLAlchemy()
mongo = PyMongo(None)
security = Security()
app_admin = Admin(name="后台管理", template_mode="bootstrap3")

