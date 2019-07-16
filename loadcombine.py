#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/6/4 14:03
# @Author  : Liuyu
# @File    : loadcombine.py

import re
import pandas as pd


# 荷载工况类
class LoadCombine(object):

    def __init__(self, content):
        """
        content is considered as string read from 'wpj*.out' between lines(combined by '-')
        :param content:
        """
        content = content.replace('--', '0.0')
        content = re.split(r'\n', content)
        __lines_lst = []
        for __line in content:
            __cache = __line.split()
            if len(__cache) > 5:
                __lines_lst.append(__line.split())

        __combine = pd.DataFrame(__lines_lst[1:], columns=__lines_lst[0], dtype=float)
        self.combine = __combine
        self.load_case_without_eq = __combine[(__combine['X-E'] == 0) &
                                              (__combine['Y-E'] == 0) &
                                              (__combine['Z-E'] == 0)
                                              ]['Ncm'].tolist()

    def control_by_eq(self, lc_num):
        return False if int(lc_num) in self.load_case_without_eq else True
