#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
自定义异常
"""
from flask import jsonify


class APIException(Exception):
    status_code = 200
    
    def __init__(self, message, code, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        self.code = code
        self.payload = payload
        if status_code is not None:
            self.status_code = status_code
        
    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        rv['code'] = self.code
        return rv


def handle_api_exception(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response
