#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/7/5 17:31
# @File    : ETABS.py

import pandas as pd
from utility import FilePath


class Etabs(object):

    def __init__(self):

        self.dfp = FilePath(openfile=True)
        self.drift = pd.read_excel(self.dfp.input_file, sheet_name='Story Drifts', skiprows=[0, 2])
        print(self.drift)


if __name__ == '__main__':
    etabs = Etabs()
    print(etabs.dfp.input_file)
