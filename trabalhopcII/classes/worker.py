#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 10 10:49:21 2026

"""

from classes.gclass import Gclass

class Worker(Gclass):
    obj = dict()
    lst = list()
    pos = 0
    sortkey = ''
    att = ['_worker_id', '_extra_info', '_farmer_id']
    header = 'Workers'
    des = ['Id', 'Extra Info', 'Farmer Id']

    def __init__(self, worker_id, extra_info, farmer_id):
        super().__init__()

        if worker_id is None or str(worker_id) == 'None':
            self._worker_id = 0 
        else:
            self._worker_id = int(float(worker_id))
            
        self._extra_info = extra_info

        if farmer_id is None or str(farmer_id) == 'None':
            self._farmer_id = 0
        else:
            self._farmer_id = int(float(farmer_id))
        
        Worker.obj[self._worker_id] = self
        Worker.lst.append(self._worker_id)

    @property
    def worker_id(self): return self._worker_id
    @worker_id.setter
    def worker_id(self, value): self._worker_id = value

    @property
    def extra_info(self): return self._extra_info
    @extra_info.setter
    def extra_info(self, value): self._extra_info = value

    @property
    def farmer_id(self): return self._farmer_id
    @farmer_id.setter
    def farmer_id(self, value): self._farmer_id = value