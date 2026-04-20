#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 10 10:49:21 2026

@author: franciscasilva
"""

from classes.gclass import Gclass

class Worker(Gclass):
    obj = dict()
    lst = list()
    pos = 0
    sortkey = ''
    att = ['_id', '_extra_info', '_farmer_id']
    header = 'Workers'
    des = ['Id', 'Extra Info', 'Farmer Id']

    def __init__(self, id, extra_info, farmer_id):
        super().__init__()

        if id is None or str(id) == 'None':
            self._id = 0 
        else:
            self._id = int(float(id))
            
        self._extra_info = extra_info

        if farmer_id is None or str(farmer_id) == 'None':
            self._farmer_id = 0
        else:
            self._farmer_id = int(float(farmer_id))
        
        Worker.obj[self._id] = self
        Worker.lst.append(self._id)
    @property
    def id(self): return self._id
    @id.setter
    def id(self, value): self._id = value

    @property
    def extra_info(self): return self._extra_info
    @extra_info.setter
    def extra_info(self, value): self._extra_info = value

    @property
    def farmer_id(self): return self._farmer_id
    @farmer_id.setter
    def farmer_id(self, value): self._farmer_id = value