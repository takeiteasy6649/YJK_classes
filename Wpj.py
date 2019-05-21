#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/5/20 22:56
# @Author  : Aries
# @Site    : 
# @File    : Wpj.py
# @Software: PyCharm

import re
import tkinter as tk
from tkinter import filedialog
import os
import tools


class Wpj(object):

    def __init__(self, content: str):

        try:
            self.floor_number = int(re.findall(r'第(.*?)层', content)[0])
        except IndexError as e:
            print(e)

        try:
            self.std_floor_number = int(re.findall(r'标准层(\d+)', content)[0])
        except IndexError as e:
            print(e)

        self.list_content = re.split(r'\s+\*{5,}', content)

        for __ct in range(len(self.list_content)):

            __tmp_item = self.list_content[__ct].strip()

            if __tmp_item.find('荷载组合分项系数说明') >= 0:
                self.combine = __tmp_item

            elif __tmp_item.find('柱配筋设计及验算') == 0:
                self.columns = tools.remove_null(re.split(r'-{5,}', self.list_content[__ct + 1].strip()))

            elif __tmp_item.find('梁配筋设计及验算') == 0:
                self.beams = tools.remove_null(re.split(r'-{5,}', self.list_content[__ct + 1].strip()))


class Columns(object):

    def __init__(self, lst_col_str: list):
        if isinstance(lst_col_str, list) and len(lst_col_str) >= 1:
            for __item_col_str in lst_col_str:
                pass
            pass
        else:
            raise


if __name__ == '__main__':

    # 对话框取得文件夹名称
    dir_tk = tk.Tk()
    dir_tk.withdraw()
    dfp_data = filedialog.askdirectory()

    file_name = os.path.join(dfp_data, 'wpj1.out')

    with open(file_name, 'r') as f:
        rebar_file_content = Wpj(f.read())
        columns = Columns(rebar_file_content.columns)
