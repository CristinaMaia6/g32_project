

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
    att = ['_id_transaction', '_id_farmer', '_id_market', '_transaction_date', '_amount']
    header = 'Transactions'
    des = ['Id', 'Farmer Id', 'Market Id', 'Date', 'Amount']

    def __init__(self, id_transaction, id_farmer, id_market, transaction_date, amount):
        super().__init__()
        
        self._id_transaction = int(float(id_transaction)) if id_transaction and str(id_transaction) != 'None' else 0
        self._id_farmer = int(float(id_farmer)) if id_farmer and str(id_farmer) != 'None' else 0
        self._id_market = int(float(id_market)) if id_market and str(id_market) != 'None' else 0
        
        if isinstance(transaction_date, str) and transaction_date != 'None':
            try:
                self._transaction_date = datetime.date.fromisoformat(transaction_date)
            except ValueError:
                self._transaction_date = transaction_date
        else:
            self._transaction_date = transaction_date
            
        self._amount = float(amount) if amount and str(amount) != 'None' else 0.0
        
        Transactions.obj[self._id_transaction] = self
        Transactions.lst.append(self._id_transaction)

    @property
    def id_transaction(self): return self._id_transaction
    @id_transaction.setter
    def id_transaction(self, value): self._id_transaction = value

    @property
    def transaction_date(self): return self._transaction_date
    @transaction_date.setter
    def transaction_date(self, value): self._transaction_date = value

    @property
    def amount(self): return self._amount
    @amount.setter
    def amount(self, value): self._amount = value

    @property
    def id_farmer(self): return self._id_farmer
    @id_farmer.setter
    def id_farmer(self, value): self._id_farmer = value

    @property
    def id_market(self): return self._id_market
    @id_market.setter
    def id_market(self, value): self._id_market = value
