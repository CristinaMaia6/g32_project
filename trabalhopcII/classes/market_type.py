# -*- coding: utf-8 -*-
"""
Created on Mon Apr 20 01:43:33 2026

@author: crism
"""

from classes.gclass import Gclass

class MarketType(Gclass):
    obj = dict()
    lst = list()
    pos = 0
    sortkey = ''
    # Os atributos devem coincidir com as colunas da tabela SQL
    att = ['_id_market', '_market_type']
    header = 'Tipos de Mercado'
    des = ['Id Mercado', 'Tipo de Mercado']

    def __init__(self, id_market, market_type):
        super().__init__()
        # Usamos o id_market como a chave principal desta tabela
        self._id_market = int(id_market)
        self._market_type = market_type
        
        # Guardar o objeto nos dicionários e listas da classe
        MarketType.obj[self._id_market] = self
        MarketType.lst.append(self._id_market)

    @property
    def id_market(self): 
        return self._id_market
    
    @id_market.setter
    def id_market(self, value): 
        self._id_market = value

    @property
    def market_type(self): 
        return self._market_type
    
    @market_type.setter
    def market_type(self, value): 
        self._market_type = value