#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/5/4 7:05
# @Author  : Aries
# @Site    : 
# @File    : entry.py
# @Software: PyCharm


import os
# import sys
import glob
from tkinter import filedialog
# 导入 Tkinter 库
import tkinter as tk


# 获取屏幕尺寸
def get_screen_size(window):
    return window.winfo_screenwidth(), window.winfo_screenheight()


# 获取窗口尺寸
def get_window_size(window):
    return window.winfo_reqwidth(), window.winfo_reqheight()


# 窗口置中
def center_window(__root, width, height):
    screenwidth = __root.winfo_screenwidth()
    screenheight = __root.winfo_screenheight()
    size = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
    __root.geometry(size)


# 单击动作
def clicked():
    path_got = filedialog.askdirectory()
    txt.delete(0.0, tk.END)
    txt.insert(tk.INSERT, path_got)

    ext_names = ['*.out', '*.xlsx', '*.xls', 'txt']
    lst_f = []

    if path_got:

        for item in ext_names:
            file_name = os.path.join(path_got, item)
            lst_f = lst_f + glob.glob(file_name)

        for ct in range(len(lst_f)):
            lbl.insert(ct, os.path.split(lst_f[ct])[1])


def set_text(event):
    # this block works
    # w = event.widget
    # cur_index = w.curselection()[-1]
    # txt_file_content.insert(tk.INSERT, w.get(cur_index))
    # with open(os.path.join(txt.get(0.0, tk.END).replace('\n', ''), w.get(cur_index)), 'r', errors='ignore') as f:
    #     txt_file_content.delete(0.0, tk.END)
    #     txt_file_content.insert(tk.INSERT, f.read())
    # this doesn't
    # self.curIndex = self.nearest(event.y)
    # print(self.curIndex)
    # self.curIndex = event.widget.nearest(event.y)
    # print(self.curIndex)
    pass


# 创建窗口对象
root = tk.Tk()
root.title('Just a toy!')
center_window(root, 1200, 900)

frm_top = tk.Frame(root)

lbl = tk.Label(frm_top, text='数据文件路径')
lbl.pack(side=tk.LEFT, padx=10, expand=tk.NO, fill=tk.NONE)

txt = tk.Text(frm_top, height=1)
txt.pack(side=tk.LEFT, padx=10, expand=tk.YES, fill=tk.X)
# txt.grid(column=1, row=0, sticky=W+E)

btn = tk.Button(frm_top, text='选择文件夹', command=clicked)
btn.pack(side=tk.LEFT, padx=10, expand=tk.NO, fill=tk.NONE)
# btn.grid(column=2, row=0, sticky=E)

# frm_top.pack(side=TOP, expand=YES, fill=X, anchor=N)
frm_top.pack(side=tk.TOP, padx=10, anchor=tk.N, expand=tk.YES, fill=tk.X)

frm_f_name = tk.Frame(root)
frm_f_name.pack(side=tk.LEFT, expand=tk.YES, fill=tk.BOTH)

ltb_top = tk.Listbox(frm_f_name, selectmode='browse')
ltb_top.bind('<Double-Button-1>', set_text)
ltb_top.pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH)
# lbl.grid(column=0, row=1, sticky=N+S+W)

lbl_bottom = tk.Listbox(frm_f_name, selectmode='browse')
lbl_bottom.pack(side=tk.BOTTOM, expand=tk.YES, fill=tk.BOTH)

# txt_file_content = tk.Text(frm_f_name, font=('Bookman Old Style', 12))
# txt_file_content.pack(side=tk.TOP, expand=tk.YES, fill=tk.X)
# # txt_file_content.grid(column=1, row=1, sticky=W + E)

# # scb_file_content = Scrollbar(root)
# # txt_file_content.config.py(yscrollcommand=scb_file_content.set)
# # scb_file_content.config.py(command=txt_file_content.yview)
# # scb_file_content.grid(column=2, row=1, sticky=N + S + W)

# txt_info = tk.Text(frm_f_name)
# txt_info.pack(side=tk.TOP, expand=tk.YES, fill=tk.X)
# # txt_info.grid(column=1, row=2, sticky=W+E)

frm_d_name = tk.Frame(root)

ltb_top_d = tk.Listbox(frm_d_name, selectmode='browse')
ltb_top_d.bind('<Double-Button-1>', set_text)
ltb_top_d.pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH)

lbl_bottom_d = tk.Listbox(frm_d_name, selectmode='browse')
lbl_bottom_d.pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH)

frm_d_name.pack(side=tk.LEFT, expand=tk.YES, fill=tk.BOTH)

frm_d = tk.Frame(root)

txt_top_d = tk.Listbox(frm_d, selectmode='browse')
txt_top_d.bind('<Double-Button-1>', set_text)
txt_top_d.pack(side=tk.TOP, expand=tk.YES, fill=tk.Y)

txt_bottom_d = tk.Listbox(frm_d, selectmode='browse')
txt_bottom_d.pack(side=tk.BOTTOM, expand=tk.YES, fill=tk.Y)

frm_d.pack(side=tk.LEFT, expand=tk.YES, fill=tk.Y)

frm_merge = tk.Frame(root)

txt_merge = tk.Text(frm_merge)
txt_merge.pack(side=tk.LEFT, expand=tk.YES, fill=tk.BOTH)

frm_merge.pack(side=tk.LEFT, fill=tk.Y)

# 进入消息循环
root.mainloop()
