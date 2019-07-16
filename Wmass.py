#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/6/2 16:34
# @File    : Wmass.py

import re
import utility
import pandas as pd
from io import StringIO
import ploter


class Wmass(object):

    def __init__(self, content):

        self._list_content = [x.strip() for x in re.split(r'\s+\*{5,}', content)]

        result_dict = {'设计参数输出': '_design_info_str',
                       '楼层属性': '_floor_info_str',
                       '塔属性': '_tower_info_str',
                       '各层质量、质心坐标，层质量比': '_mass_info_str',
                       '各楼层质量、单位面积质量分布(单位:kg/m**2)': '_mass_density_info_str',
                       '结构整体抗倾覆验算': '_overturn_info_str',
                       '结构整体稳定验算': '_building_stable_info_str',
                       '楼层抗剪承载力验算': '_storey_shear_capacity_info_str',
                       }

        for key, value in result_dict.items():

            try:
                pos = self._list_content.index(key)
                setattr(self, value,
                        self._list_content[pos + 1].strip()
                        )
            except ValueError:
                pass

        self.design_info = lines_2_dict(getattr(self, '_design_info_str'))
        self.floor_info = lines_2_df(getattr(self, '_floor_info_str'))
        self.tower_info = lines_2_df(getattr(self, '_tower_info_str'))
        self.mass_info = lines_2_df(getattr(self, '_mass_info_str'))

        pos = self._list_content.index('计算时间')
        _str = self._list_content[pos + 3]
        _str = re.sub(r'\s*No.', 'No=', _str)
        _str = re.sub(r'\s*=\s*', '=', _str)
        _str = re.sub(r'\(\s*', '(', _str)
        _str = re.sub(r'\(.*?\)', '', _str)
        __lst = re.split(r'\s+-{3,}', _str)
        __result = []
        for __item in __lst[:-1]:
            __item = re.sub(r'\n', '', __item)
            __item = re.sub('=', ' ', __item)
            __lst_dict = __item.split()
            __result.append(pd.Series(dict(zip(__lst_dict[::2], __lst_dict[1::2]))))
        self.stiffness = pd.DataFrame(__result, dtype=float)

    @property
    def mass_density_info(self):
        _columns = re.findall(r'[\u4e00-\u9fa5]+', getattr(self, '_mass_density_info_str'))
        _data = StringIO(getattr(self, '_mass_density_info_str'))
        return pd.read_csv(_data, sep=r'\s+', skiprows=[0, ], names=_columns)

    @property
    def overturn_info(self):
        tmp = '工况 ' + getattr(self, '_overturn_info_str')
        return lines_2_df(tmp)

    @property
    def building_stable_info(self):
        return BuildingStableInfo(getattr(self, '_building_stable_info_str'))

    @property
    def storey_shear_capacity_info(self):
        tmp = re.split(r'\n\n', getattr(self, '_storey_shear_capacity_info_str'))[-1]
        return lines_2_df(tmp)

    def mass_plot(self, filename='楼层质量', **kwargs):
        for name, group in self.mass_density_info.groupby('塔号'):
            ploter.MPLLine({'YJK': [group['楼层质量'].tolist(),
                                    list(range(group.shape[0], 0, -1))
                                    ]
                            },
                           figsize=(8.58 / 2.54, 11 / 2.54),
                           xlabel='楼层质量$(kg)$', ylabel='楼层',
                           filename='%d 塔 %s.png' % (name, filename),
                           yticks=list(range(group.shape[0], 0, -1)),
                           yticklabels=group['层号'].tolist(),
                           **kwargs).draw()

            ploter.MPLBar({'YJK': [list(range(group.shape[0], 0, -1)),
                                   group['楼层质量'].tolist()
                                   ]
                           },
                          bar_type='h',
                          figsize=(8.58 / 2.54, 11 / 2.54),
                          xlabel='楼层质量$(kg)$', ylabel='楼层',
                          filename='%d 塔 %sbar.png' % (name, filename),
                          **kwargs).draw(lim={'下层质量的1.5倍': [list(range(group.shape[0], 1, -1)),
                                                            [x * 1.5 for x in group['楼层质量'].tolist()[1:]]
                                                            ]
                                              })
            return '%d 塔 %sbar.png' % (name, filename)

    def mass_density_plot(self, filename='单位面积质量', **kwargs):
        for name, group in self.mass_density_info.groupby('塔号'):
            ploter.MPLLine({'YJK': [group['单位面积质量'].tolist(),
                                    list(range(group.shape[0], 0, -1))
                                    ]
                            },
                           figsize=(8.58 / 2.54, 11 / 2.54),
                           xlabel='单位面积楼层质量$(kg/m^2)$', ylabel='楼层',
                           filename='%d 塔 %s' % (name, filename),
                           yticks=list(range(group.shape[0], 0, -1)),
                           yticklabels=group['层号'].tolist(),
                           **kwargs).draw()

    def stiffness_plot(self, filename='侧移刚度', **kwargs):
        for name, group in self.stiffness.groupby('TowerNo'):
            ploter.MPLLine({'YJK': [group['RJX3'].tolist()[2:],
                                    list(range(1, group.shape[0]+1))[2:]
                                    ]
                            },
                           figsize=(8.58 / 2.54, 11 / 2.54),
                           xlabel='X方向侧移刚度\n(地震剪力与地震层间位移的比)', ylabel='楼层',
                           filename='%d 塔 X 方向 %s.png' % (name, filename),
                           yticks=list(range(1, group.shape[0]+1))[2:],
                           yticklabels=group['FloorNo'].astype(int).tolist()[2:],
                           **kwargs).draw()
            ploter.MPLLine({'YJK': [group['RJY3'].tolist()[2:],
                                    list(range(1, group.shape[0]+1))[2:]
                                    ]
                            },
                           figsize=(8.58 / 2.54, 11 / 2.54),
                           xlabel='Y方向侧移刚度\n(地震剪力与地震层间位移的比)', ylabel='楼层',
                           filename='%d 塔 Y 方向 %s.png' % (name, filename),
                           yticks=list(range(1, group.shape[0]+1))[2:],
                           yticklabels=group['FloorNo'].astype(int).tolist()[2:],
                           **kwargs).draw()

    def shear_capacity_plot(self, filename='层受剪承载力', **kwargs):
        for name, group in self.storey_shear_capacity_info.groupby('塔号'):
            ploter.MPLBar({'YJK': [list(range(group.shape[0], 0, -1))[:-2],
                                   group['X向承载力'].tolist()[:-2]
                                   ]
                           },
                          bar_type='h',
                          figsize=(8.58 / 2.54, 11 / 2.54),
                          xlabel='X方向层受剪承载力', ylabel='楼层',
                          filename='%d 塔 X 方向 %s.png' % (name, filename),

                          **kwargs).draw(lim={'上层的80%': [list(range(group.shape[0]-1, 0, -1))[:-2],
                                                         [x * 0.8 for x in group['X向承载力'].tolist()[1:-2]]
                                                         ]
                                              }
                                         )
            ploter.MPLBar({'YJK': [list(range(group.shape[0], 0, -1))[:-2],
                                   group['Y向承载力'].tolist()[:-2]
                                   ]
                           },
                          bar_type='h',
                          figsize=(8.58 / 2.54, 11 / 2.54),
                          xlabel='Y方向层受剪承载力', ylabel='楼层',
                          filename='%d 塔 Y 方向 %s.png' % (name, filename),

                          **kwargs).draw(lim={'上层的80%': [list(range(group.shape[0] - 1, 0, -1))[:-2],
                                                         [x * 0.8 for x in group['Y向承载力'].tolist()[1:-2]]
                                                         ]
                                              }
                                         )

    def building_stable_plot(self, filename='刚重比', **kwargs):
        for name, group in self.building_stable_info.eq.groupby('塔号'):
            ploter.MPLLine({'YJK': [group['X刚重比'].tolist(),
                                    list(range(group.shape[0]))]},
                           filename='%d 塔 X 方向地震作用 %s.png' % (name, filename),
                           xlabel='X方向刚重比(地震)', ylabel='楼层',
                           figsize=(8.58 / 2.54, 11 / 2.54),
                           vlines=[10, 20],
                           yticks=list(range(group.shape[0])),
                           yticklabels=group['层号'].astype(int).tolist(),
                           **kwargs
                           ).draw()
            ploter.MPLLine({'YJK': [group['Y刚重比'].tolist(),
                                    list(range(group.shape[0]))]},
                           filename='%d 塔 Y 方向地震作用 %s.png' % (name, filename),
                           xlabel='Y方向刚重比(地震)', ylabel='楼层',
                           figsize=(8.58 / 2.54, 11 / 2.54),
                           vlines=[10, 20],
                           yticks=list(range(group.shape[0])),
                           yticklabels=group['层号'].astype(int).tolist(),
                           **kwargs
                           ).draw()


class BuildingStableInfo(object):

    def __init__(self, content):
        content = content.replace(':', '')
        __lst = [x.strip() for x in re.split(r'\n\n', content)]
        self.eq = lines_2_df(__lst[__lst.index('地震') + 1])
        self.wind = lines_2_df(__lst[__lst.index('风荷载') + 1])


def lines_2_df(content: str):

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


def lines_2_dict(content: str):

    if isinstance(content, str):
        lst_lines = [x.strip() for x in re.split('\n', content)]
        lst_info = []
        for __item in lst_lines:
            if __item.find(':') > 0:
                lst_info.extend([x.strip() for x in __item.split(':')])
        return dict(zip(lst_info[::2], lst_info[1::2]))
    else:
        print('类型错误')


if __name__ == '__main__':

    dfp = utility.FilePath()
    wmass_file = dfp.full_name('wmass.out')
    with open(wmass_file, 'r') as f:
        wmass = Wmass(f.read())
        print(wmass.design_info['嵌固端所在层号(层顶嵌固)'])
        wmass.mass_plot(filename='楼层质量测试')
        wmass.mass_density_plot()
        wmass.stiffness_plot()
        wmass.shear_capacity_plot()
        wmass.building_stable_plot()
        # wmass.design_info['']
