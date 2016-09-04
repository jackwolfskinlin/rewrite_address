#!/bin/bash

# 编译_coordtrans扩展
cd libs/pycoordtrans
python2 setup.py build_ext --inplace
mv _coordtrans.so ../../

