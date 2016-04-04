import numpy as np


class Utils(object):
    @staticmethod
    def parse_curve_function(func):
        pars_list = [
            ('^', '**'), ('sin', 'np.sin'), ('cos', 'np.cos'), ('tg', 'np.tg'),
            ('ctg', 'np.ctg'), ('sqrt', 'np.sqrt')
        ]
        if func:
            for i, j in pars_list:
                func = func.replace(i, j)

        return func

    @staticmethod
    def parse_range(range_t):
        if range_t:
            for i in ['[', ']']:
                range_t = range_t.strip(i)
            range_t = range_t.replace('pi', str(np.pi))
            range_t = range_t.split(',')
            range_t = map(eval, range_t)
        else:
            range_t = [0, 0, 0]

        return {
            'min': float(range_t[0]),
            'max': float(range_t[1]),
            'interval': float(range_t[2])
        }
