#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 10 10:49:36 2026

@author: franciscasilva
"""

from classes.gclass import Gclass
import datetime

class Transactions(Gclass):
    obj = dict()
    lst = list()
    pos = 0
    sortkey = ''
    att = ['_id', '_farmer_id', '_market_id', '_transaction_date', '_amount']
    header = 'Transactions'
    des = ['Id', 'Farmer Id', 'Market Id', 'Date', 'Amount']

    def __init__(self, id, farmer_id, market_id, transaction_date, amount):
        super().__init__()
        
        self._id = int(float(id)) if id and str(id) != 'None' else 0
        self._farmer_id = int(float(farmer_id)) if farmer_id and str(farmer_id) != 'None' else 0
        self._market_id = int(float(market_id)) if market_id and str(market_id) != 'None' else 0
        
        if isinstance(transaction_date, str) and transaction_date != 'None':
            try:
                self._transaction_date = datetime.date.fromisoformat(transaction_date)
            except ValueError:
                self._transaction_date = transaction_date
        else:
            self._transaction_date = transaction_date
            
        self._amount = float(amount) if amount and str(amount) != 'None' else 0.0
        
        Transactions.obj[self._id] = self
        Transactions.lst.append(self._id)

    @property
    def id(self): return self._id
    @id.setter
    def id(self, value): self._id = value

    @property
    def transaction_date(self): return self._transaction_date
    @transaction_date.setter
    def transaction_date(self, value): self._transaction_date = value

    @property
    def amount(self): return self._amount
    @amount.setter
    def amount(self, value): self._amount = value

    @property
    def farmer_id(self): return self._farmer_id
    @farmer_id.setter
    def farmer_id(self, value): self._farmer_id = value

    @property
    def market_id(self): return self._market_id
    @market_id.setter
    def market_id(self, value): self._market_id = value