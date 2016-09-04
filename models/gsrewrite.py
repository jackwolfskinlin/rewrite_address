#!/usr/bin/env python
# -*- coding: utf-8 -*-
# All internal text data is stored as unicode, and will be compared by unicode

import re
import utils_helper as utils


class GsRewrite:
    def __init__(self, conf):
        self.conf = conf

    def process(self, area, name, addr, blng, blat, slng, slat, soso_st, soso_ba, soso_district):
        result = {'errno': 1, 'errmsg': 'fail to rewrite'}

        try:
            params = self.convert_param(area, name, addr, blng, blat, slng, slat)
            area, name, addr, blng, blat, slng, slat = (x for x in params)
        except:
            result['errno'] = 2
            return result

        # 非法过滤
        if utils.filter_request(area, name, addr, blng, blat, slng, slat):
            result['errno'] = 3
            return result

        # (name, addr) = self.split_long_name(name, addr) # ignored during small flow testing

        info = {}
        rwtype = self.match(area, name, addr, blng, blat, slng, slat, info, soso_st, soso_ba, soso_district)
        (area, name, addr, blng, blat, slng, slat) = self.fill(rwtype, info, area, name, addr, blng, blat, slng, slat)

        if not self.revert_param(area, name, addr, blng, blat, slng, slat):
            result['errno'] = 4
            return result

        result = {'errno': 0, 'name': name, 'addr': addr, 'lng': blng, 'lat': blat, 'rwtype': rwtype}
        return result

    def match(self, area, name, addr, blng, blat, slng, slat, info, soso_st, soso_ba, soso_district):
        if self.match_white(area, name, addr, blng, blat, slng, slat, info):
            return 1

        # 点击大于阈值
        click_threshold = self.conf.default_click_threshold
        if area in self.conf.click_threshold_by_area:
            click_threshold = self.conf.click_threshold_by_area[area]
        (click, score) = self.get_poi_score_click(area, name)
        if score > 50 or click >= click_threshold:
            return 10

        """
        # name中含有站、桥等字样
        if re.search(u'桥|站|地铁|立交|机场|号线', name):
            return 20
        """

        """
        # name包含商圈名，且与POI在5km范围内
        if area in self.conf.ba:
            for ba_item in self.conf.ba[area]:
                if ba_item[0] in name and 5000 > get_distance(slng, slat, ba_item[1], ba_item[2]):
                    info['ba'] = ba_item[0]
                    return 50
        """

        # name等于区县名
        if name in self.conf.region_list:
            info['region'] = name
            return 60

        # name等于省市名
        if name in self.conf.cities:
            info['city'] = name
            return 70

        # soso_data = utils.get_soso_rgeoc(slng, slat, self.conf.soso_srv_ip, self.conf.soso_srv_appkey, self.conf.soso_timeout)
        # soso_st = utils.get_soso_street(soso_data)
        # # soso_ba = utils.get_soso_ba(soso_data)
        # soso_district = utils.get_soso_district(soso_data)

        # name中已有路、街、道用区改写
        if len(addr) <= 5 and re.search(u'路|街|道', name) and soso_district and soso_district not in name and not any(region in name for region in self.conf.region_list):
            info['district'] = soso_district
            return 75

        """
        # name大于8个字
        if len(re.sub(u'[a-zA-Z0-9()-]', '', name)) > 8:
            return 40

        # 用商圈改写
        if soso_ba:
            info['ba'] = soso_ba
            return 80 if soso_ba in name else 90
        """

        # 没有商圈但有路
        if soso_st and not re.search(u'高速|快速|(一|二|三|四|五|六|七)环', soso_st):
            info['district_street'] = ''
            if soso_district and soso_district not in name and not any(region in name for region in self.conf.region_list):
                info['district_street'] = soso_district

            if soso_st and soso_st not in name:
                info['district_street'] += soso_st

            if len(addr) <= 5:
                return 100

        return -1

    def fill(self, rwtype, info, area, name, addr, blng, blat, slng, slat):
        if rwtype in [10, 60, 70]:
            addr = ""

        if rwtype == 75 and 'district' in info:
            addr = info['district']

        if rwtype == 100 and 'district_street' in info:
            addr = info['district_street']

        # extra short
        if addr in self.conf.cities:
            addr = ""

        addr = re.sub(u'\d+(号|楼|层)*$', '', addr)

        return area, name, addr, blng, blat, slng, slat

    def get_poi_score_click(self, area, name):
        return 0, 0

    def match_white(self, area, name, addr, blng, blat, slng, slat, info):
        return False

    def split_long_name(self, name, addr):
        parts = name.split(u'区')
        if len(parts) != 2 or len(parts[0]) < 1:
            return name, addr

        # 区前一个字不能是下面任一
        if parts[0][-1] in u"小一二三四五六七八九十东南西北中":
            return name, addr

        name = parts[0] + u'区'
        addr = parts[1]

        return name, addr

    def convert_param(self, area, name, addr, blng, blat, slng, slat):
        area = int(area)
        blng, blat = (float(x) for x in (blng, blat))
        slng, slat = (float(x) for x in (slng, slat))
        # name和addr已经是unicode(ucs-2)
        return area, name, addr, blng, blat, slng, slat

    def revert_param(self, area, name, addr, blng, blat, slng, slat):
        try:
            name = name.encode('utf-8')
            addr = addr.encode('utf-8')
            return True
        except:
            return False
