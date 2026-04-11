#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 10 10:49:07 2026

@author: franciscasilva
"""

from classes.gclass import Gclass

class Market(Gclass):
    obj = dict()
    lst = list()
    pos = 0
    sortkey = ''
    att = ['_id', '_title', '_category']
    header = 'Markets'
    des = ['Id', 'Title', 'Category']

    def __init__(self, id, title, category):
        super().__init__()
        id = Market.get_id(id)
        self._id = id
        self._title = title
        self._category = category
        
        Market.obj[id] = self
        Market.lst.append(id)

    @property
    def id(self): return self._id
    @id.setter
    def id(self, value): self._id = value

    @property
    def title(self): return self._title
    @title.setter
    def title(self, value): self._title = value

    @property
    def category(self): return self._category
    @category.setter
    def category(self, value): self._category = value