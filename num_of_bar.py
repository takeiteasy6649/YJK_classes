#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/7/13 0:28
# @File    : num_of_bar.py

# -*- coding: utf-8 -*-

width = float(input('梁宽:'))
diameter = float(input('纵筋直径:'))
cover = float(input('保护层厚度:'))

net_width = width - 2 * cover - diameter

top_space = max((30, 1.5 * diameter)) + diameter
bottom_space = max((25, diameter)) + diameter

top_num = net_width // top_space + 1
bottom_num = net_width // bottom_space + 1

top_net_space = (width - 2 * cover - top_num * diameter) / (top_num - 1)
bottom_net_space = (width - 2 * cover - bottom_num * diameter) / (bottom_num - 1)

print('上铁最多布置%d根直径%d的钢筋, 钢筋净距%.2f\n下铁最多布置%d根直径%d的钢筋, 钢筋净距%.2f'
      %
      (top_num, diameter, top_net_space, bottom_num, diameter, bottom_net_space))
