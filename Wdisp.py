#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/6/13 21:00
# @File    : Wdisp.py

import re
import pandas as pd
# from io import StringIO

import utility
from utility import multiple_replace
import ploter


class Wdisp(object):

    def __init__(self, content):
        __list_name = [x.replace(' ', '') for x in re.findall(r'=+.*?=+\s+(.*?)\n', content)]
        __list_content = [x.strip()
                          for x in re.split(r'=+.*?=+\s+.*?\n',
                                            multiple_replace(content.strip(),
                                                             {'\n\n': '\n', '1/ ': '', '1/': '', '%': ''}))]

        if len(__list_name) + 1 == len(__list_content):
            __lst = []
            __lst_wind = []
            __lst_spc_lateral = []
            __lst_gravity = []
            __lst_cqc = []
            for __ct, __value in enumerate(__list_name):
                __lst.append(__value)
                if __value.find('风') >= 0:
                    __lst_wind.append(__value)
                elif __value.find('规定水平力') >= 0:
                    __lst_spc_lateral.append(__value)
                elif __value.find('竖向') >= 0:
                    __lst_gravity.append(__value)
                else:
                    __lst_cqc.append(__value)
                __cache = re.sub(r'\n\s{8,}', '', __list_content[__ct + 1])
                setattr(self, __value, lines_2_df(__cache))
            self.displacement = __lst
            self.wind = __lst_wind
            self.gravity = __lst_gravity
            self.spc_lateral = __lst_spc_lateral
            self.cqc = __lst_cqc

    def export(self):
        writer = pd.ExcelWriter(dfp.result_name('Disp.xlsx'))
        for item in self.displacement:
            getattr(self, item).to_excel(writer, sheet_name=item)
        writer.save()

    def drift_plot(self):
        writer = pd.ExcelWriter(dfp.result_name('Disp_Drift.xlsx'))
        drift_dict = {}
        for item in self.cqc:
            if item.find('方向') >= 0:
                df = getattr(self, item)
                dff = df.iloc[:, [0, 1, -3]]
                dff = pd.concat([dff, 1 / dff.iloc[:, -1]], sort=False, axis=1)
                drift_dict[item] = dff
                dff.to_excel(writer, sheet_name=item)
                for name, group in df.groupby('Tower'):
                    image_name = item.replace('下的楼层最大位移', '层间位移角')
                    png_name = '%d 塔 %s' % (name, image_name)
                    print('输出:%s' % png_name)
                    ploter.MPLLine({image_name: [10000 / group.iloc[:, -3], group['Floor']]},
                                   figsize=(8.58 / 2.54, 11 / 2.54),
                                   yticks=range(group['Floor'].astype(int).tolist()[-1],
                                                len(group['Floor']) + group['Floor'].astype(int).tolist()[-1]),
                                   yticklabels=group['Floor'].astype(int).tolist().reverse(),
                                   xlabel='%s\n$(1/10000)$' % png_name,
                                   ylabel='楼层',
                                   filename=dfp.result_name('%s .png' % png_name)
                                   ).draw(vlim=10000 / 550, xlimlab='1/550')
        writer.save()
        return drift_dict

    def ratio_plot(self):
        writer = pd.ExcelWriter(dfp.result_name('Disp_Ratio.xlsx'))
        ratio_dict = {}
        for item in self.spc_lateral:
            df = getattr(self, item)
            dff = df.iloc[:, [0, 1, -5, -1]]
            dff.to_excel(writer, sheet_name=item)
            ratio_dict[item] = dff
            for name, group in df.groupby('Tower'):
                ratio_name = item.replace('作用下的楼层最大位移', '位移比')
                drift_ratio_name = item.replace('作用下的楼层最大位移', '层间位移比')
                for nickname, position in zip([ratio_name, drift_ratio_name], [-5, -1]):
                    png_name = '%d 塔 %s' % (name, nickname)
                    print('输出:%s' % png_name)
                    ploter.MPLLine({nickname: [group.iloc[:, position], group['Floor']]},
                                   figsize=(8.58 / 2.54, 11 / 2.54),
                                   yticks=range(group['Floor'].astype(int).tolist()[-1],
                                                len(group['Floor']) + group['Floor'].astype(int).tolist()[-1]),
                                   yticklabels=group['Floor'].astype(int).tolist().reverse(),
                                   xlabel='%s' % png_name,
                                   ylabel='楼层',
                                   filename=dfp.result_name('%s .png' % png_name)
                                   ).draw(vlim=1.2, xlimlab='1.2')

        writer.save()
        return ratio_dict

    def gravity_plot(self):
        print(self.gravity)

    def wind_plot(self):
        print(self.wind)


def lines_2_df(content: str):
    """

    :param content:
    :return:
    """
    if isinstance(content, str):
        lst_lines = [x.strip() for x in re.split('\n', content)]
        lst_lst = []
        len_df = 0
        for ct, item in enumerate(lst_lines):
            if ct == 0:
                lst_lst.append(item.split())
                len_df = len(lst_lst[0])
            else:
                _cache = item.split()
                if len(_cache) >= len_df:
                    lst_lst.append(_cache[0:len_df])
        return pd.DataFrame(lst_lst[1:], columns=lst_lst[0], dtype=float)


if __name__ == '__main__':
    dfp = utility.FilePath()
    wdisp_file = dfp.full_name('wdisp.out')
    with open(wdisp_file, 'r') as f:
        wdisp = Wdisp(f.read())
        yjk_drift = wdisp.drift_plot()
        wdisp.wind_plot()
        yjk_ratio = wdisp.ratio_plot()
        wdisp.gravity_plot()
        wdisp.export()
