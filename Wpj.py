#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/5/20 22:56
# @File    : Wpj.py

import re
import tkinter as tk
from tkinter import filedialog
import os
import pandas as pd
import numpy as np


import config
import utility
from column import ConcreteColumn
from beam import ConcreteBeam
from loadcombine import LoadCombine
import ploter


class Wpj(object):

    result_dict = {'柱配筋设计及验算': 'columns',
                   '支撑配筋设计及验算': 'braces',
                   '墙柱配筋设计及验算': 'wall_columns',
                   '墙梁配筋设计及验算': 'wall_beams',
                   '梁配筋设计及验算': 'beams',
                   '次梁配筋设计及验算': 'sec_beams',
                   '空心板肋梁配筋设计及验算': 'hollow_slab',
                   '地基梁配筋设计及验算': 'foundation_beam'
                   }

    def __init__(self, content: str):

        try:
            self.floor_number = int(re.findall(r'第(.*?)层', content)[0])
        except IndexError as e:
            print(e)

        try:
            self.std_floor_number = int(re.findall(r'标准层(\d+)', content)[0])
        except IndexError as e:
            print(e)

        self.list_content = [x.strip() for x in re.split(r'\s+\*{5,}', content)]

        self.columns = []
        self.braces = []
        self.wall_columns = []
        self.wall_beams = []
        self.beams = []
        self.sec_beams = []
        self.hollow_slab = []
        self.foundation_beam = []

        for __ct in range(len(self.list_content)):

            __tmp_item = self.list_content[__ct].strip()

            if __tmp_item.find('荷载组合分项系数说明') >= 0:
                self.combine = LoadCombine(__tmp_item)

        for key, value in self.result_dict.items():

            try:
                lst = []
                pos = self.list_content.index(key)
                data = utility.remove_null(re.split(r'-{5,}', self.list_content[pos + 1].strip()))
                if key.find('柱配筋设计及验算') == 0:
                    # self.col_data = data
                    print('处理柱数据...')
                    for item in data:
                        if item.find('砼柱') >= 0:
                            lst.append(ConcreteColumn(item,  LIST_SIGN_COLUMN, LIST_SIGN_COLUMN_CONCRETE))
                        elif item.find('钢柱') >= 0:
                            pass
                        elif item.find('型钢砼柱') >= 0:
                            pass
                elif key.find('梁配筋设计及验算') == 0:
                    print('处理梁数据')
                    for item in data:
                        if item.find('砼梁') >= 0:
                            lst.append(ConcreteBeam(item))

                setattr(self, value, lst)
            except ValueError:
                pass


if __name__ == '__main__':

    # 柱编号
    SIGN_COLUMN_NUMBER = 'N-C'
    # 柱布置角度
    SIGN_ANGLE = 'Ang'
    # 混凝土保护层厚度
    SIGN_CONCRETE_COVER = 'Cover'

    # 柱长度
    SIGN_COLUMN_LENGTH = 'Lc'
    # 不要修改以下两行
    SIGN_COLUMN_LENGTH_X = SIGN_COLUMN_LENGTH + 'x'
    SIGN_COLUMN_LENGTH_Y = SIGN_COLUMN_LENGTH + 'y'

    # 柱长度系数
    SIGN_COLUMN_LENGTH_ADJUST_FACTOR = 'C'
    # 不要修改以下两行
    SIGN_COLUMN_LENGTH_ADJUST_FACTOR_X = SIGN_COLUMN_LENGTH_ADJUST_FACTOR + 'x'
    SIGN_COLUMN_LENGTH_ADJUST_FACTOR_Y = SIGN_COLUMN_LENGTH_ADJUST_FACTOR + 'y'

    # 抗震等级
    SIGN_SEISMIC_GRADE = 'Nfc'
    # 抗震构造等级
    SIGN_SEISMIC_CONSTRUCT_GRADE = 'Nfc_gz'

    # 混凝土强度等级
    SIGN_CONCRETE_STRENGTH_GRADE = 'Rcc'
    # 纵筋强度等级
    SIGN_REBAR_GRADE = 'Fy'
    # 箍筋强度等级
    SIGN_STIRRUP_GRADE = 'Fyv'

    # 钢材强度等级
    SIGN_STEEL_GRADE = 'Rsc'

    # 活荷载折减系数
    SIGN_LIVE_LOAD_REDUCTION = 'livec'

    # SIGN
    SIGN_ADJUST_MOMENT_UPPER = 'ηmu'
    SIGN_ADJUST_MOMENT_DOWN = 'ηmd'
    SIGN_ADJUST_SHEAR_UPPER = 'ηvu'
    SIGN_ADJUST_SHEAR_DOWN = 'ηvd'

    # 剪跨比
    SIGN_COLUMN_SHEAR_SPAN_RATIO = 'λc'

    # 抗剪承载力
    SIGN_CB_XF = 'CB_XF'
    SIGN_CB_YF = 'CB_YF'

    # 截面类型变量在括号内，该行共有3对括号，位置受该参数控制，开始于0
    POSITION_SEC_TYPE = 1

    # 搜索括号中内容的pattern
    PATTERN_BRACKET = re.compile(r'[(](.*?)[)]')

    # 搜索右括号'）'和'('之间内容的pattern，该数据为截面类型的字母
    PATTERN_NUM_in_BRA__mm_in_BRA = re.compile(r'[(]\d+[)](.*?)[(]mm[)]')

    # 搜索'(mm)='和'\n'之间内容的pattern，
    PATTERN_EQUAL_2_END = re.compile(r'[(]mm[)]=(.*?)\n')

    # 搜索'('和'\n'之间内容的pattern，
    PATTERN_LEFT_BRACKET_2_END = re.compile(r'\s{2,}[(]\s(.*?)\n')

    # Column的11个属性，其余属性放到子类
    LIST_SIGN_COLUMN = [SIGN_COLUMN_NUMBER,  # 1
                        SIGN_ANGLE,  # 2
                        SIGN_COLUMN_LENGTH_ADJUST_FACTOR_X,  # 3
                        SIGN_COLUMN_LENGTH_ADJUST_FACTOR_Y,  # 4
                        SIGN_COLUMN_LENGTH_X,  # 5
                        SIGN_COLUMN_LENGTH_Y,  # 6
                        SIGN_SEISMIC_GRADE,  # 7
                        SIGN_SEISMIC_CONSTRUCT_GRADE,  # 8
                        SIGN_LIVE_LOAD_REDUCTION,  # 9
                        SIGN_CB_XF,  # 10
                        SIGN_CB_YF,  # 11
                        ]

    # 混凝土柱的属性，子类引用，本类不使用，放在此处方便修改
    LIST_SIGN_COLUMN_CONCRETE = [SIGN_CONCRETE_COVER,  # 1
                                 SIGN_CONCRETE_STRENGTH_GRADE,  # 2
                                 SIGN_REBAR_GRADE,  # 3
                                 SIGN_STIRRUP_GRADE,  # 4
                                 SIGN_COLUMN_SHEAR_SPAN_RATIO,  # 5
                                 ]

    # 对话框取得文件夹名称
    dir_tk = tk.Tk()
    dir_tk.withdraw()
    dfp_data = filedialog.askdirectory()

    file_name = os.path.join(dfp_data, 'wpj2.out')

    with open(file_name, 'r') as f:
        wpj = Wpj(f.read())
        scu_x = []
        scu_y = []
        sar = []
        sar_beam = []
        for col in wpj.columns:
            if isinstance(col, ConcreteColumn):
                scu_x.append(col.shear_capacity_utilization.x)
                scu_y.append(col.shear_capacity_utilization.y)
                sar.append(col.shear_axial_ratio(wpj.combine))
        for beam in wpj.beams:
            if isinstance(beam, ConcreteBeam):
                sar_beam.append(beam.shear_axial_ratio(wpj.combine))
        t = pd.DataFrame(sar_beam)
        t.to_excel('d:/test.xlsx')
        ploter.MPLScatter({'剪压比': [range(len(sar)), sar]},
                          hlines=1,
                          legend=True,
                          c=1 - np.array(sar),
                          filename='d:/柱剪压比',
                          xlabel='构件编号',
                          ylabel='剪压比/限值').draw()
        ploter.MPLScatter({'剪压比': [range(len(sar_beam)), [sar_beam]]},
                          hlines=1,
                          legend=True,
                          c=1 - np.array(sar_beam),
                          filename='d:/梁剪压比',
                          xlabel='构件编号',
                          ylabel='剪压比/限值').draw()
        ploter.MPLHist({'剪压比': sar_beam},
                       legend=True,
                       sign=True,
                       filename='d:/梁剪压比分布',
                       xlabel='剪压比/限值',
                       ylabel='构件数量').draw()
        config_para = config.Setup('config.ini')
