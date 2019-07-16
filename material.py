#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/6/3 13:20
# @Author  : Liuyu
# @File    : material.py


# 材料类: 基类
class Material:

    def __init__(self, *args):
        pass


# 材料类：混凝土
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


# 材料类：钢材
class Steel(Material):

    def __init__(self):
        super().__init__()
