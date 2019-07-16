#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/6/7 23:17
# @Author  : Liuyu
# @File    : fea.py


# 对应 fea.dat-ERR.txt文件的类，读取控制振型对应的周期，并按奇偶分为x和y方向，并求最大值作为时程分析时对比的周期
class ModalCtrl:

    def __init__(self, content):
        self.content = content
        all_modal_ctrl_line = re.findall(r'方向(.*?)[\n]', content)
        self.all_modal_ctrl = list(map(lambda x: float(re.findall(r'[(](.*?)[)]', x)[0]), all_modal_ctrl_line))
        self.modal_ctrl_x = min(self.all_modal_ctrl[::2])
        self.modal_ctrl_y = min(self.all_modal_ctrl[1::2])
