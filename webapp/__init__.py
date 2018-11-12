#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask, g
from .ext import api, db, mongo, security, app_admin
from .auth.models import user_datastore, User, Role
from .models import AirPorts, AirLines, Whitelist, Flights, AirLineFlights, Carriers, SpiderAirLines, ProxyConfig
from .decorators import get_view_rate_limit


def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')
    # 配置
    app.config.from_object('config')
    # 初始化扩展
    api.init_app(app)
    db.init_app(app)
    mongo.init_app(app)
    security.init_app(app, datastore=user_datastore)
    app_admin.init_app(app)
    if not app.debug:
        import os
        import logging
        from logging import Formatter
        from logging.handlers import RotatingFileHandler
        file_handler = RotatingFileHandler(
            # os.path.abspath(os.path.join(app.config.get('BASEDIR'), 'logs/webapp.log')),
            os.path.abspath(os.path.join('/tmp/', 'api_air_webapp.log')),
            maxBytes=10000000,
            backupCount=10,
            encoding='utf8'
        )
        file_handler.setFormatter(Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.DEBUG)
        app.logger.addHandler(file_handler)
    
    from .errors import handle_api_exception, APIException
    app.register_error_handler(APIException, handle_api_exception)
    
    # 蓝图注册
    from .auth import auth, auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    from .air_general_api import air_general_api_v1, air_general_api_v1_bp
    app.register_blueprint(air_general_api_v1_bp, url_prefix='/api')
    
    from .air_data_api import air_data_v1, air_data_v1_bp
    app.register_blueprint(air_data_v1_bp, url_prefix='/api/sp')

    from .whitelist import whitelist_v1, whitelist_v1_bp
    app.register_blueprint(whitelist_v1_bp, url_prefix='/api/sp')
    
    from .air_batch_api import air_batch_api_v1, air_batch_api_v1_bp
    app.register_blueprint(air_batch_api_v1_bp, url_prefix='/api')

    from webapp.webadmin.views import UserView, RoleView, MyModelView, AirPortView, AirlinesView, WhitelistView, \
        FlightsView, NotAuthenticatedMenuLink, AuthenticatedMenuLink, AirlineFlightsView, CarriersView, \
        SpiderAirLinesView, ProxyConfigView
    app_admin.add_view(RoleView(Role, db.session, name='用户组管理', endpoint='role', category="系统配置"))
    app_admin.add_view(UserView(User, db.session, name='用户管理', endpoint='user', category="系统配置"))
    app_admin.add_view(AirPortView(AirPorts, db.session, name='机场管理', endpoint='airport', category="基础数据"))
    app_admin.add_view(AirlinesView(AirLines, db.session, name='航线管理', endpoint='airlines', category="基础数据"))
    app_admin.add_view(FlightsView(Flights, db.session, name='国内航班管理', endpoint='flight', category="基础数据"))
    app_admin.add_view(AirlineFlightsView(AirLineFlights, db.session, name='官网政策管理', endpoint='airlineflights', category="基础数据"))
    app_admin.add_view(CarriersView(Carriers, db.session, name='航司管理', endpoint='carriers', category="基础数据"))
    app_admin.add_view(SpiderAirLinesView(SpiderAirLines, db.session, name='爬虫线路管理', endpoint='爬虫'))
    # 废弃，如果需要白名单，使用阿里云或者类似的Api Gateway更合适
    # app_admin.add_view(WhitelistView(Whitelist, db.session, name='白名单管理', endpoint='系统配置'))
    app_admin.add_view(ProxyConfigView(ProxyConfig, db.session, name='代理ip管理', endpoint='proxy', category="系统配置"))
    
    from webapp.webadmin.views_show import DataExportView, CarrierListView, SpiderDataCountView
    app_admin.add_view(CarrierListView(name='航司航班统计', endpoint='carrierlist', category="基础数据"))
    app_admin.add_view(SpiderDataCountView(name='爬虫数据统计', endpoint='spidercount', category="基础数据"))
    app_admin.add_view(DataExportView(name='价格数据导出', endpoint='dataexport'))
    
    app_admin.add_link(NotAuthenticatedMenuLink(name='login', endpoint='security.login'))
    app_admin.add_link(AuthenticatedMenuLink(name='logout', endpoint='security.logout'))
    
    # Create a user to test with
    # @app.before_first_request
    # def create_roles():
    #     try:
    #         db.create_all()
    #         r = user_datastore.create_role(id=1, name='superuser', description='超级管理员')
    #         u = user_datastore.create_user(id=1, email='', password='')
    #         user_datastore.create_role(id=2, name='manager', description='普通后台用户')
    #         user_datastore.create_role(id=3, name='user', description='普通前台用户')
    #         user_datastore.add_role_to_user(u, r)
    #         db.session.commit()
    #     except:
    #         pass

    @app.after_request
    def inject_x_rate_headers(response):
        limit = get_view_rate_limit()
        if limit and limit.send_x_headers:
            h = response.headers
            h.add('X-RateLimit-Remaining', str(limit.remaining))
            h.add('X-RateLimit-Limit', str(limit.limit))
            h.add('X-RateLimit-Reset', str(limit.reset))
        return response
            
    return app
