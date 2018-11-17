#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import render_template, jsonify
from flask_security import login_required, auth_token_required, current_user
from . import auth_bp


@auth_bp.route('/')
@login_required
def home():
    token = current_user.get_auth_token()
    return jsonify({'authentication_token': token})


@auth_bp.route('/api')
@auth_token_required
def token_protected():
    return 'you\'re logged in by Token!'


