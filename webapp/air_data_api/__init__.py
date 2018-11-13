#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Blueprint
from flask_restful import Api


air_data_v1_bp = Blueprint('airlines_v1', __name__)
air_data_v1 = Api(air_data_v1_bp)

from . import views
