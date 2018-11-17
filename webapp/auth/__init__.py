#! -*- coding: utf-8 -*-
from flask import Blueprint
from flask_restful import Api


auth_bp = Blueprint('auth', __name__)
auth = Api(auth_bp)

from . import views

