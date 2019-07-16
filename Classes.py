#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/5/16 22:45
# @Author  : Aries
# @Site    : 
# @File    : Classes.py
# @Software: PyCharm

import re
import tkinter as tk
from tkinter import filedialog
import os
import math
# import numpy as np
import pandas as pd
import Wpj


# 去除List中的空值''
def remove_null(lst_got):
    while '' in lst_got:
        lst_got.remove('')
    return lst_got


# 对多行文字按行split，每行按空格split，形成2维数组
def lines_fill_df(lines, position):
    __lst_data = []
    for __item in lines.split('\n'):
        __cache = __item.strip().split()
        if len(__cache) >= position:
            __lst_data.append(__cache[0: position])
    return pd.DataFrame(__lst_data[1:], columns=__lst_data[0])


# 以符号分隔，去除空元素
def split_remove_null(pattern, str_with_n):
    return remove_null(re.split(pattern, str_with_n.strip()))


class ControlForce:

    def __init__(self, *args):

        if len(args) == 1:
            pass
        elif len(args) > 1:
            pass

        # if str_force.find(')') >= 0:
        #     str_force = str_force.strip()
        #     self.load_case = str_force.split(')')[0]
        #     self.force_data = str_force.split(')')[1].split()
        #     __lst_name = []
        #     __lst_data = []
        #     for __item__ in self.force_data:
        #         __lst_name.append(__item__.split('=')[0])
        #         __lst_data.append(__item__.split('=')[1])
        #     self.force_dict = dict(zip(__lst_name, __lst_data))


class ControlMoment(ControlForce):

    def __init__(self, str_force):
        super().__init__(str_force)


class ControlShear(ControlForce):

    pass


class ControlJoint(ControlForce):

    pass


class ControlAxial(ControlForce):

    pass


class Material:

    def __init__(self):
        pass


class Concrete(Material):

    def __init__(self, content):
        super().__init__()
        __int_rcc = float(content)
        if isinstance(__int_rcc, float):
            if __int_rcc == 15:
                self.fc = 7.2
                self.ft = 0.91
            elif __int_rcc == 20:
                self.fc = 9.6
                self.ft = 1.10
            elif __int_rcc == 25:
                self.fc = 11.9
                self.ft = 1.27
            elif __int_rcc == 30:
                self.fc = 14.3
                self.ft = 1.43
            elif __int_rcc == 35:
                self.fc = 16.7
                self.ft = 1.57
            elif __int_rcc == 40:
                self.fc = 19.1
                self.ft = 1.71
            elif __int_rcc == 45:
                self.fc = 21.1
                self.ft = 1.80
            elif __int_rcc == 50:
                self.fc = 23.1
                self.ft = 1.89
            elif __int_rcc == 55:
                self.fc = 25.3
                self.ft = 1.96
            elif __int_rcc == 60:
                self.fc = 27.5
                self.ft = 2.04
            elif __int_rcc == 65:
                self.fc = 29.7
                self.ft = 2.09
            elif __int_rcc == 70:
                self.fc = 31.8
                self.ft = 2.14
            elif __int_rcc == 75:
                self.fc = 33.8
                self.ft = 2.18
            elif __int_rcc == 80:
                self.fc = 35.9
                self.ft = 2.22
            else:
                raise
        self.fck = self.fc * 1.4
        self.ftk = self.ft * 1.4

        if __int_rcc <= 50:
            self.alpha_1 = 1.0
            self.beta_1 = 0.8
            self.beta_c = 1.0
        elif __int_rcc == 80:
            self.alpha_1 = 0.94
            self.beta_1 = 0.74
            self.beta_c = 0.8
        else:
            self.alpha_1 = 1.0 - (1.0 - 0.94) * (80 - __int_rcc) / 30
            self.beta_1 = 0.8 - (0.8 - 0.74) * (80 - __int_rcc) / 30
            self.beta_c = 1.0 - (1.0 - 0.80) * (80 - __int_rcc) / 30


class Steel(Material):

    def __init__(self):
        super().__init__()


class Section:

    def __init__(self, section_type, section_name, section_data):
        if len(section_name) > 0:
            self.names = section_name[0].split('*')
        else:
            raise
        if len(section_data) > 0:
            if section_data[0].find(Column.SIGN_ANGLE) >= 0:
                self.data = section_data[0].split()[0].split('*')
            else:
                self.data = section_data[0].split('*')
        else:
            raise
        if isinstance(int(section_type), int):
            self.type = int(section_type)
        else:
            raise
        if len(self.names) == len(self.data):
            if self.type == 1 or self.type == 13 or self.type == 15:
                self.area = float(self.data[0]) * float(self.data[1])
            elif self.type == 3:
                self.area = math.pi * pow(float(self.data[0]), 2) / 4
        else:
            raise


class Column:

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
    LIST_SIGN = [SIGN_COLUMN_NUMBER,  # 1
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
    LIST_SIGN_CONCRETE = [SIGN_CONCRETE_COVER,  # 1
                          SIGN_CONCRETE_STRENGTH_GRADE,  # 2
                          SIGN_REBAR_GRADE,  # 3
                          SIGN_STIRRUP_GRADE,  # 4
                          SIGN_COLUMN_SHEAR_SPAN_RATIO,  # 5
                          ]

    def __init__(self, content: str, lst_para: list, *args):

        content = re.sub(r'=\s+', '=', content)
        content = content.replace('(%)', '')
        __lst_attr = lst_para
        if isinstance(args, tuple):
            if len(args) >= 1:
                __lst_attr.extend(args[0])

        for __item in __lst_attr:
            pattern = re.compile(__item + r'=(\S+)')
            # __value = __lst_got[0] if len(__lst_got) > 0 else None
            __lst_got = re.findall(pattern, content)
            if len(__lst_got) > 0:
                __value = __lst_got[0]
            else:
                __value = None
            setattr(self, '%s' % Greece2Eng.replace(__item), __value)

        self.section = Section(re.findall(self.PATTERN_BRACKET, content)[self.POSITION_SEC_TYPE],
                               re.findall(self.PATTERN_NUM_in_BRA__mm_in_BRA, content),
                               re.findall(self.PATTERN_EQUAL_2_END, content))
        # 各工况list
        self.lst_force_data = re.findall(self.PATTERN_LEFT_BRACKET_2_END, content)

    @staticmethod
    def material(str_material):
        if str_material.find('砼柱') >= 0:
            return 'concrete'
        elif str_material.find('钢柱') >= 0:
            return 'steel'

    def shear_capacity_utilization(self):
        pass


class ConcreteColumn(Column):

    def __init__(self, content):

        super().__init__(content, self.LIST_SIGN_CONCRETE)

        self.concrete = Concrete(getattr(self, self.SIGN_CONCRETE_STRENGTH_GRADE, None))

        self.axial_force = self.lst_force_data[0]

    def shear_axial_ratio(self, load_com):
        # for force in self.forces:
        #     if float(force.load_case) in load_com.load_case_no_eq:
        #         return self.concrete.beta_c * self.concrete.fc * self.section.area
        #     else:
        #         print('lc is %s' % force.load_case)
        pass


class LoadCase:

    def __init__(self, content):
        content = content.replace('--', '0.0')
        content = re.split('\n', content.strip())
        content = remove_null(content)
        _lst_content = []
        for __line in content:
            _item_line = __line.split()
            if len(_item_line) > 5:
                _lst_content.append(__line.split())
        __combine = pd.DataFrame(_lst_content[1:], columns=_lst_content[0], dtype=float)
        self.load_case_no_eq = __combine[(__combine['X-E'] == 0) & (__combine['Y-E'] == 0) & (__combine['Z-E'] == 0)][
            'Ncm'].tolist()
        self.combine = __combine


class Greece2Eng:

    char_dict = {
        'α': 'alpha',
        'β': 'beta',
        'γ': 'gamma',
        'δ': 'delta',
        'ε': 'epsilon',
        'ζ': 'zeta',
        'η': 'eta',
        'θ': 'theta',
        'ι': 'iota',
        'κ': 'kappa',
        'λ': 'lambda',
        'μ': 'mu',
        'ν': 'nu',
        'ξ': 'xi',
        'ο': 'omicron',
        'π': 'pi',
        'ρ': 'rho',
        'σ': 'sigma',
        'ς': 'sigma',
        'τ': 'tau',
        'υ': 'upsilon',
        'φ': 'phi',
        'χ': 'chi',
        'ψ': 'psi',
        'ω': 'omega'
    }

    @classmethod
    def replace(cls, str2rep):
        return cls.multiple_replace(str2rep, cls.char_dict)

    # 多重替换函数
    @staticmethod
    def multiple_replace(text, dict_rpl):
        rx = re.compile('|'.join(map(re.escape, dict_rpl)))

        def rules(match): return dict_rpl[match.group(0)]

        return rx.sub(rules, text)


if __name__ == '__main__':

    # 对话框取得文件夹名称
    dir_tk = tk.Tk()
    dir_tk.withdraw()
    dfp_data = filedialog.askdirectory()

    file_name = os.path.join(dfp_data, 'wpj1.out')

    with open(file_name, 'r') as f:
        wpj = Wpj.Wpj(f.read())
        lst = []
        for item in wpj.columns:
            lst.append(Column(item))
