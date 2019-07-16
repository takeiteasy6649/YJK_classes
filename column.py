#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/5/16 22:45
# @File    : Column.py

import re
import math
import pandas as pd
import time

from material import Concrete
from utility import Greece2Eng
from utility import str_2_dict
from loadcombine import LoadCombine


# 计时装饰器
def timer(func):
    def wrapper(*args, **kwargs):
        time.time()
        result = func(*args, **kwargs)
        print('func takes %.3f seconds' % time.process_time())
        return result
    return wrapper


# 控制工况类: 基类
class ControlForce(object):

    def __init__(self, lc: int, **kwargs):
        try:
            self.load_case = int(lc)
            for key, value in kwargs.items():
                setattr(self, key, float(value))
        except TypeError:
            print('参数错误')

    @property
    def dict(self):
        return self.__dict__

    @property
    def str(self):
        return str(self.__dict__)

    @property
    def series(self):
        return pd.Series(self.__dict__)


# 控制工况类: 弯矩
class Moment(ControlForce):

    def __init__(self, lc: int, **kwargs):
        super().__init__(lc, **kwargs)
        try:
            dir_pos = re.findall(r"As([a-z]+?)'", self.str)[0]
            self.direction = dir_pos[0] if len(dir_pos) == 2 else None
            self.position = dir_pos[-1] if len(dir_pos) > 0 else None
        except ValueError:
            print('参数错误')


# 控制工况类: 轴力
class AxialForce(ControlForce):

    def __init__(self, lc: int, **kwargs):
        super().__init__(lc, **kwargs)

        self.Rsv = self.Rsv / 100.0 if hasattr(self, 'Rsv') is True else pd.NaT
        self.Rs = self.Rs / 100.0 if hasattr(self, 'Rs') is True else pd.NaT


# 控制工况类: 剪力
class ShearForce(ControlForce):

    def __init__(self, lc: int, **kwargs):
        super().__init__(lc, **kwargs)

    @property
    def direction(self):
        try:
            direction = re.findall(r"Asv([a-z]+?)'", self.str)
            return direction[0] if len(direction) > 0 else None
        except ValueError:
            print('参数错误')
        except IndexError:
            print(re.findall(r"Asv([a-z]+?)'", self.str))


# 控制工况类: 节点核芯区
class JointForce(ControlForce):

    def __init__(self, lc: int, **kwargs):
        super().__init__(lc, **kwargs)

    @property
    def direction(self):
        try:
            direction = re.findall(r"Vj([a-z]+?)'", self.str)
            return direction if len(direction) > 0 else None
        except ValueError:
            print('参数错误')
        except IndexError:
            print(re.findall(r"Vj([a-z]+?)'", self.str))


# 截面类
class Section(object):

    def __init__(self, sec_type, sec_dim_name, sec_dim_data, cover=20):
        """
        all param send in is considered with units in 'mm'
        :param sec_type:
        :param sec_dim_name:
        :param sec_dim_data:
        :param cover:
        """
        try:
            self.section_type = int(sec_type)
        except ValueError:
            print('截面类型参数错误')

        try:
            self.cover = int(cover)
        except ValueError:
            print('保护层参数错误')

        sdn = sec_dim_name[0].split('*') if len(sec_dim_name) > 0 else []

        if len(sec_dim_data) > 0:

            if sec_dim_data[0].find('Ang') >= 0:
                sdd = sec_dim_data[0].split()[0].split('*')
            else:
                sdd = sec_dim_data[0].split('*')
        else:
            sdd = []

        self.section_dict = dict(zip(sdn, sdd)) if len(sdn) == len(sdd) else None
        for key, value in self.section_dict.items():
            setattr(self, key, value)

    # 截面面积
    @property
    def area(self):
        """
        cal the area of section
        :return:
        """
        area = pd.NaT

        # 矩形截面
        if self.section_type in [1, 13, 15]:
            b = float(self.B) if hasattr(self, 'B') else pd.NaT
            h = float(self.H) if hasattr(self, 'H') else pd.NaT
            try:
                area = b*h
            except ValueError:
                print('参数类型错误')
            except TypeError:
                print('%s, %s' % (b, h))
        # 圆形截面
        elif self.section_type in [3, ]:
            try:
                area = math.pi * pow(float(self.Dr), 2) / 4 if hasattr(self, 'Dr') else pd.NaT
            except TypeError:
                print('%s' % self.Dr if hasattr(self, 'Dr') else pd.NaT)
        elif self.section_type in [103, 105, ]:
            try:
                area = math.pi * pow(float(self.B), 2) / 4 if hasattr(self, 'B') else pd.NaT
            except TypeError:
                print('%s' % self.Dr if hasattr(self, 'Dr') else pd.NaT)
        # 其它截面暂时返回空值

        return area


# 柱类
class Column:

    __LIST = []

    def __init__(self, content, *args):
        """
        init deal with 'content' from 'wpj*.out'
        1. findall param in LIST
        2. findall load_case start with '('
        3. get the information given in CHINESE
        :param content:
        :param args:
        """
        content = re.sub(r'=\s+', '=', content)
        content = re.sub(r'\(%\)', '', content)
        __lst_attr = self.__LIST

        # args: for extend
        for __item in args:
            __lst_attr.extend(__item)

        for __item in __lst_attr:
            __pattern = re.compile(__item + r'=(\S+)')

            __lst_got = re.findall(__pattern, content)
            __value = __lst_got[0] if len(__lst_got) > 0 else None

            setattr(self, '%s' % Greece2Eng.replace(__item), __value)

        # load_case & forces
        __lst_force = []
        for __force in re.findall(r'\s{2,}[(]\s(.*?)\n', content):
            __lc = int(__force.split(')')[0].strip())
            __dct_force = str_2_dict(__force.split(')')[1], '=')
            __lst_force.append((__lc, __dct_force))

        self.lst_force_data = __lst_force

        # 截面类型变量在括号内，该行共有3对括号，位置受该参数控制，开始于0
        self.POSITION_SEC_TYPE = 1

        # 搜索括号中内容的pattern
        self.PATTERN_BRACKET = re.compile(r'[(](.*?)[)]')

        # 搜索右括号'）'和'('之间内容的pattern，该数据为截面类型的字母
        self.PATTERN_NUM_in_BRA__mm_in_BRA = re.compile(r'[(]\d+[)](.*?)[(]mm[)]')

        # 搜索'(mm)='和'\n'之间内容的pattern，
        self.PATTERN_EQUAL_2_END = re.compile(r'[(]mm[)]=(.*?)\n')

        # 搜索'('和'\n'之间内容的pattern，
        self.PATTERN_LEFT_BRACKET_2_END = re.compile(r'\s{2,}[(]\s(.*?)\n')

        # section
        self.section = Section(re.findall(self.PATTERN_BRACKET, content)[self.POSITION_SEC_TYPE],
                               re.findall(self.PATTERN_NUM_in_BRA__mm_in_BRA, content),
                               re.findall(self.PATTERN_EQUAL_2_END, content))

        # material
        self.concrete = Concrete(self.Rcc) if hasattr(self, 'Rcc') else None
        self.steel = Concrete(self.Rsc) if hasattr(self, 'Rsc') else None


# 混凝土柱类
class ConcreteColumn(Column):

    def __init__(self, content, *args):
        super().__init__(content, *args)

        self.info = ' '.join(re.findall(r'[\u4e00-\u9fa5]+', content))

        if content.find('节点核芯区设计结果') >= 0:
            self.has_joint = True
        else:
            self.has_joint = False

    @property
    def moment(self):
        __lst_moment = []
        for __lc, __dct_force in self.lst_force_data:
            if str(__dct_force).find('M') >= 0:
                __lst_moment.append(Moment(__lc, **__dct_force))

        return __lst_moment

    @property
    def shear(self):
        __lst_shear = []
        for __lc, __dct_force in self.lst_force_data:
            if str(__dct_force).find('V') >= 0 > str(__dct_force).find('Vj'):
                __lst_shear.append(ShearForce(__lc, **__dct_force))
        return __lst_shear

    @property
    def axial(self):
        __lst_axial = []
        for __lc, __dct_force in self.lst_force_data:
            if str(__dct_force).find('Nu') >= 0:
                __lst_axial.append(AxialForce(__lc, **__dct_force))
        return __lst_axial

    @property
    def joint(self):
        __lst_joint = []
        for __lc, __dct_force in self.lst_force_data:
            if str(__dct_force).find('Vj') >= 0:
                __lst_joint.append(JointForce(__lc, **__dct_force))
        return __lst_joint

    def shear_axial_ratio(self, load_combine):

        if isinstance(load_combine, LoadCombine):
            tmp = []
            for __shear in self.shear:
                __gamma_re = 0.85 if load_combine.control_by_eq(__shear.load_case) else 1.0
                __shear_axial_ratio_limit = 0.2 if float(getattr(self, 'lambdac')) > 2 else 0.15

                v_max = max(abs(float(__shear.Vx)), abs(float(__shear.Vy))) if hasattr(
                    __shear, 'Vx') and hasattr(__shear, 'Vy') else pd.NaT

                tmp.append(v_max * 1000 * __gamma_re / (
                    __shear_axial_ratio_limit * self.concrete.beta_c * self.concrete.fc * self.section.area))

            return max(tmp)
        else:
            raise ValueError

    @ property
    def shear_capacity_utilization(self):
        return ShearCapacityUtilization(self.shear, float(getattr(self, 'CB_XF')), float(getattr(self, 'CB_YF')))


# 抗剪承载力利用率
class ShearCapacityUtilization(object):

    def __init__(self, shear: list, cb_xf, cb_yf):
        for item in shear:
            if isinstance(item, ShearForce):
                if item.direction == 'x':
                    self.x = abs(getattr(item, 'Vx') / cb_xf)
                elif item.direction == 'y':
                    self.y = abs(getattr(item, 'Vy') / cb_yf)
                elif item.direction is None:
                    self.x = abs(getattr(item, 'Vx') / cb_xf)
                    self.y = abs(getattr(item, 'Vy') / cb_yf)
                else:
                    print('Direction Error:%s' % item.direction)
            else:
                print('Type Error')


# @ timer
# def main():
#
#     # 对话框取得文件夹名称
#
#     data_path = FilePath()
#
#     file_name = os.path.join(data_path.input_path, 'wpj3.out')
#
#     with open(file_name, 'r') as f:
#         wpj = Wpj.Wpj(f.read())
#         lcc = LoadCombine(wpj.combine)
#         lst = []
#         for item in wpj.columns:
#             if item.find('砼柱') >= 0:
#                 lst.append(ConcreteColumn(item, LIST_SIGN, LIST_SIGN_CONCRETE))
#
#         fff = []
#         for item in lst:
#             fff.append(item.shear_axial_ratio(lcc))
#
#         fff = np.array(fff)
#         font = dict(family='KaiTi', color='black', weight='normal', size=10.5)
#         plt.figure(figsize=(17.16 / 2.54, 11 / 2.54))
#         plt.grid(alpha=0.5, linestyle="-.", linewidth=0.3)
#
#         plt.scatter(range(len(fff)), fff, c=1 - fff, marker='.')
#
#         plt.text(np.where(fff == np.max(fff))[0][0],
#                  max(fff),
#                  '$%.2f$' % max(fff),
#                  color='firebrick'
#                  )
#
#         plt.xlabel('构件编号', fontdict=font)
#         plt.ylabel('剪压比', fontdict=font)
#
#         xmin, xmax = plt.xlim()
#         plt.hlines(1, xmin, xmax, colors='r', linestyles='--')
#
#         plt.tight_layout()
#         plt.savefig(os.path.join(data_path.current_result_path, '剪压比'), transparent=True, dpi=300)
#         plt.show()
#
#         fff = []
#         for item in lst:
#             for item_m in item.moment:
#                 fff.append([item_m.N, item_m.Mx, item_m.My])
#         # fff = list(set(fff))
#         tmp_t = pd.DataFrame(fff[::2], columns=['N', 'Mx', 'My'])
#         tmp_b = pd.DataFrame(fff[1::2], columns=['N', 'Mx', 'My'])
#         tmp_t.to_excel('PMM_t.xlsx')
#         tmp_b.to_excel('PMM_b.xlsx')
#
#         fff = []
#         for item in lst:
#             fff.append(item.shear_capacity_utilization.x)
#
#         fff = np.array(fff)
#         font = dict(family='KaiTi', color='black', weight='normal', size=10.5)
#         plt.figure(figsize=(17.16 / 2.54, 11 / 2.54))
#         plt.grid(alpha=0.5, linestyle="-.", linewidth=0.3)
#
#         plt.scatter(range(len(fff)), fff, c=1 - fff, marker='.')
#
#         plt.text(np.where(fff == np.max(fff))[0][0],
#                  max(fff),
#                  '$%.2f$' % max(fff),
#                  color='firebrick'
#                  )
#
#         plt.xlabel('构件编号', fontdict=font)
#         plt.ylabel('抗剪承载力利用率', fontdict=font)
#
#         xmin, xmax = plt.xlim()
#         plt.hlines(1, xmin, xmax, colors='r', linestyles='--')
#
#         plt.tight_layout()
#         plt.savefig(os.path.join(data_path.current_result_path, '抗剪承载力利用率'), transparent=True, dpi=300)
#         plt.show()
#
#         fff = []
#         for item in lst:
#             fff.append(item.axial[0].Uc)
#
#         fff = np.array(fff)
#         font = dict(family='KaiTi', color='black', weight='normal', size=10.5)
#         plt.figure(figsize=(17.16 / 2.54, 11 / 2.54))
#         plt.grid(alpha=0.5, linestyle="-.", linewidth=0.3)
#
#         plt.scatter(range(len(fff)), fff, c=1 - fff, marker='.')
#
#         plt.text(np.where(fff == np.max(fff))[0][0],
#                  max(fff),
#                  '$%.2f$' % max(fff),
#                  color='firebrick'
#                  )
#
#         plt.xlabel('构件编号', fontdict=font)
#         plt.ylabel('轴压比', fontdict=font)
#
#         xmin, xmax = plt.xlim()
#         plt.hlines(1, xmin, xmax, colors='r', linestyles='--')
#
#         plt.tight_layout()
#         plt.savefig(os.path.join(data_path.current_result_path, '轴压比'), transparent=True, dpi=300)
#         plt.show()
#
#         # test hist
#         plt.figure(figsize=(17.16 / 2.54, 11 / 2.54))
#         plt.grid(alpha=0.5, linestyle="-.", linewidth=0.3)
#
#         n, bins, patches = plt.hist(fff,
#                                     bins=np.arange(0, max(fff)+0.1, 0.1),
#                                     density=False,
#                                     rwidth=0.8,
#                                     align='mid')
#
#         total = np.sum(n)
#         for ct in range(len(n)):
#             plt.text(bins[ct],
#                      n[ct],
#                      '{:.1%}'.format(n[ct]/total),
#                      )
#
#         plt.xlabel('轴压比', fontdict=font)
#         plt.ylabel('构件个数', fontdict=font)
#
#         plt.tight_layout()
#         plt.savefig(os.path.join(data_path.current_result_path, '轴压比分布'), transparent=True, dpi=300)
#         plt.show()
#
#     # with open(file_name, 'r') as f:
#     #     pass
#
#     return lst, fff
#
#
# if __name__ == '__main__':
#
#     start = time.time()
#
#     # 柱编号
#     SIGN_COLUMN_NUMBER = 'N-C'
#     # 柱布置角度
#     SIGN_ANGLE = 'Ang'
#     # 混凝土保护层厚度
#     SIGN_CONCRETE_COVER = 'Cover'
#
#     # 柱长度
#     SIGN_COLUMN_LENGTH = 'Lc'
#     # 不要修改以下两行
#     SIGN_COLUMN_LENGTH_X = SIGN_COLUMN_LENGTH + 'x'
#     SIGN_COLUMN_LENGTH_Y = SIGN_COLUMN_LENGTH + 'y'
#
#     # 柱长度系数
#     SIGN_COLUMN_LENGTH_ADJUST_FACTOR = 'C'
#     # 不要修改以下两行
#     SIGN_COLUMN_LENGTH_ADJUST_FACTOR_X = SIGN_COLUMN_LENGTH_ADJUST_FACTOR + 'x'
#     SIGN_COLUMN_LENGTH_ADJUST_FACTOR_Y = SIGN_COLUMN_LENGTH_ADJUST_FACTOR + 'y'
#
#     # 抗震等级
#     SIGN_SEISMIC_GRADE = 'Nfc'
#     # 抗震构造等级
#     SIGN_SEISMIC_CONSTRUCT_GRADE = 'Nfc_gz'
#
#     # 混凝土强度等级
#     SIGN_CONCRETE_STRENGTH_GRADE = 'Rcc'
#     # 纵筋强度等级
#     SIGN_REBAR_GRADE = 'Fy'
#     # 箍筋强度等级
#     SIGN_STIRRUP_GRADE = 'Fyv'
#
#     # 钢材强度等级
#     SIGN_STEEL_GRADE = 'Rsc'
#
#     # 活荷载折减系数
#     SIGN_LIVE_LOAD_REDUCTION = 'livec'
#
#     # SIGN
#     SIGN_ADJUST_MOMENT_UPPER = 'ηmu'
#     SIGN_ADJUST_MOMENT_DOWN = 'ηmd'
#     SIGN_ADJUST_SHEAR_UPPER = 'ηvu'
#     SIGN_ADJUST_SHEAR_DOWN = 'ηvd'
#
#     # 剪跨比
#     SIGN_COLUMN_SHEAR_SPAN_RATIO = 'λc'
#
#     # 抗剪承载力
#     SIGN_CB_XF = 'CB_XF'
#     SIGN_CB_YF = 'CB_YF'
#
#     # 截面类型变量在括号内，该行共有3对括号，位置受该参数控制，开始于0
#     POSITION_SEC_TYPE = 1
#
#     # 搜索括号中内容的pattern
#     PATTERN_BRACKET = re.compile(r'[(](.*?)[)]')
#
#     # 搜索右括号'）'和'('之间内容的pattern，该数据为截面类型的字母
#     PATTERN_NUM_in_BRA__mm_in_BRA = re.compile(r'[(]\d+[)](.*?)[(]mm[)]')
#
#     # 搜索'(mm)='和'\n'之间内容的pattern，
#     PATTERN_EQUAL_2_END = re.compile(r'[(]mm[)]=(.*?)\n')
#
#     # 搜索'('和'\n'之间内容的pattern，
#     PATTERN_LEFT_BRACKET_2_END = re.compile(r'\s{2,}[(]\s(.*?)\n')
#
#     # Column的11个属性，其余属性放到子类
#     LIST_SIGN = [SIGN_COLUMN_NUMBER,  # 1
#                  SIGN_ANGLE,  # 2
#                  SIGN_COLUMN_LENGTH_ADJUST_FACTOR_X,  # 3
#                  SIGN_COLUMN_LENGTH_ADJUST_FACTOR_Y,  # 4
#                  SIGN_COLUMN_LENGTH_X,  # 5
#                  SIGN_COLUMN_LENGTH_Y,  # 6
#                  SIGN_SEISMIC_GRADE,  # 7
#                  SIGN_SEISMIC_CONSTRUCT_GRADE,  # 8
#                  SIGN_LIVE_LOAD_REDUCTION,  # 9
#                  SIGN_CB_XF,  # 10
#                  SIGN_CB_YF,  # 11
#                  ]
#
#     # 混凝土柱的属性，子类引用，本类不使用，放在此处方便修改
#     LIST_SIGN_CONCRETE = [SIGN_CONCRETE_COVER,  # 1
#                           SIGN_CONCRETE_STRENGTH_GRADE,  # 2
#                           SIGN_REBAR_GRADE,  # 3
#                           SIGN_STIRRUP_GRADE,  # 4
#                           SIGN_COLUMN_SHEAR_SPAN_RATIO,  # 5
#                           ]
#     aa, bb = main()
