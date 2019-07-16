#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/5/14 12:03
# @Author  : Aries
# @Site    : 
# @File    : sql.py
# @Software: PyCharm


import sqlite3


# db_name = r'D:\YJK结果文件试算模型\施工图\dtlmodel.ydb'
# col_num = 2
# int_floor = 2


def find_col_sec(col_num, int_floor, db_name):
    db = sqlite3.connect(db_name)
    cu = db.cursor()
    cu.execute('select StdFlrID from tblFloor where No_=%d' % int_floor)
    std_flr_id = cu.fetchone()[0]
    cu.execute('select SectID from tblColSeg where No_=%d and StdFlrID=%d' % (col_num, std_flr_id))
    col_sec_id = cu.fetchone()[0]
    cu.execute("select ShapeVal from tblColSect where ID=%d" % col_sec_id)
    sec_shape_value = cu.fetchone()[0]
    return sec_shape_value



