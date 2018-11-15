#! /usr/bin/env python
# -*- coding:utf-8 -*-

from flask import Blueprint

sc_verify_api_bp = Blueprint('sc_verify_api_bp', __name__)
from . import views
