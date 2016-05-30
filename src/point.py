# -*- coding: utf-8 -*-


class Point(object):
    def __init__(self, x=None, y=None, weight=1.0):
        self.x = x
        self.y = y
        self.weight = weight

    @property
    def cord(self):
        return self.x, self.y

    def update(self, x, y):
        self.x += x
        self.y += y

    def save(self):
        return (
            self.x,
            self.y,
            self.weight
        )
