# -*- coding: utf-8 -*-
# @Author: yupengarthur
# @Date:   2016-04-12 15:08:30

import os
import json
import datetime
import logging
import logging.handlers


class didiLog():
    """
    didi_log - initialize log module

    Args:
      log_dir       - 日志目录，若不存在会自动创建
                      注意info级别的日志会输出到public目录
                      warn/error级别的日志会输出到error目录
      level         - 日志最低输出级别
      when          - 时间间隔，天级('D')/小时级('H')
      backuptimes   - 日志保留份数(时间）
      maxbytes      - 日志文件大小
      bactuprolls   - 日志保留份数(大小)
      fmt           - 日志格式(注意，此处非public日志)
      datefmt       - 日期时间格式

    Raises:
        OSError: fail to create log directories
        IOError: fail to open log file
    """

    def __init__(
        self, log_dir="./log", level=logging.INFO,
        when="H", backuptimes=72,
        maxbytes=100000000, bactuprolls=3,
        fmt="%(levelname)s: %(asctime)s: %(filename)s:%(lineno)d %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    ):
        self.when = when
        self.backuptimes = backuptimes

        formatter = logging.Formatter(fmt, datefmt)
        public_formatter = logging.Formatter("%(message)s")

        self.mkdirsifnotexit(log_dir)

        logger = logging.getLogger()
        logger.setLevel(level)

        # 设置roll.log
        handler = logging.handlers.RotatingFileHandler(
            filename=os.path.join(log_dir, 'roll.log'),
            maxBytes=maxbytes,
            backupCount=bactuprolls)
        handler.setLevel(level)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        didi_public_dir = os.path.join(log_dir, "public/")
        didi_error_dir = os.path.join(log_dir, "error/")

        self.didi_public = self.get_didi("didi.public", didi_public_dir, "public.log", logging.INFO, public_formatter)
        self.didi_error = self.get_didi("", didi_error_dir, "error.log", logging.WARNING, formatter)

    def get_didi(self, name, log_dir, filename, level, formatter):
        logger = logging.getLogger(name)
        self.mkdirsifnotexit(log_dir)
        handler = logging.handlers.TimedRotatingFileHandler(
            filename=os.path.join(log_dir, filename),
            when=self.when,
            backupCount=self.backuptimes)
        handler.setLevel(level)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def mkdirsifnotexit(self, log_dir):
        if not os.path.isdir(log_dir):
            os.makedirs(log_dir)


def writePublicLog(didi_logger, key, res_obj, name, addr, lng, lat, maptype, oid, area):
        kvlist = [key]
        kvlist.append('timestamp=' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        kvlist.append('oid=' + str(oid))
        kvlist.append('area=' + str(area))
        kvlist.append('name=' + name)
        kvlist.append('addr=' + addr)
        kvlist.append('lng=' + str(lng))
        kvlist.append('lat=' + str(lat))
        kvlist.append('maptype=' + str(maptype))
        kvlist.append('json_str=' + json.dumps(res_obj, ensure_ascii=False))
        didi_logger.didi_public.info("||".join(kvlist))


if __name__ == '__main__':
    logger = didiLog()
    logger.didi_public.info("public test")
    logger.didi_error.error("error test")
    logging.info("Hello World!!!")
    logging.warn("warning")
    logging.error("error")
    logging.warn("warning over")
    logging.error("error over")
    logging.info("over")
