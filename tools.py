#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/5/4 8:08
# @Author  : Aries
# @Site    : 
# @File    : tools.py
# @Software: PyCharm

import tkinter as tk
from tkinter import filedialog
import os
import glob
import time
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib import font_manager
import sqlite3
import math


def find_col_sec(col_num, int_floor, db_name):
    db = sqlite3.connect(db_name)
    cu = db.cursor()
    cu.execute('select StdFlrID from tblFloor where No_=?', str(int_floor))
    std_flr_id = cu.fetchone()[0]
    print('column number = %d' % col_num)
    print('stdFlrID = %d' % std_flr_id)
    cu.execute('select SectID from tblColSeg where No_=%d and StdFlrID=%d' % (col_num, std_flr_id))
    col_sec_id = cu.fetchone()[0]
    print('colSecID = %d' % col_sec_id)
    cu.execute("select ShapeVal from tblColSect where ID=?", col_sec_id)
    sec_shape_value = cu.fetchone()[0]
    return sec_shape_value


# 以符号分隔，去除空元素
def split_remove_null(pattern, str_with_n):
    return remove_null(re.split(pattern, str_with_n.strip()))


# 去除List中的空值''
def remove_null(lst_got):
    while '' in lst_got:
        lst_got.remove('')
    return lst_got


# 合并相邻两行
def interlace(lst_got):
    if isinstance(lst_got, list):
        return list(map(lambda x, y: (x + y).split(), lst_got[::2], lst_got[1::2]))
    else:
        raise


# 处理层号数组
def floor_reset(lst_floor, num_podium):
    # 最小层号和转换层位置的最小值作为start，数组长度作为长度，步长为1
    _start = min(int(lst_floor[0]), num_podium+1)
    _stop = _start + len(lst_floor)
    return np.arange(_start, _stop)


# 对多行文字按行split，每行按空格split，形成2维数组
def lines_fill_df(lines, position):
    __lst_data = []
    for __item in lines.split('\n'):
        __cache = __item.strip().split()
        if len(__cache) >= position:
            __lst_data.append(__cache[0: position])
    return pd.DataFrame(__lst_data[1:], columns=__lst_data[0])


# 多重替换函数
def multiple_replace(text, dict_rpl):
    rx = re.compile('|'.join(map(re.escape, dict_rpl)))
    def rules(match): return dict_rpl[match.group(0)]
    return rx.sub(rules, text)


# 补全层号信息
def insert_floor(lst_dsp_cache):
    lst_return = [lst_dsp_cache[0]]
    for ct_in in range(1, len(lst_dsp_cache)):
        if len(lst_dsp_cache[ct_in]) == len(lst_dsp_cache[0]) - 1:
            lst_dsp_cache[ct_in].insert(0, lst_dsp_cache[ct_in - 1][0])
            lst_return.append(lst_dsp_cache[ct_in])
        elif len(lst_dsp_cache[ct_in]) == len(lst_dsp_cache[0]):
            lst_return.append(lst_dsp_cache[ct_in])

    return lst_return


def etabs_split(df_got):
    if '楼层' in df_got.columns:
        df_got['etabs_floor'] = list(map(lambda x: int(re.findall(r'\d+', x)[-1]), df_got['楼层']))
        df_got['etabs_tower'] = list(map(lambda x: int(re.findall(r'\d+', x)[0]), df_got['楼层']))
        # # 单塔时的处理，待测试
        # if df_got['etabs_floor'] == df_got['etabs_tower']:
        #     df_got['etabs_tower'] = [1] * df_got['etabs_floor'].shape[0]
        return df_got


# 设置图例置顶，透明，2列
def set_leg_trans(__plt):
    chinese = mpl.font_manager.FontProperties(fname=r'C:\Windows\Fonts\simkai.ttf')
    legend = __plt.legend(prop=chinese, bbox_to_anchor=(0., 1.02, 1., 0.102), loc='lower left', ncol=2, mode='expand',
                          borderaxespad=0)
    __leg_frame = legend.get_frame()
    __leg_frame.set_alpha(1)
    __leg_frame.set_facecolor('none')


# 绘图
def draw_plot(drawer, lst_x, lst_y, lst_legend, label_hor, label_ver, saved_png_name,
              draw_type='plot', draw_height=0.8):

    font = dict(family='KaiTi', color='black', weight='normal', size=10.5)
    marker = ['^', 'o', '*', 'v', 'p', 'P', 'h', 'H']

    if isinstance(lst_x[0], pd.Series) and isinstance(lst_y[0], np.ndarray):
        if len(lst_x) == len(lst_y):
            for num_item in range(0, len(lst_x)):
                if draw_type == 'plot':
                    drawer.plot(lst_x[num_item],
                                lst_y[num_item],
                                label=lst_legend[num_item],
                                marker=marker[num_item % 8])
                elif draw_type == 'barh':
                    drawer.barh(lst_y[num_item] + draw_height*num_item/2,
                                lst_x[num_item],
                                height=draw_height,
                                label=lst_legend[num_item],
                                marker=marker[num_item % 8])

            ticks = lst_y[0]
        else:
            raise
    elif isinstance(lst_x, pd.Series) and isinstance(lst_y, np.ndarray):
        if lst_x.shape[0] == len(lst_y):
            if draw_type == 'plot':
                drawer.plot(lst_x,
                            lst_y,
                            label=lst_legend,
                            marker=marker[0])
            elif draw_type == 'barh':
                drawer.barh(lst_y + draw_height,
                            lst_x,
                            height=draw_height,
                            label=lst_legend,
                            marker=marker[0])
            ticks = lst_y
        else:
            raise

    drawer.yticks(ticks)
    drawer.xlabel(label_hor, fontdict=font)
    drawer.ylabel(label_ver, fontdict=font)

    set_leg_trans(drawer)
    drawer.tight_layout()
    drawer.savefig(saved_png_name, transparent=True, dpi=300)
    drawer.show()


# 文件目录类，生成结果文件夹，给各模块提供文件路径
class DataFilePath:

    def __init__(self, data_path_name):
        if os.path.exists(data_path_name):
            self.ext_names = ['*.out', '*.xlsx', '*.xls', '*.txt']

            self.data_path_name = data_path_name
            self.result_path_name = os.path.join(data_path_name, 'result %s' % time.time())
            os.makedirs(self.result_path_name)
            self.data_file_names = []
            __lst_file_names = []
            for __item in self.ext_names:
                __lst_file_names.extend(glob.glob(os.path.join(data_path_name, __item)))
            self.data_file_names = __lst_file_names
            __db_name = os.path.join(data_path_name, 'dtlmodel.ydb')
            if os.path.exists(__db_name):
                self.db_name = __db_name
            else:
                raise OSError
        else:
            raise NotADirectoryError


# 对应 fea.dat-ERR.txt文件的类，读取控制振型对应的周期，并按奇偶分为x和y方向，并求最大值作为时程分析时对比的周期
class ModalCtrl:

    def __init__(self, content):
        self.content = content
        all_modal_ctrl_line = re.findall(r'方向(.*?)[\n]', content)
        self.all_modal_ctrl = list(map(lambda x: float(re.findall(r'[(](.*?)[)]', x)[0]), all_modal_ctrl_line))
        self.modal_ctrl_x = min(self.all_modal_ctrl[::2])
        self.modal_ctrl_y = min(self.all_modal_ctrl[1::2])


# wmass.out文件对应的类
class Wmass:

    def __init__(self, content):
        if content.find('总信息文件') < 0:
            raise
        self.content = content
        content = re.split(r'\s+\*{2,}', content.strip().replace('\n\n', '\n'))
        content.pop(0)
        # 各项数据名称，属性名称：result_names，数据格式：list
        # 数据内容，属性名称：result_dates，数据格式：dict
        self.result_names = list(map(lambda x: re.sub(r'[(].*?[)]', '', x.strip().split('\n')[0]), content[::2]))
        self.result_dates = dict(zip(self.result_names, content[1::2]))

        # 设计参数，属性名称：info，数据格式：dict
        __lst_name = []
        __lst_data = []
        for __item in self.result_dates['设计参数输出'].split('\n'):
            __cache = __item.split(':')
            if len(__cache) == 2:
                __lst_name.append(__cache[0].strip())
                __lst_data.append(__cache[1].strip())
        self.info = dict(zip(__lst_name, __lst_data))

        # 楼层属性
        self.storey = lines_fill_df(self.result_dates['楼层属性'], 2).astype(float)

        # 楼层质量
        __lst_data = []
        _df = lines_fill_df(self.result_dates['各层质量、质心坐标，层质量比'], 10).astype(float)
        _columns = _df.columns.tolist()
        _columns[-3] = '未折减活载质量'
        _df.columns = _columns
        _df['重力荷载代表值'] = _df['恒载质量'] + _df['活载质量']
        self.mass = _df

        # 楼层等效尺寸
        self.storey_area = lines_fill_df(self.result_dates['各楼层等效尺寸'], 9).astype(float)

        # 稳定验算（刚重比）-地震
        self.rigid_weight_ratio_eq = lines_fill_df(self.result_dates['结构整体稳定验算'].split(':')[1], 8).astype(float)

        # 稳定验算（刚重比）-风荷载
        self.rigid_weight_ratio_wind = lines_fill_df(self.result_dates['结构整体稳定验算'].split(':')[2], 8).astype(float)

        # 层抗剪承载力
        self.storey_shear_strength = lines_fill_df(self.result_dates['楼层抗剪承载力验算'], 6).astype(float)

        # 刚度
        __cache = re.split(r'\s+-{2,}', self.result_dates['各层刚心、偏心率、相邻层侧移刚度比等计算信息'])[:-1]
        __lst_cache = []
        for __item in __cache:
            __item_replaced = re.sub(r'[(].*?[)]', '', __item)
            __item_replaced = multiple_replace(__item_replaced, {'No.': '', '=': ''})
            __lst_cache.append(__item_replaced.replace('\n', '').split())
        self.stiffness = pd.DataFrame(list(map(lambda x: x[1::2], __lst_cache)), columns=__lst_cache[0][::2])

    def to_excel(self, file_name):
        with pd.ExcelWriter(file_name) as __writer:
            self.mass.to_excel(__writer, sheet_name='mass')
            self.rigid_weight_ratio_eq.to_excel(__writer, sheet_name='rigid_weight_ratio_eq')
            self.stiffness.to_excel(__writer, sheet_name='stiffness')
            self.storey_area.to_excel(__writer, sheet_name='storey_area')
            self.storey_shear_strength.to_excel(__writer, sheet_name='storey_shear_strength')


# wdisp.out文件对应的类
class Wdisp:

    def __init__(self, content):
        if content.find('位移输出文件') < 0:
            raise
        self.content = content
        # 按‘等号 内容 等号 名称（names） 换行’的格式取得数据名称（names），数据格式list
        self.result_names = list(map(lambda x: x.replace(' ', ''),
                                     re.findall(r'=+\s+\S+\s+=+\s+(.*?)\n', content)))
        # 按‘等号 内容 等号 名称（names） 换行’的格式split数据，得到数据list
        content = re.split(r'=+\s+\S+\s+=+\s+.*?\n',
                           multiple_replace(content.strip(),
                                            {'\n\n': '\n', '1/ ': '', '1/': '', '%': ''}))
        content.pop(0)
        # 单工况数据内容，属性名称：result_dates，数据格式：dict
        self.result_dates = dict(zip(self.result_names, content))

        # 位移数据，数据格式：dict，位移角一列为倒数，百分比一列为放大100倍的数值，数据名称：self.disp_data
        __lst_name_cache = []
        __lst_df_cache = []
        for __key, __value in self.result_dates.items():
            _lst = []
            __cache = __value.strip().split('\n')
            if len(__cache[0].split()) == 4:
                _lst = list(map(lambda x: x.strip().split(), __cache))
            else:
                _lst = list(map(lambda x, y: x.strip().split() + y.strip().split(), __cache[::2], __cache[1::2]))

            __lst_name_cache.append(__key)
            __lst_df_cache.append(pd.DataFrame(_lst[1:], columns=_lst[0]).dropna().astype(float))

        self.disp_data = dict(zip(__lst_name_cache, __lst_df_cache))

    def to_excel(self, file_name):
        with pd.ExcelWriter(file_name) as __writer:
            for __key, __value in self.disp_data.items():
                __value.to_excel(__writer, sheet_name=__key)

    # def get(self, load_case_name, data_name):
    #     if isinstance(data_name, int):
    #         _df = self.disp_data[load_case_name][self.disp_data[load_case_name].columns[data_name]]
    #     elif isinstance(data_name, str):
    #         _df = self.disp_data[load_case_name][data_name]
    #     return _df
    #
    # def compare_etabs(self, df_etabs):
    #     print(self.result_names)
    #     num_input = input('要对比的数据序号:')
    #     print(df_etabs.drift)


# wzq.out文件对应的类
class Wzq:

    def __init__(self, content):
        if content.find('周期、地震力与振型输出文件') < 0:
            raise
        self.content = content

        # 剪重比限值, 百分数（无百分号%）
        _lst = re.findall(r'楼层最小剪重比.*=(.*?)%[\n]', content)
        self.shear_weight_ratio_lim_x = float(_lst[0].strip())
        self.shear_weight_ratio_lim_y = float(_lst[1].strip())

        content = re.split(r'=+.*=+', content)
        # 楼层剪力调整系数，数据格式：DataFrame，数据名：self.shear_adjust_factor
        self.shear_adjust_factor = lines_fill_df(content[1], 6).astype(float)

        # 星号行split数据_lst，[1]为周期，[2][3]为剪力及剪重比
        _lst = re.split(r'\s+\*{2,}\n',  content[0].strip())

        __period_data = _lst[1].split('\n\n')
        # 周期，数据格式DataFrame（object），数据名称：self.period
        _df = lines_fill_df('\n'.join([__period_data[1], __period_data[2]]), 5)

        _direct_str = list(map(lambda x: re.findall(r'\d+\.\d+', x), _df.iloc[:, -2]))
        _df.drop([_df.columns[-2]], axis=1, inplace=True)
        _col_name = ['x&y', 'x', 'y']
        _df_direct = pd.DataFrame(_direct_str, columns=_col_name)
        for _ct in range(len(_col_name)):
            _df[_col_name[_ct]] = _df_direct[_col_name[_ct]]

        self.period = _df.astype(float)

        # 剪重比x, 剪重比为百分数（无百分号%）
        self.shear_weight_ratio_x =\
            lines_fill_df(multiple_replace(re.split(r'\s+-+\n', _lst[2])[-1],
                                           {'(': ' ', ')': ' ', '%': ''}),
                          7).astype(float)
        # 剪重比y, 剪重比为百分数（无百分号%）
        self.shear_weight_ratio_y = \
            lines_fill_df(multiple_replace(re.split(r'\s+-+\n', _lst[3])[-1],
                                           {'(': ' ', ')': ' ', '%': ''}),
                          7).astype(float)

    def to_excel(self, file_name):
        with pd.ExcelWriter(file_name) as __writer:
            self.period.to_excel(__writer, sheet_name='period')
            self.shear_adjust_factor.to_excel(__writer, sheet_name='shear_adjust_factor')
            self.shear_weight_ratio_x.to_excel(__writer, sheet_name='shear_weight_ratio_x')
            self.shear_weight_ratio_y.to_excel(__writer, sheet_name='shear_weight_ratio_y')


# wdyna.out文件对应的类
class Wdyna:

    def __init__(self, content):

        if content.find('动态时程分析结果输出') < 0:
            raise

        self.content = content

        __columns_dsp = ['floor', 'tower', 'jmax', 'max', 'ave', 'drf_max', 'h',
                         'jmaxd', 'max_d', 'ave_d', 'drf_ave']
        self.columns_dsp = ['floor', 'tower', 'jmax', 'max', 'ave', 'drf_max', 'h',
                            'jmaxd', 'max_d', 'ave_d', 'drf_ave', 'wave_name']
        __columns_v = ['floor', 'tower', 'v', 'm']
        self.columns_v = ['floor', 'tower', 'v', 'm', 'wave_name']

        # 各地震波名称，地震波数量
        self.name_of_waves = re.findall(r'=+地震波最大反应：(.*?)=+', content)
        self.num_of_waves = len(self.name_of_waves)

        # 用/{3,}进行分割content
        content = re.split(r'/{3,}', content)
        # content[0] 为各地震波计算结果
        # content[2] 为基底剪力数据
        # content[4] 为多波对比数据

        __lst_cache = re.split('=+.*=+', content[0].replace('1/', ''))
        __lst_cache.pop(0)
        __lst_df_v_x = []
        __lst_df_v_y = []
        __lst_df_dsp_x = []
        __lst_df_dsp_y = []
        __df_dsp_x = pd.DataFrame(columns=__columns_dsp)
        __df_dsp_y = pd.DataFrame(columns=__columns_dsp)
        __df_v_x = pd.DataFrame(columns=__columns_v)
        __df_v_y = pd.DataFrame(columns=__columns_v)

        for __num_item in range(len(__lst_cache)):
            __wave_date = re.split('-{2,}', __lst_cache[__num_item].replace('\n\n', '\n'))

            __dsp_x = __wave_date[3].strip().split('\n')

            __df_tmp = pd.DataFrame(insert_floor(interlace(__dsp_x)), columns=__columns_dsp).astype(float)
            __df_tmp['wave_name'] = [self.name_of_waves[__num_item]] * __df_tmp.shape[0]
            __df_dsp_x = __df_dsp_x.append(__df_tmp, ignore_index=True)

            __dsp_y = __wave_date[6].strip().split('\n')

            __df_tmp = pd.DataFrame(insert_floor(interlace(__dsp_y)), columns=__columns_dsp).astype(float)
            __df_tmp['wave_name'] = [self.name_of_waves[__num_item]] * __df_tmp.shape[0]
            __df_dsp_y = __df_dsp_y.append(__df_tmp, ignore_index=True)

            __v_x = __wave_date[4].strip().split('\n')
            __df_tmp = pd.DataFrame(insert_floor(list(map(lambda x: x.split(), __v_x))),
                                    columns=__columns_v).astype(float)
            __df_tmp['wave_name'] = [self.name_of_waves[__num_item]] * __df_tmp.shape[0]
            __df_v_x = __df_v_x.append(__df_tmp, ignore_index=True)

            __v_y = __wave_date[7].strip().split('\n')
            __df_tmp = pd.DataFrame(insert_floor(list(map(lambda x: x.split(), __v_y))),
                                    columns=__columns_v).astype(float)
            __df_tmp['wave_name'] = [self.name_of_waves[__num_item]] * __df_tmp.shape[0]
            __df_v_y = __df_v_y.append(__df_tmp, ignore_index=True)

        # 位移及层剪力
        self.df_dsp_x = __df_dsp_x
        self.df_dsp_y = __df_dsp_y
        self.df_v_x = __df_v_x
        self.df_v_y = __df_v_y

        # 基底剪力对比，待完善
        # __lst_cache = re.split('-{2,}', multiple_replace(content[2], {')': ')  ', '%': ''}))
        #
        # a = list(map(lambda x: re.split('\s{2,}', x), __lst_cache[0]))
        #
        # print(a)
        #
        # pass

        # 剪力对比（判断平均值，包络值）
        __lst_cache = re.split('={2,}', content[4].strip())
        if self.num_of_waves == 7:
            __position = 0
        else:
            __position = 2
        self.compare_v_x = lines_fill_df(__lst_cache[__position].split('\n\n')[0], 6).astype(float)
        self.compare_v_y = lines_fill_df(__lst_cache[__position].split('\n\n')[1], 6).astype(float)
        pass

    def to_excel(self, file_name):
        with pd.ExcelWriter(file_name) as __writer:
            self.df_dsp_x.to_excel(__writer, sheet_name='displacement_x')
            self.df_dsp_y.to_excel(__writer, sheet_name='displacement_y')
            self.df_v_x.to_excel(__writer, sheet_name='shear_force_x')
            self.df_v_y.to_excel(__writer, sheet_name='shear_force_y')


# wdynaspec.out文件对应的类
class WdynaSpec:

    def __init__(self, content):

        if content.find('弹性时程反应谱数据') < 0:
            raise

        self.content = content
        content = content.split('\n\n')
        content.remove('')

        # 多字符替换content第2项(谱时长，间隔)，split，取偶数项（[1::2]）,取奇数项（[::2]）
        dict_rpl = {'\n': ':', '(s)': ''}
        spec_info = multiple_replace(content[1], dict_rpl).split(':')
        spec_info = np.array(spec_info[1::2], dtype='float')

        # 形成时间序列
        self.spec_time_range = np.arange(spec_info[1], spec_info[2], spec_info[3])

        # 处理每个波数据
        __spec_names = []
        __spec_points = []
        for _ct in range(2, len(content)):
            __spec_data = content[_ct].split('\n')
            __spec_name = __spec_data[0].split(':')[-1].strip()
            __spec_names.append(__spec_name)
            __spec_str = ' '.join(__spec_data[1:])
            __spec_point = __spec_str.split()
            __spec_points.append(np.array(__spec_point, dtype='float'))

        # 各地震波的反应谱数据，数据格式dict，key为波名，value为np.array
        self.spec_dates = dict(zip(__spec_names, __spec_points))


class Uc:
    def __init__(self, content):
        __result = []
        sp_by_star = re.split(r'\*{2,}', content)

        for num in range(0, len(sp_by_star)):
            if sp_by_star[num].find('柱配筋设计及验算') >= 0 > sp_by_star[num].find('墙'):
                sp_by_hyphen = re.split(r'\s+-{2,}', sp_by_star[num+1])
                for cache in sp_by_hyphen:
                    if cache.split():
                        sp_by_line_feed = re.split('\n', cache)
                        for line in sp_by_line_feed:
                            if line.find('Uc=') >= 0:
                                sp_by_uc = re.split('Uc=', line.strip())
                                sp_by_space = re.split(r'\s+', sp_by_uc[1].strip())
                                __result.append(float(sp_by_space[0]))
        self.uc = __result

    def col_hist(self, file_name=None):

        plt.hist(self.uc, density=False, bins='auto', rwidth=0.8, align='right', label='uc', stacked=True)
        if file_name is not None:
            plt.savefig(file_name)
        plt.show()


# 截面属性类
class SectionProperty:

    def __init__(self, section_type, section_dicts):

        for name, value in section_dicts.items():
            setattr(self, name, float(value))

        pass

        if section_type == 1:
            self.area = self.B * self.H
            # print('area is: %f' % self.area)

            pass
        elif section_type == 2:
            pass
        elif section_type == 3:
            self.area = math.pi * pow(self.Dr, 2) / 4
            # print('area is: %f' % self.area)
            pass
        elif section_type == 4:
            pass
        elif section_type == 5:
            pass
        elif section_type == 6:
            pass
        elif section_type == 7:
            pass
        elif section_type == 8:
            pass
        elif section_type == 9:
            pass
        elif section_type == 10:
            pass
        elif section_type == 11:
            pass
        elif section_type == 12:
            pass
        elif section_type == 13:
            pass
        elif section_type == 14:
            pass
        elif section_type == 15:
            pass
        elif section_type == 26:
            pass
        elif section_type == 28:
            pass
        elif section_type == 29:
            pass
        elif section_type == 101:
            pass
        elif section_type == 102:
            pass
        elif section_type == 103:
            pass
        elif section_type == 104:
            pass
        elif section_type == 105:
            pass
        else:
            pass
        pass
        pass


class Column:
    def __init__(self, content):
        self.content = content
        if content.find('多塔') >= 0:
            cb_pos = -2
        else:
            cb_pos = -1
        _lst = content.strip().split('\n')
        _lst = remove_null(_lst)

        """
        第一行
        """
        # 柱构件编号
        self.number = int(re.findall(r'N-C=(.*?)\s', _lst[0])[0].strip())
        # 构件截面尺寸代码
        self.sec_dims = re.findall(r'[)](.*?)[(]', _lst[0])[-1]

        # 判断是否有角度，读角度、截面类型、截面参数
        if _lst[0].find('Ang=') >= 0:
            _lst_cache = _lst[0].split('Ang=')
            self.ang = float(_lst_cache[1].strip())
            __cache = _lst_cache[0]
        else:
            self.ang = 0.0
            __cache = _lst[0]

        # 截面类型, 截面数据
        self.sec_type = int(re.findall(r'[(](.*?)[)]', __cache)[-2])
        self.sec_info = __cache.split('=')[-1].strip()

        _lst_name = self.sec_dims.split('*')
        _lst_data = self.sec_info.split('*')
        _dict = dict(zip(_lst_name, _lst_data))
        self.sec_prop = SectionProperty(self.sec_type, _dict)

        """
        第三行
        """
        # 构件信息, 汉字文本
        self.col_info = _lst[2]

        """
        抗剪承载力，位置为cb_pos
        """
        # 抗剪承载力
        _lst_cache = re.findall(r'\d+\.\d+', _lst[cb_pos])
        self.cb_xf = _lst_cache[0]
        self.cb_yf = _lst_cache[1]

        _lst_remain = [_lst[1]] + _lst[3: cb_pos]

        for __item in _lst_remain:

            if __item.find('=') >= 0:

                __item = re.sub(r'=\s+', '=', __item)

                if __item.strip()[0] == '(':
                    _lc = int(re.findall(r'[(](.*?)[)]', __item)[0].strip())
                    __cache = 'lc=%d ' % _lc + __item.strip()
                else:
                    __cache = __item.strip()
                __cache = re.sub(r'\(.*?\)', '', __cache)

                _lst_sign = re.findall('As(.*?)=', __cache)
                if len(_lst_sign) == 2:
                    __cache = re.sub('As(.*?)=', 'As=', __cache)
                    __cache = re.sub('=', '%s=' % _lst_sign[0], __cache)

                _lst_cache = __cache.split()

                for _attr in _lst_cache:
                    _lst_attr = _attr.split('=')
                    setattr(self, _lst_attr[0], _lst_attr[1])

    def shear_axial_ratio(self, df_com):
        if self.col_info.find('砼柱') >= 0:
            if float(self.lambda_c) > 2:
                _factor = 0.2
                pass
            else:
                _factor = 0.15
                pass
            # self.sec_prop.area *
            pass
        elif self.col_info.find('型钢砼柱') >= 0:
            pass
        # _shear_force = max(self.Vxvx, self.Vxvy, self.Vyvy, self.Vyvx)
        return self.lambda_c

    def shear_capacity_utilization(self):
        pass


class Beam:
    def __init__(self, content):
        self.content = content
        pass


class TransferElement:

    def __init__(self, content):
        self.content = content
        content = re.sub('λ', 'lambda_', content)
        content = re.sub('η', 'eta_', content)
        __floor_num = int(re.findall('第(.*?)层', content)[0].strip())
        _lst = re.split(r'\s+\*{2,}', content)
        _lst = remove_null(_lst)

        for _ct in range(len(_lst)):
            if _lst[_ct].find('荷载组合分项系数说明') >= 0:
                __cache = _lst[_ct].replace('--', '0.0')
                self.combine = lines_fill_df(__cache, 13).astype(float)
            elif _lst[_ct].find('柱配筋设计及验算') >= 0 > _lst[_ct].find('墙'):
                _lst_cache = split_remove_null(re.compile('-{3,}'), _lst[_ct + 1])
                _lst_columns = []
                for __item in _lst_cache:
                    _lst_columns.append(Column(__item))
                self.columns = _lst_columns
            elif _lst[_ct].find('梁配筋设计及验算') >= 0 > _lst[_ct].find('墙'):
                _lst_cache = split_remove_null(re.compile('-{3,}'), _lst[_ct + 1])
                _lst_beams = []
                pass

        for __item in self.columns:
            print('from %s' % __item.shear_axial_ratio(self.combine))


class Etabs:

    def __init__(self, excel_name):
        _df = pd.read_excel(excel_name, 'Centers of Mass and Rigidity', skiprows=[0, 2]).fillna(0)
        self.mass = etabs_split(_df[_df['质量 X'] != 0])
        self.period = pd.read_excel(excel_name, 'Modal Periods and Frequencies', skiprows=[0, 2])
        _df = pd.read_excel(excel_name, 'Story Drifts', skiprows=[0, 2])
        self.drift = etabs_split(_df.drop(columns=_df.columns[-2]))
        pass


# 调试运行
if __name__ == '__main__':

    # 文件名称dict，如果数据文件名称变化根据情况修改带后缀名 out 的项
    dict_file_names = {'wmass': 'wmass.out',
                       'wzq': 'wzq.out',
                       'wdisp': 'wdisp.out',
                       'wv02q': 'wv02q.out',
                       'wdyna': 'wdyna.out',
                       'wdynaspec': 'wdynaSpec.out',
                       'wpj1': 'wpj1.out',
                       'wpj2': 'wpj2.out',
                       'fea': 'fea.dat-ERR.txt',
                       'model_db': 'dtlmodel.ydb',
                       1: 'wmass.out',
                       2: 'wzq.out',
                       3: 'wdisp.out',
                       4: 'wv02q.out',
                       5: 'wdyna.out',
                       6: 'wdynaSpec.out',
                       7: 'wpj1.out',
                       8: 'wpj2.out',
                       9: 'fea.dat-ERR.txt',
                       10: 'dtlmodel.ydb'}

    # 对话框取得文件夹名称，创建文件信息的类实例dfp_data
    dir_tk = tk.Tk()
    dir_tk.withdraw()
    dfp_data = DataFilePath(filedialog.askdirectory())
    # if ''

    # 循环形成各个数据文件的类实例
    for _file in dfp_data.data_file_names:
        _ext = os.path.splitext(_file)[-1]
        if _ext.find('out') >= 0 or _ext.find('txt') >= 0:
            with open(_file, 'r') as f:
                if _file.find(dict_file_names[1]) >= 0:
                    wmass = Wmass(f.read())
                    wmass.to_excel(os.path.join(dfp_data.result_path_name, 'wmass_yjk.xlsx'))

                elif _file.find(dict_file_names[2]) >= 0:
                    wzq = Wzq(f.read())
                    wzq.to_excel(os.path.join(dfp_data.result_path_name, 'wzq_yjk.xlsx'))

                elif _file.find(dict_file_names[3]) >= 0:
                    wdisp = Wdisp(f.read())
                    wdisp.to_excel(os.path.join(dfp_data.result_path_name, 'wdisp_yjk.xlsx'))

                elif _file.find(dict_file_names[4]) >= 0:
                    pass
                elif _file.find(dict_file_names[5]) >= 0:
                    wdyna = Wdyna(f.read())
                    wdyna.to_excel(os.path.join(dfp_data.result_path_name, 'wdyna_yjk.xlsx'))

                elif _file.find(dict_file_names[6]) >= 0:
                    wdynaspec = WdynaSpec(f.read())

                elif _file.find(dict_file_names[7]) >= 0:
                    uc = Uc(f.read())
                elif _file.find(dict_file_names[8]) >= 0:
                    transfer_ele = TransferElement(f.read())
                    pass
                elif _file.find(dict_file_names[9]) >= 0:
                    modal_ctrl = ModalCtrl(f.read())
        elif _ext.find('xlsx') >= 0 or _ext.find('xls') >= 0:
            etabs = Etabs(_file)
    # wdisp.get('X方向地震作用下的楼层最大位移', 'Floor')
    # wdisp.get('X方向地震作用下的楼层最大位移', -3)
    #
    # plt.plot(1 / wdisp.get('X方向地震作用下的楼层最大位移', -3), wdisp.get('X方向地震作用下的楼层最大位移', 'Floor'))
    # plt.show()
    #
    # # print(floor_reset(wdisp.get('X方向地震作用下的楼层最大位移', 'Floor').tolist()))
