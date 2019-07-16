#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/6/3 6:49
# @Author  : Liuyu
# @File    : ploter.py

import os
import matplotlib.pyplot as plt
from matplotlib import font_manager
import itertools
import numpy as np


def plot_env(draw_func):
    def wrapper(self, *args, **kwargs):
        self.show()
        u = draw_func(self, *args, **kwargs)
        self.close()
        return u

    return wrapper


class MPLBase(object):

    def __init__(self, data, kind=None,
                 figsize=(17.16 / 2.54, 11 / 2.54),
                 grid=True,
                 legend=True,
                 xlim=None, ylim=None,
                 xticks=None, yticks=None,
                 xticklabels=None, yticklabels=None,
                 xlabel=None, ylabel=None,
                 hlines=None, vlines=None,
                 fontsize=None,
                 filename=None,
                 **kwargs):

        self.marker = itertools.cycle(('o', 'v', 'p', 'h', 'x', 'd', '*', '+'))
        self.font = dict(family='KaiTi', color='black', weight='normal', size=10.5)

        self.small_font = dict(family='KaiTi', color='black', weight='normal', size=9)

        self.kai = font_manager.FontProperties(fname=os.path.join(os.getenv('SYSTEMROOT'), 'Fonts/simkai.ttf'))

        self.data = data
        self.kind = kind
        self.figsize = figsize
        self.grid = grid
        self.legend = legend
        self.xlim = xlim
        self.ylim = ylim
        self.xticks = xticks
        self.yticks = yticks
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.hlines = hlines
        self.vlines = vlines
        self.fontsize = fontsize
        self.filename = filename
        self.xticklabels = xticklabels
        self.yticklabels = yticklabels
        self.kwargs = kwargs

        self.fig, self.axs = plt.subplots(1, 1, figsize=self.figsize)

    def show(self):

        if self.grid is True:
            self.axs.grid(alpha=0.5, linestyle="-.", linewidth=0.3)
        self.axs.set_xlabel(self.xlabel, fontdict=self.font)
        self.axs.set_ylabel(self.ylabel, fontdict=self.font)

    def close(self):

        if self.hlines is not None:
            left, right = self.axs.get_xlim()
            self.axs.hlines(self.hlines, left, right, color='r', linestyle='--', label='Limit')
        if self.vlines is not None:
            bottom, top = self.axs.get_ylim()
            self.axs.vlines(self.vlines, bottom, top, color='r', linestyle='--', label='Limit')
        if self.legend is True:
            frm = self.axs.legend(prop=self.kai, bbox_to_anchor=(0., 1.02, 1., .102), loc='lower left',
                                  ncol=1, mode="expand", borderaxespad=0.)
            frm = frm.get_frame()
            frm.set_alpha(1)
            frm.set_facecolor('none')
        if self.yticks is not None:
            self.axs.set_yticks(self.yticks)
        if self.yticklabels is not None:
            self.axs.set_yticklabels(self.yticklabels)
        self.fig.show()
        self.fig.savefig(self.filename, transparent=True, dpi=300)
        self.fig.clear()
        plt.close(fig=self.fig)


class MPLLine(MPLBase):

    def __init__(self, data, **kwargs):
        super().__init__(data, **kwargs)

    @plot_env
    def draw(self, hlim=None, vlim=None, xlimlab=None, ylimlab=None):
        if isinstance(self.data, dict):
            for key, value in self.data.items():
                self.axs.plot(value[0], value[1], label=key, marker=next(self.marker))
                if hlim is not None and ylimlab is not None:
                    x_min, x_max = self.axs.get_xlim()
                    self.axs.hlines(hlim, x_min, x_max, linestyle='--', color='firebrick', label=ylimlab)
                if vlim is not None and xlimlab is not None:
                    y_min, y_max = self.axs.get_ylim()
                    self.axs.vlines(vlim, y_min, y_max, linestyle='--', color='firebrick', label=xlimlab)


class MPLScatter(MPLBase):

    def __init__(self, data, c=None, **kwargs):
        super().__init__(data, **kwargs)
        self.c = c

    @plot_env
    def draw(self):
        if isinstance(self.data, dict):
            for key, value in self.data.items():
                self.axs.scatter(value[0], value[1], label=key, marker=next(self.marker), c=self.c, s=5)


class MPLHist(MPLBase):

    def __init__(self, data, rwidth=0.8, align='mid', sign=True, **kwargs):
        super().__init__(data, **kwargs)

        self.rwidth = rwidth
        self.align = align
        self.sign = sign

    @plot_env
    def draw(self):
        if isinstance(self.data, dict):
            for key, value in self.data.items():
                n, bins, patches = self.axs.hist(value,
                                                 bins=np.arange(0, max(value) + 0.1, 0.1),
                                                 density=False,
                                                 rwidth=self.rwidth,
                                                 align=self.align,
                                                 label=key
                                                 )
                if self.sign is True:
                    total = np.sum(n)
                    for x, y in zip(bins, n):
                        self.axs.annotate('{:.1%}'.format(y / total), xy=(x, y), xytext=(0, 1),
                                          textcoords="offset pixels",)


class MPLBar(MPLBase):

    def __init__(self, data, bar_type='h', height=0.8, **kwargs):
        super().__init__(data, **kwargs)

        self.height = height
        self.bar_type = bar_type

    @plot_env
    def draw(self, lim=None):
        if isinstance(self.data, dict):
            num = len(self.data)
            height = self.height / num
            if self.bar_type == 'h':
                for ct, key in enumerate(self.data):
                    self.axs.barh([x + height * ct for x in self.data[key][0]],
                                  self.data[key][1],
                                  alpha=0.8,
                                  height=height,
                                  label=key)
                if isinstance(lim, dict):
                    for ct, key in enumerate(lim):
                        self.axs.plot(lim[key][1],
                                      [x + height * ct for x in lim[key][0]],
                                      label=key,
                                      linestyle='--'
                                      )
                self.axs.set_yticks(list(self.data.values())[0][0])
            elif self.bar_type == 'v':
                for ct, key in enumerate(self.data):
                    self.axs.bar([x + height * ct for x in self.data[key][0]],
                                 self.data[key][1],
                                 width=height,
                                 label=key)
                if isinstance(lim, dict):
                    for ct, key in enumerate(lim):
                        self.axs.plot([x + height * ct for x in lim[key][0]],
                                      lim[key][1],
                                      label=key,
                                      linestyle='--'
                                      )
                self.axs.set_xticks(list(self.data.values())[0][0])


if __name__ == '__main__':
    draw = MPLLine({'YJK': [[1, 2, 3, 4], [1, 2, 3, 4]], 'ETABS': [[4, 3, 2, 1], [1, 2, 3, 4]]},
                   filename='line', xlabel='x1', ylabel='y1').draw()
    MPLLine({'YJK': [[1, 2, 3, 4], [1, 2, 3, 4]]}, filename='line2', xlabel='x2', ylabel='y2').draw()
    MPLScatter({'YJK': [[1, 2, 3, 4], [1, 2, 3, 4]]}, filename='scatter1', xlabel='编号', ylabel='ysc').draw()
    MPLBar({'YJK': [[1, 2, 3, 4], [1, 2, 3, 4]], 'ETABS': [[4, 3, 2, 1], [1, 2, 3, 4]],
            'PKPM': [[1, 2, 3, 4], [1, 2, 3, 4]]},
           bar_type='v', filename='barh', xlabel='x1', ylabel='y1').draw()
