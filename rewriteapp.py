#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import json

import tornado.ioloop
import tornado.web
import tornado.gen
import tornado.options as opt
import tornado.httpserver
import tornado.httpclient

import config
from models.rewrite import Rewrite
from models.gsrewrite import GsRewrite
from models import utils_helper as utils
from models import log_helper as log

reload(sys)
sys.setdefaultencoding('utf-8')

# 配置命令行参数
opt.define("port", default=23333, help="run on the given port", type=int)

didi_logger = log.didiLog()
g_cfg = config.g_cfg
taxi_rewrite = Rewrite(g_cfg)
gs_rewrite = GsRewrite(g_cfg)
g_err_msg = {"errno": 1, "errmsg": u"必要参数缺失"}


class GsRewriteHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        area = self.get_argument('area', default=None)
        name = self.get_argument('name', default=None)
        addr = self.get_argument('addr', default=None)
        lng = self.get_argument('lng', default=None)
        lat = self.get_argument('lat', default=None)
        orderid = self.get_argument('orderid', default=0)
        maptype = self.get_argument('maptype', default='baidu')

        if not all([area, name, addr, lng, lat, maptype]):
            self.write(g_err_msg)
            return

        if lng and lat:
            if maptype == 'soso':
                slng, slat = float(lng), float(lat)
                blng, blat = utils.other2baidu(slng, slat, maptype)
            elif maptype == 'baidu':
                blng, blat = float(lng), float(lat)
                slng, slat = utils.baidu2other(blng, blat, 'soso')
            else:
                blng, blat = utils.other2baidu(lng, lat, maptype)
                slng, slat = utils.baidu2other(blng, blat, 'soso')

        soso_url = utils.get_soso_rgeoc_url(slng, slat, g_cfg.soso_srv_ip, g_cfg.soso_srv_appkey)
        client = tornado.httpclient.AsyncHTTPClient()
        soso_st, soso_ba, soso_district = None, None, None
        try:
            resp = yield client.fetch(
                soso_url, connect_timeout=g_cfg.soso_conn_timeout, request_timeout=g_cfg.soso_timeout)
            if resp.code == 200:
                soso_data = json.loads(resp.body.decode('gb18030'))
                soso_st, soso_ba, soso_district = utils.get_soso_info(soso_data)
                # print soso_url, soso_st, soso_ba, soso_district
            else:
                didi_logger.didi_error.error("soso_rgeo response status error, url: {}, status: {}".format(
                    soso_url, resp.code))
        except Exception as e:
            didi_logger.didi_error.error("soso_rgeo requst error, url: {}, error: {}".format(soso_url, e))
        res_obj = gs_rewrite.process(area, name, addr, blng, blat, slng, slat, soso_st, soso_ba, soso_district)

        if res_obj.get('errno', -1) == 0:
            res_obj['lng'], res_obj['lat'] = utils.baidu2other(res_obj['lng'], res_obj['lat'], maptype)
            res_obj['addrname'] = utils.merge_addr_name(res_obj.get('addr'), res_obj.get('name'))
        self.write(res_obj)
        log.writePublicLog(didi_logger, "gsrewrite", res_obj, name, addr, lng, lat, maptype, orderid, area)
        self.finish()


class TaxiRewriteHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        area = self.get_argument('area', default=None)
        name = self.get_argument('name', default=None)
        addr = self.get_argument('addr', default=None)
        blng = self.get_argument('blng', default=None)
        blat = self.get_argument('blat', default=None)
        slng = self.get_argument('slng', default=None)
        slat = self.get_argument('slat', default=None)
        lng = self.get_argument('lng', default=None)
        lat = self.get_argument('lat', default=None)
        orderid = self.get_argument('orderid', default=0)
        maptype = self.get_argument('maptype', default='baidu')

        if lng and lat:
            if maptype == 'soso':
                slng, slat = float(lng), float(lat)
                blng, blat = utils.other2baidu(slng, slat, maptype)
            elif maptype == 'baidu':
                blng, blat = float(lng), float(lat)
                slng, slat = utils.baidu2other(blng, blat, 'soso')
            else:
                blng, blat = utils.other2baidu(lng, lat, maptype)
                slng, slat = utils.baidu2other(blng, blat, 'soso')

        if not all([area, name, addr, blng, blat, slng, slat]):
            self.write(g_err_msg)
            return

        soso_url = utils.get_soso_rgeoc_url(slng, slat, g_cfg.soso_srv_ip, g_cfg.soso_srv_appkey)
        client = tornado.httpclient.AsyncHTTPClient()
        soso_st, soso_ba, soso_district = None, None, None
        try:
            resp = yield client.fetch(
                soso_url, connect_timeout=g_cfg.soso_conn_timeout, request_timeout=g_cfg.soso_timeout)
            if resp.code == 200:
                soso_data = json.loads(resp.body.decode('gb18030'))
                soso_st, soso_ba, soso_district = utils.get_soso_info(soso_data)
                # print soso_url, soso_st, soso_ba, soso_district
            else:
                didi_logger.didi_error.error("soso_rgeo response status error, url: {}, status: {}".format(
                    soso_url, resp.code))
        except Exception as e:
            didi_logger.didi_error.error("soso_rgeo requst error, url: {}, error: {}".format(soso_url, e))
        res_obj = taxi_rewrite.process(area, name, addr, blng, blat, slng, slat, soso_st, soso_ba, soso_district)

        if res_obj.get('errno', -1) == 0:
            res_obj['lng'], res_obj['lat'] = utils.baidu2other(res_obj['lng'], res_obj['lat'], maptype)
            res_obj['addrname'] = utils.merge_addr_name(res_obj.get('addr'), res_obj.get('name'))
        self.write(res_obj)
        log.writePublicLog(didi_logger, "taxirewrite", res_obj, name, addr, lng, lat, maptype, orderid, area)
        self.finish()


def make_app():
    app = tornado.web.Application([
        (r"/rewrite", TaxiRewriteHandler),
        (r"/poiservice/rewrite", TaxiRewriteHandler),
        (r"/gulfstream/rewrite", GsRewriteHandler),
        (r"/gs_rewrite", GsRewriteHandler)
    ])
    return app


if __name__ == "__main__":
    opt.parse_command_line()
    if not g_cfg.isready:
        print g_cfg.last_error
        os.exit(1)
    app = make_app()
    server = tornado.httpserver.HTTPServer(app)
    server.listen(opt.options.port)
    tornado.ioloop.IOLoop.instance().start()
