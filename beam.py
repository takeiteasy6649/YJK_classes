#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/5/27 12:24
# @File    : beam.py

# import os
import re
import math
import numpy as np
import pandas as pd

from utility import Greece2Eng
from loadcombine import LoadCombine
from material import Concrete
# from material import Steel


# 截面类
class Section(object):

    def __init__(self, sec_type, sec_dim_name, sec_dim_data, cover=20):
        """
        all param send in is considered with units in 'mm'
        :param sec_type:
        :param sec_dim_name:
        :param sec_dim_data:
        :param cover:
        """
        try:
            self.section_type = int(sec_type)
        except ValueError:
            print('截面类型参数错误')

        try:
            self.cover = int(cover)
        except ValueError:
            print('保护层参数错误')

        sdn = sec_dim_name[0].split('*') if len(sec_dim_name) > 0 else []

        if len(sec_dim_data) > 0:

            if sec_dim_data[0].find('Ang=') >= 0:
                sdd = sec_dim_data[0].split()[0].split('*')
            else:
                sdd = sec_dim_data[0].split('*')
        else:
            sdd = []

        self.section_dict = dict(zip(sdn, sdd)) if len(sdn) == len(sdd) else None
        for key, value in self.section_dict.items():
            setattr(self, key, value)

    # 截面面积
    @property
    def area(self):
        """
        cal the area of section
        :return:
        """
        area = pd.NaT

        # 矩形截面
        if self.section_type in [1, 13, 15]:
            b = float(self.B) if hasattr(self, 'B') else pd.NaT
            h = float(self.H) if hasattr(self, 'H') else pd.NaT
            try:
                area = b*h
            except ValueError:
                print('参数类型错误')
            except TypeError:
                print('%s, %s' % (b, h))
        # 圆形截面
        elif self.section_type in [3, ]:
            try:
                area = math.pi * pow(float(self.Dr), 2) / 4 if hasattr(self, 'Dr') else pd.NaT
            except TypeError:
                print('%s' % self.Dr if hasattr(self, 'Dr') else pd.NaT)
        elif self.section_type in [103, 105, ]:
            try:
                area = math.pi * pow(float(self.B), 2) / 4 if hasattr(self, 'B') else pd.NaT
            except TypeError:
                print('%s' % self.Dr if hasattr(self, 'Dr') else pd.NaT)
        # 其它截面暂时返回空值

        return area

    @property
    def wt(self):
        if self.section_type in [1, 13, 15]:
            b = float(self.B) if hasattr(self, 'B') else pd.NaT
            h = float(self.H) if hasattr(self, 'H') else pd.NaT
            try:
                wt = pow(min(b, h), 2) * (3 * max(b, h) - min(b, h)) / 6
                return wt
            except ValueError:
                print('参数类型错误')
            except TypeError:
                print('%s, %s' % (b, h))


class Element(object):

    __LIST = ['N-B', 'Lb', 'Rcb', 'Cover']

    def __init__(self, content, *args):
        """
        init deal with 'content' from 'wpj*.out'
        1. findall param in LIST
        2. get the information given in CHINESE
        :param content:
        :param args:
        """
        content = re.sub(r'=\s+', '=', content)
        content = re.sub(r'\(%\)', '', content)
        __lst_attr = self.__LIST

        # args: for extend
        for __item in args:
            __lst_attr.extend(__item)

        for __item in __lst_attr:
            __pattern = re.compile(__item + r'=(\S+)')

            __lst_got = re.findall(__pattern, content)
            __value = __lst_got[0] if len(__lst_got) > 0 else None

            setattr(self, '%s' % Greece2Eng.replace(__item), __value)

        # 截面类型变量在括号内，该行共有3对括号，位置受该参数控制，开始于0
        self.POSITION_SEC_TYPE = 1

        # 搜索括号中内容的pattern
        self.PATTERN_BRACKET = re.compile(r'[(](.*?)[)]')

        # 搜索右括号'）'和'('之间内容的pattern，该数据为截面类型的字母
        self.PATTERN_NUM_in_BRA__mm_in_BRA = re.compile(r'[(]\d+[)](.*?)[(]mm[)]')

        # 搜索'(mm)='和'\n'之间内容的pattern，
        self.PATTERN_EQUAL_2_END = re.compile(r'[(]mm[)]=(.*?)\n')

        # 搜索'('和'\n'之间内容的pattern，
        self.PATTERN_LEFT_BRACKET_2_END = re.compile(r'\s{2,}[(]\s(.*?)\n')

        # section
        self.section = Section(re.findall(self.PATTERN_BRACKET, content)[self.POSITION_SEC_TYPE],
                               re.findall(self.PATTERN_NUM_in_BRA__mm_in_BRA, content),
                               re.findall(self.PATTERN_EQUAL_2_END, content))

        # material
        self.concrete = Concrete(self.Rcb) if hasattr(self, 'Rcb') else None
        self.steel = Concrete(self.Rsb) if hasattr(self, 'Rsb') else None


class Beam(Element):

    str_cache = ''

    def __init__(self, content, *args):
        super().__init__(content, *args)

        pass


class ConcreteBeam(Beam):

    def __init__(self, content, *args):
        super().__init__(content, *args)

        content = re.sub(r'\([A-Za-z]+\)', '', content)
        content = re.sub(r'\(', '', content)
        content = re.sub(r'\)', '', content)
        content = re.sub(r'%\s+', 'Ratio', content)
        content = re.sub(r'\sAst', 'Ast', content)
        self.force = beam_content_2_df(content)

        __position = self.force[self.force[self.force.columns[0]]
                                ==
                                'RatioSteel'].index.tolist()
        __position = [x + 1 for x in __position]
        __position.insert(0, 0)
        __position.append(len(self.force))

        __lst_attr_name = ['m_n', 'm_p', 'shear']
        self.m_n = None
        self.m_p = None
        self.shear = None
        for ct in range(len(__position) - 1):
            __case_data = self.force.iloc[__position[ct]:__position[ct+1], :]
            __case_data.set_index(__case_data[0], drop=True, inplace=True)
            setattr(self, __lst_attr_name[ct], __case_data.drop(0, axis=1).astype(float))

    def shear_axial_ratio(self, load_combine):
        """
        shear_axial_ratio of beam is not only control by shear, but also by torsion
        :param load_combine:
        :return:
        """
        if isinstance(load_combine, LoadCombine):
            __v = self.shear.loc['V'].values
            __load_case = self.shear.loc['LoadCase'].values
            try:
                __t = self.shear.loc['T'].values
            except KeyError:
                __t = np.array([0] * len(__v))

            __tmp = []
            for ct in range(len(__v)):
                __shear_axial_ratio_limit = 0.2 if\
                    float_attr(getattr(self, 'Lb'))*1000/float(getattr(self.section, 'H')) > 2.5 else 0.15
                if load_combine.control_by_eq(__load_case[ct]):
                    __gamma_re = 0.85
                else:
                    __gamma_re = 1.0
                    __shear_axial_ratio_limit = 0.25

                __tmp.append((abs(__v[ct]) * 1000 / self.section.area
                              +
                              abs(__t[ct]) * pow(10, 6) / (0.8 * self.section.wt))
                             *
                             __gamma_re
                             /
                             (__shear_axial_ratio_limit * self.concrete.beta_c * self.concrete.fc)
                             )
            return max(__tmp)

    @property
    def shear_utilization_ratio(self):

        return 1

    # @property
    # def shear_capacity(self):
    #     self.Rcb *


def float_attr(content):
    return float(re.sub(r'\(.*?\)', '', content))


def beam_content_2_df(beam_data: str):
    beam_data_lst = re.split('\n', beam_data)

    _lst_cache = []
    for beam_datum in beam_data_lst:
        beam_datum_lst = beam_datum.split()
        if len(beam_datum_lst) > 9:
            _lst_cache.append(beam_datum_lst)
    df_return = pd.DataFrame(_lst_cache)
    return df_return


# def main():
#
#     # 对话框取得文件夹名称
#     dir_tk = tk.Tk()
#     dir_tk.withdraw()
#     dfp_data = filedialog.askdirectory()
#
#     file_name = os.path.join(dfp_data, 'wpj2.out')
#
#     with open(file_name, 'r') as f:
#         wpj = Wpj.Wpj(f.read())
#         # lcc = LoadCombine(wpj.combine)
#         lst = []
#         if hasattr(wpj, 'beams'):
#             for item in wpj.beams:
#                 if item.find('砼梁') >= 0:
#                     lst.append(ConcreteBeam(item))
#         return lst
#
#
# if __name__ == '__main__':
#
#     # 梁的编号
#     SIGN_BEAM_NUMBER = 'N-B'
#     # 梁的长度(m)
#     SIGN_BEAM_LENGTH = 'Lb'
#     # 梁的抗震等级
#     SIGN_BEAM_SEISMIC_GRADE = 'Nfb'
#     # 梁抗震构造措施的抗震等级
#     SIGN_BEAM_SEISMIC_CONSTRUCT_GRADE = 'Nfb_gz'
#     # 梁的材料强度
#     SIGN_BEAM_CONCRETE_GRADE = 'Rcb'
#     # 梁的钢号
#     SIGN_BEAM_STEEL = 'Rsb'
#     # 构件的主筋强度设计值
#     SIGN_BEAM_REBAR_GRADE = 'Fy'
#     # 构件的箍筋强度设计值
#     SIGN_BEAM_STIRRUP_GRADE = 'Fyv'
#     # 柱、墙活荷载按楼层折减系数
#     SIGN_LIVE_LOAD_REDUCTION = 'livec'
#     # 框架梁为刚度放大系数，连梁为刚度折减系数
#     SIGN_BEAM_STIFFNESS = 'stif'
#     # 薄弱层调整系数，大于1时输出
#     SIGN_WEAK_STOREY_FACTOR = 'brc'
#     # 水平转换构件地震作用调整系数，大于1时输出
#     SIGN_TRANSFER = 'zh'
#     # 梁弯矩调幅系数
#     SIGN_MOMENT_REDUCTION = 'tf'
#     # 梁扭矩折减系数
#     SIGN_TORSION_REDUCTION = 'nj'
#     # 梁强剪弱弯调整系数
#     SIGN_BEAM_MOMENT_ADJUST = 'ηv'
#
#     cache = main()
#     # tmp = pd.DataFrame(list(zip(cache[0].m_n, cache[0].m_n_load_case, cache[0].m_n_ratio))).T
#     # tmp = tmp.set_index(tmp[tmp.columns[0]])
#     #
#     # print(tmp.loc['+M'])
#     # print(tmp.loc['LoadCase'])
#     # print(tmp.loc['RatioSteel'])
