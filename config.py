#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/5/21
# @File    : config.py.py

import configparser
import os


class Setup(object):

    __file_name = 'config.ini'

    def __init__(self, *args):
        self.config = configparser.ConfigParser()
        if len(args) == 1 and os.path.exists(args[0]):
            self.config.read(args[0])
        else:
            self.config.read(self.__file_name)

        __SIGN_COLUMN_NUMBER = self.config["COLUMN"]['SIGN_COLUMN_NUMBER']
        __SIGN_ANGLE = self.config["COLUMN"]['SIGN_ANGLE']
        __SIGN_CONCRETE_COVER = self.config["COLUMN"]['SIGN_CONCRETE_COVER']
        __SIGN_COLUMN_LENGTH_X = self.config["COLUMN"]['SIGN_COLUMN_LENGTH_X']
        __SIGN_COLUMN_LENGTH_Y = self.config["COLUMN"]['SIGN_COLUMN_LENGTH_Y']
        __SIGN_COLUMN_LENGTH_ADJUST_FACTOR_X = self.config["COLUMN"]['SIGN_COLUMN_LENGTH_ADJUST_FACTOR_X']
        __SIGN_COLUMN_LENGTH_ADJUST_FACTOR_Y = self.config["COLUMN"]['SIGN_COLUMN_LENGTH_ADJUST_FACTOR_Y']
        __SIGN_SEISMIC_GRADE = self.config["COLUMN"]['SIGN_SEISMIC_GRADE']
        __SIGN_SEISMIC_CONSTRUCT_GRADE = self.config["COLUMN"]['SIGN_SEISMIC_CONSTRUCT_GRADE']
        __SIGN_CONCRETE_STRENGTH_GRADE = self.config["COLUMN"]['SIGN_CONCRETE_STRENGTH_GRADE']
        __SIGN_REBAR_GRADE = self.config["COLUMN"]['SIGN_REBAR_GRADE']
        __SIGN_STIRRUP_GRADE = self.config["COLUMN"]['SIGN_STIRRUP_GRADE']
        __SIGN_STEEL_GRADE = self.config["COLUMN"]['SIGN_STEEL_GRADE']
        __SIGN_LIVE_LOAD_REDUCTION = self.config["COLUMN"]['SIGN_LIVE_LOAD_REDUCTION']
        __SIGN_ADJUST_MOMENT_UPPER = self.config["COLUMN"]['SIGN_ADJUST_MOMENT_UPPER']
        __SIGN_ADJUST_MOMENT_DOWN = self.config["COLUMN"]['SIGN_ADJUST_MOMENT_DOWN']
        __SIGN_ADJUST_SHEAR_UPPER = self.config["COLUMN"]['SIGN_ADJUST_SHEAR_UPPER']
        __SIGN_ADJUST_SHEAR_DOWN = self.config["COLUMN"]['SIGN_ADJUST_SHEAR_DOWN']
        __SIGN_COLUMN_SHEAR_SPAN_RATIO = self.config["COLUMN"]['SIGN_COLUMN_SHEAR_SPAN_RATIO']
        __SIGN_CB_XF = self.config["COLUMN"]['SIGN_CB_XF']
        __SIGN_CB_YF = self.config["COLUMN"]['SIGN_CB_YF']

        self.LIST_SIGN_COLUMN = [__SIGN_COLUMN_NUMBER,  # 1
                                 __SIGN_ANGLE,  # 2
                                 __SIGN_COLUMN_LENGTH_ADJUST_FACTOR_X,  # 3
                                 __SIGN_COLUMN_LENGTH_ADJUST_FACTOR_Y,  # 4
                                 __SIGN_COLUMN_LENGTH_X,  # 5
                                 __SIGN_COLUMN_LENGTH_Y,  # 6
                                 __SIGN_SEISMIC_GRADE,  # 7
                                 __SIGN_SEISMIC_CONSTRUCT_GRADE,  # 8
                                 __SIGN_LIVE_LOAD_REDUCTION,  # 9
                                 __SIGN_CB_XF,  # 10
                                 __SIGN_CB_YF,  # 11
                                 ]


if __name__ == '__main__':
    config = configparser.ConfigParser()

    config["COLUMN"] = {
        # 柱编号
        'SIGN_COLUMN_NUMBER': 'N-C',
        # 柱布置角度
        'SIGN_ANGLE': 'Ang',
        # 混凝土保护层厚度
        'SIGN_CONCRETE_COVER': 'Cover',

        # 柱长度:X
        'SIGN_COLUMN_LENGTH_X': 'Lcx',
        # 柱长度:Y
        'SIGN_COLUMN_LENGTH_Y': 'Lcy',

        # 柱长度系数:X
        'SIGN_COLUMN_LENGTH_ADJUST_FACTOR_X': 'Cx',
        # 柱长度系数:Y
        'SIGN_COLUMN_LENGTH_ADJUST_FACTOR_Y': 'Cy',

        # 抗震等级
        'SIGN_SEISMIC_GRADE': 'Nfc',
        # 抗震构造等级
        'SIGN_SEISMIC_CONSTRUCT_GRADE': 'Nfc_gz',

        # 混凝土强度等级
        'SIGN_CONCRETE_STRENGTH_GRADE': 'Rcc',
        # 纵筋强度等级
        'SIGN_REBAR_GRADE': 'Fy',
        # 箍筋强度等级
        'SIGN_STIRRUP_GRADE': 'Fyv',

        # 钢材强度等级
        'SIGN_STEEL_GRADE': 'Rsc',

        # 活荷载折减系数
        'SIGN_LIVE_LOAD_REDUCTION': 'livec',

        # 强柱弱梁m、强剪弱弯v调整系数，u-顶，d-底
        'SIGN_ADJUST_MOMENT_UPPER': 'ηmu',
        'SIGN_ADJUST_MOMENT_DOWN': 'ηmd',
        'SIGN_ADJUST_SHEAR_UPPER': 'ηvu',
        'SIGN_ADJUST_SHEAR_DOWN': 'ηvd',

        # 剪跨比
        'SIGN_COLUMN_SHEAR_SPAN_RATIO': 'λc',

        # 抗剪承载力
        'SIGN_CB_XF': 'CB_XF',
        'SIGN_CB_YF': 'CB_YF'
    }

    with open('config.ini', 'w') as file:
        config.write(file)
