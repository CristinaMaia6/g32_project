#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 10 10:49:36 2026

@author: franciscasilva
"""

from classes.gclass import Gclass
import datetime

class Transaction(Gclass):
    obj = dict()
    lst = list()
    pos = 0
    sortkey = ''
    att = ['_id', '_transaction_date', '_amount', '_farmer_id', '_market_id']
    header = 'Transactions'
    des = ['Id', 'Date', 'Amount', 'Farmer Id', 'Market Id']

    def __init__(self, id, transaction_date, amount, farmer_id, market_id):
        super().__init__()
        id = Transaction.get_id(id)
        self._id = id
        
        if isinstance(transaction_date, str):
            self._transaction_date = datetime.date.fromisoformat(transaction_date)
        else:
            self._transaction_date = transaction_date
            
        self._amount = float(amount)
        self._farmer_id = int(farmer_id)
        self._market_id = int(market_id)
        
        Transaction.obj[id] = self
        Transaction.lst.append(id)

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