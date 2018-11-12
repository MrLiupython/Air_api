#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask_script import Manager, Shell
from flask_migrate import MigrateCommand, Migrate
from webapp import create_app
from webapp.ext import db
from webapp.models import AirPorts, AirLines, Flights, Whitelist, AirLineFlights, Carriers, SpiderAirLines, ProxyConfig
from webapp.auth.models import Role, User, RolesUsers

# 初始化app
app = create_app()

# 初始化命令行扩展
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    return dict(app=app, db=db, AirPort=AirPorts, AirLines=AirLines, Role=Role, User=User, RolesUsers=RolesUsers, MainlandFlight=Flights, Whitelist=Whitelist, AirLineFlights=AirLineFlights, Carriers=Carriers, SpiderAirLines=SpiderAirLines, ProxyConfig=ProxyConfig)


manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
