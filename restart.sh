#!/bin/bash
# 依赖tornado, 请确认对应python是否安装了相关模块。
kill -9 `ps aux | grep rewriteapp | grep -v grep | awk '{print $2}'`
mkdir -p log
mkdir -p log/public
nohup python rewriteapp.py --log_file_prefix=log/access.log &>/dev/null &

