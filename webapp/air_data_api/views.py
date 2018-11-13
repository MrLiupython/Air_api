#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import request
from flask_restful import Resource, abort

from ..models import AirPorts, AirLines, Flights
from . import air_data_v1
from sqlalchemy import or_, and_


class AirPortApi(Resource):
    def get(self):
        code = request.args.get("code", "")
        all = request.args.get("all", "0")
        result = {
            'data': '',
            'code': '',
            'message': ''
        }
        if all is "1":
            # all参数为"1"返回所有机场
            data = []
            airport_list = AirPorts.query.all()
            for ap in airport_list:
                ap_data = {
                    "iata": ap.iata,
                    "icao": ap.icao,
                    "city_iata_code": ap.city_iata_code,
                    "c_airport": ap.c_airport,
                    "e_airport": ap.e_airport,
                    "c_city": ap.c_city,
                    "e_city": ap.e_city,
                    "country": ap.country,
                    "country_iata_code": ap.country_iata_code,
                }
                data.append(ap_data)
            result.update({
                'data': data,
                'code': '1111',
                'message': '一共有{}个机场'.format(len(data))
            })
        elif len(code) != 3:
            # TODO: 机场三字码非法，非法筛选待完善
            result.update({
                'data': '',
                'code': '1004',
                'message': '机场代码非法'
            })
        else:
            ap = AirPorts.query.filter_by(iata=code).first()
            if not ap:
                result.update({
                    'data': {},
                    'code': '1001',
                    'message': '未查询到机场信息'
                })
            else:
                ap_data = {
                    "iata": ap.iata,
                    "icao": ap.icao,
                    "city_iata_code": ap.city_iata_code,
                    "c_airport": ap.c_airport,
                    "e_airport": ap.e_airport,
                    "c_city": ap.c_city,
                    "e_city": ap.e_city,
                    "country": ap.country,
                    "country_iata_code": ap.country_iata_code,
                }
                result = {
                    'data': ap_data,
                    'code': '1111',
                    'message': '{}机场的信息'.format(code)
                }
                
        return result


class FlightApi(Resource):
    def get(self):
        dep = request.args.get('dep', '')
        arr = request.args.get('arr', '')
        flight_no = request.args.get('flight_no', '')
        result = {
            'data': '',
            'code': '',
            'message': ''
        }
        if not (dep and arr and flight_no):
            return {
                'data': '',
                'code': '1004',
                'message': 'Lack Argument'
            }
        
        item = Flights.query.filter_by(flight_no=flight_no, dep=dep, arr=arr).first()
        
        if not item:
            # 这里去查询下航线库，看是航线不在库中，还是这个日期没有开始被抓取
            verify_airline = AirLines.query.filter_by(dep=dep, arr=arr).first()
            if not verify_airline:
                result.update({
                    "message": "该航线不在库中，请联系管理员添加",
                    "code": "1000"
                })
            else:
                result.update({
                    "message": "未找到该航班信息",
                    "code": "1001"
                })
        else:
            item2 = Flights.query.filter_by(main_flight_no=flight_no, dep=dep, arr=arr).all()
            shared = []
            if item2:
                for shared_item in item2:
                    shared.append(shared_item.flight_no)
            result.update({
                "message": "ok",
                "code": "1111",
                "data": {
                    "carrier": item.carrier,
                    "flight_no": item.flight_no,
                    "dep": item.dep,
                    "arr": item.arr,
                    "dep_time": item.dep_time,
                    "arr_time": item.arr_time,
                    "plane_style": item.plane_style,
                    "plane_style_name": item.plane_style_name,
                    "main_carrier": item.main_carrier,
                    "main_flight_no": item.main_flight_no,
                    "dep_country": item.dep_country,
                    "arr_country": item.arr_country,
                    "last_update": item.last_update,
                    "shared": shared
                }
            })
        return result


# 根据多种条件查询航线
class AirLinesApi(Resource):
    def get(self):
        tm = {}
        tm['carrier'] = request.args.get("carrier", "")
        tm['dep'] = request.args.get("dep", "")
        tm['arr'] = request.args.get("arr", "")
        tm['dep_country'] = request.args.get("dep_country", "")
        tm['arr_country'] = request.args.get("arr_country", "")
        tm['status'] = request.args.get('status', '')
        kw = {k: v for k, v in tm.items() if v}
        
        result = {
            "message": "failure",
            "carrier": kw.get('carrier', ''),
            "dep": kw.get('dep', ''),
            "arr": kw.get('arr', ''),
            "dep_country": kw.get('dep_country', ''),
            "arr_country": kw.get('arr_country', ''),
            "data": [],
            'code': '0000'
        }
        
        if not kw:
            result.update({
                'code': '1004',
                'message': '有效的查询参数为空，请提供正确的参数'
            })
        else:
            lines = AirLines.query.filter_by(**kw).all()
            if not lines:
                result.update({
                    "message": "未查询到航线,请检查参数 如有疑问，其联系管理员",
                    "code": "1001",
                })
            else:
                lines_list = list(set([i.dep + '-' + i.arr for i in lines]))
                result.update({
                    "message": "success",
                    "data": lines_list,
                    'code': '1111'
                })
        
        return result


# 根据航线类型查询航线
class AirlinesCountryType(Resource):
    def get(self):
        line_list = []
        carrier = request.args.get('carrier', '')
        status = request.args.get('status', '')
        try:
            airlines_country_type = int(request.args.get('ac_type'))
            message = 'success'
        except (ValueError, TypeError):
            message = 'error country type value type'
            country_type = ''
        else:
            # 1: 大陆  2. 海外 - 大陆  大陆-海外 3. 海外-海外
            if airlines_country_type == 1:
                lines = AirLines.query.filter_by(dep_country='中国', arr_country='中国').all()
                country_type = '大陆-大陆'
            elif airlines_country_type == 2:
                lines = AirLines.query.filter(or_(and_(AirLines.dep_country == '中国', AirLines.arr_country != '中国'), and_(AirLines.dep_country != '中国', AirLines.arr_country == '中国'))).all()
                country_type = '大陆-海外，海外-大陆'
            elif airlines_country_type == 3:
                lines = AirLines.query.filter(AirLines.dep_country != '中国', AirLines.arr_country != '中国').all()
                country_type = '海外-海外'
            elif airlines_country_type == 0:
                lines = AirLines.query.all()
                country_type = '所有航线'
            else:
                lines = []
                country_type = 'error country type value'
            if carrier:
                # status状态，状态0过滤一些空线路或者航班数量很少的线路，状态1为默认值，不带status返回全部航线数据
                if not status:
                    line_list = list(set([i.dep + '-' + i.arr for i in lines if i.carrier == carrier]))
                else:
                    line_list = list(set([i.dep + '-' + i.arr for i in lines if i.carrier == carrier and i.status == int(status)]))
            else:
                line_list = list(set([i.dep + '-' + i.arr for i in lines]))

        result = {
            "message": message,
            "country_type": country_type,
            "data": line_list
        }
        return result
    

air_data_v1.add_resource(AirPortApi, "/airport")
air_data_v1.add_resource(FlightApi, "/flight")
air_data_v1.add_resource(AirLinesApi, "/airlines")
air_data_v1.add_resource(AirlinesCountryType, "/airlines_country")
