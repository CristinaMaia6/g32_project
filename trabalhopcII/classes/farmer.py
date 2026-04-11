#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 10 10:48:18 2026

@author: franciscasilva
"""

from classes.gclass import Gclass
import datetime

class Farmer(Gclass):
    obj = dict()
    lst = list()
    pos = 0
    sortkey = ''
    att = ['_id', '_name', '_creation_date']
    header = 'Farmers'
    des = ['Id', 'Name', 'Creation Date']

    def __init__(self, id, name, creation_date):
        super().__init__()
        id = Farmer.get_id(id)
        self._id = id
        self._name = name
        if isinstance(creation_date, str):
            self._creation_date = datetime.date.fromisoformat(creation_date)
        else:
            self._creation_date = creation_date
        
        Farmer.obj[id] = self
        Farmer.lst.append(id)

    @property
    def id(self): return self._id
    @id.setter
    def id(self, value): self._id = value

    @property
    def name(self): return self._name
    @name.setter
    def name(self, value): self._name = value

    @property
    def creation_date(self): return self._creation_date
    @creation_date.setter
    def creation_date(self, value): self._creation_date = value