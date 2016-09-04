#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math
import random
import sys
import logging

import _coordtrans

reload(sys)
sys.setdefaultencoding('utf-8')


def baidu2other(lng, lat, maptype):
    if maptype == u'soso':
        lng, lat = _coordtrans.coordtrans('bd09ll', 'gcj02', float(lng), float(lat))
    elif maptype == u'wgs':
        lng, lat = _coordtrans.coordtrans('bd09ll', 'wgs84', float(lng), float(lat))
    else:
        lng, lat = float(lng), float(lat)

    return lng, lat


def other2baidu(lng, lat, maptype):
    if maptype == u'soso':
        lng, lat = _coordtrans.coordtrans('gcj02', 'bd09ll', float(lng), float(lat))
    elif maptype == u'wgs':
        lng, lat = _coordtrans.coordtrans('wgs84', 'bd09ll', float(lng), float(lat))
    else:
        lng, lat = float(lng), float(lat)

    return lng, lat


def get_distance(lng1, lat1, lng2, lat2):
    PI = 3.14159265358979
    RAD = PI / 180.0
    EARTH_RADIUS = 6378137

    radLat1 = lat1 * RAD
    radLat2 = lat2 * RAD
    a = radLat1 - radLat2
    b = (lng1 - lng2) * RAD
    s = 2 * math.asin(math.sqrt(
            pow(math.sin(a/2), 2) +
            math.cos(radLat1) * math.cos(radLat2) * pow(math.sin(b/2), 2)))
    s = s * EARTH_RADIUS
    return s


def filter_request(area, name, addr, blng, blat, slng, slat):
        if area <= 0 or area == 4:
            return True

        # empty name is invalid
        if len(name.strip()) == 0:
            return True

        # empty lng & lat is ingored by far
        try:
            if any(True for i in (blng, blat, slng, slat) if float(i) <= 5):
                return True
        except:
            pass

        return False


def get_soso_rgeoc_url(slng, slat, iplist, appkey):
    soso_ip = ''
    if len(iplist) > 0:
        soso_ip = random.choice(iplist)
    else:
        logging.error("soso_srv_ip is null")
        return
    # http://apis.map.qq.com/ws/native/location-desc/rgeoc/?lnglat=116.338656,39.99305&parameter={%22user_name%22:%22didi%22,%22app_scene_name%22:%22poi_rewrite%22,%22result_type%22:1}&key=DJYBZ-MKKH5-QXIID-QBJNE-SAKGT-IFBNJ
    params = '&parameter={"user_name":"didi","app_scene_name":"poi_rewrite","accuracy":0,"result_type":1}'
    url = 'http://{}/ws/native/location-desc/rgeoc/?lnglat={},{}&key={}'.format(soso_ip, slng, slat, appkey) + params
    return url


def get_soso_info(soso_data):
    street, ba, district = None, None, None
    try:
        for i in soso_data.get('detail').get('results'):
            dtype = i.get('dtype')
            if (not street) and dtype == 'ST':
                street = i.get('name')
            if (not ba) and dtype == 'FAMOUS_AREA' and i.get('tag') == 'BUSSINESS_AREA':
                ba = i.get('name')
            if (not district) and dtype == 'AD':
                d = i.get('d')
                if not d.endswith(u'旗'):
                    district = d
    except Exception as e:
        logging.error('get_soso_info error: {}'.format(e))
    return street, ba, district


def merge_addr_name(addr, name):
    if not name:
        return addr
    if not addr:
        return name
    if (name == addr) or name.startswith(addr):
        return name
    if addr.endswith(name):
        return addr
    return "{}|{}".format(addr, name)
