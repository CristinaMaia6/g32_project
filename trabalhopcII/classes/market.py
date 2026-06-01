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
    att = ['_market_id', '_title', '_category']
    header = 'Markets'
    des = ['Id', 'Title', 'Category']

    def __init__(self, market_id, title, category):
        super().__init__()
        market_id = Market.get_id(market_id)
        self._market_id = market_id
        self._title = title
        self._category = category
        
        Market.obj[market_id] = self
        Market.lst.append(market_id)

    @property
    def market_id(self): return self._market_id
    @market_id.setter
    def market_id(self, value): self._market_id = value

    @property
    def title(self): return self._title
    @title.setter
    def title(self, value): self._title = value

    @property
    def category(self): return self._category
    @category.setter
    def category(self, value): self._category = value
