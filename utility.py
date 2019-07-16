#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/6/3 12:55
# @Author  : Liuyu
# @File    : utility.py

import os
import glob
import tkinter as tk
import re
import random
from tkinter import filedialog


# 操作目录：数据文件目录，结果目录
class FilePath(object):
    """
    class for path operation
    """

    def __init__(self, openfile=False):
        # 对话框取得文件夹名称
        dir_tk = tk.Tk()
        dir_tk.withdraw()
        if openfile is False:
            self.input_path = filedialog.askdirectory()
        else:
            self.input_file = filedialog.askopenfilename(title="Select file",
                                                         filetypes=(("Excel files", "*.xlsx *.xls"),
                                                                    ("all files", "*.*")
                                                                    )
                                                         )
            self.input_path = os.path.split(self.input_file)[0]
        self.current_result_path = os.path.join(self.input_path, 'result%d' % random.randint(1000, 9999))
        os.makedirs(self.current_result_path)

    def new_path(self):
        self.current_result_path = os.path.join(self.input_path, 'result%d' % random.randint(1000, 9999))
        os.makedirs(self.current_result_path)
        return self.current_result_path

    def full_name(self, file_name):
        __full_name = os.path.join(self.input_path, file_name)
        if os.path.exists(__full_name):
            return __full_name
        else:
            return None

    def result_name(self, file_name):
        return os.path.join(self.current_result_path, file_name)

    @property
    def wpj_files(self):
        return glob.glob(os.path.join(self.input_path, 'wpj*.out'))


# 转换希腊字母为英文字母的类
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

    @classmethod
    # 多重替换函数, 闭包
    def multiple_replace(cls, text, dict_rpl):
        """
        closure
        :param text:
        :param dict_rpl:
        :return:
        """
        rx = re.compile('|'.join(map(re.escape, dict_rpl)))

        def rules(match): return dict_rpl[match.group(0)]

        return rx.sub(rules, text)


# 带有分隔符的字符串转为dict
def str_2_dict(str_got: str, sign_split: str):
    """
    trans data in form:
        'key' + 'sign_split' + 'value' + whitespace
    to dict
    :param str_got:
    :param sign_split:
    :return:
    """
    lst_key = []
    lst_value = []
    try:
        for str_split in str_got.split():
            lst_key.append(str_split.split(sign_split)[0])
            lst_value.append(str_split.split(sign_split)[1])
    except ValueError:
        print('参数错误')
    return dict(zip(lst_key, lst_value))


# 去除List中的空值''
def remove_null(lst_got):
    while '' in lst_got:
        lst_got.remove('')
    return lst_got


# 多重替换函数
def multiple_replace(text, dict_rpl):
    rx = re.compile('|'.join(map(re.escape, dict_rpl)))
    def rules(match): return dict_rpl[match.group(0)]
    return rx.sub(rules, text)
