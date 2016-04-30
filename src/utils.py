# -*- coding: utf-8 -*-

import os
import sys

import numpy as np
from PyQt5 import QtCore, QtGui


def parse_curve_function(func):
    pars_list = [
        ('^', '**'), ('sin', 'np.sin'), ('cos', 'np.cos'), ('tg', 'np.tg'),
        ('ctg', 'np.ctg'), ('sqrt', 'np.sqrt'),
        ('e', str(sys.float_info.epsilon))
    ]
    if func:
        for i, j in pars_list:
            func = func.replace(i, j)

    return func


def parse_range(range_t):
    def _parser(p):
        try:
            i = p.index('/')
            p = p[:i+1] + p[i+1] + '.' + p[i+2:]
        except ValueError:
            pass
        return p

    if range_t:
        for i in ['[', ']']:
            range_t = range_t.strip(i)
        range_t = range_t.replace('pi', str(np.pi))
        range_t = range_t.split(',')
        range_t = [_parser(i) for i in range_t]
        range_t = map(eval, range_t)
    else:
        range_t = [0, 0, 0]

    return {
        'min': float(range_t[0]),
        'max': float(range_t[1]),
        'interval': float(range_t[2])
    }


def get_icon(name):
    path = get_icon_path(name)
    return QtGui.QIcon(path)


def get_pixmap(name):
    path = get_icon_path(name)
    pix = QtGui.QPixmap(path)
    pix = pix.scaled(20, 20, QtCore.Qt.KeepAspectRatio)
    return pix


def get_icon_path(name):
    basedir = os.path.join(os.getcwd(), 'icons')
    return os.path.join(basedir, name)
