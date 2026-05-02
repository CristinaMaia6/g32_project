# -*- coding: utf-8 -*-
"""
Created on Mon Apr 20 02:17:02 2026

@author: crism
"""

import sys
import os
import datetime

# Imports das tuas classes (ajustados para a estrutura de pastas)
from classes.farmer import Farmer
from classes.market_type import MarketType
from classes.market import Market
from classes.transaction import Transactions
from classes.worker import Worker

def menu_principal():
    print('\nSISTEMA DE GESTÃO AGRÍCOLA')
    print('--------------------------')
    print('1 - Farmers')
    print('2 - Market Types')
    print('3 - Markets')
    print('4 - Transactions')
    print('5 - Workers')
    print('q - Quit')
    print('--------------------------')
    return input('Escolha uma classe: ')

def run_app():
    db_path = '../data/trabalhopc_project.db'
    
    while True:
        escolha = menu_principal()
        
        if escolha == 'q':
            break
            
        # Define qual a test_class e o objeto de exemplo 'ob' para o auto-incremento inicial
        if escolha == '1':
            test_class = Farmer
            ob = '0;Nome;2026-01-01'
        elif escolha == '2':
            test_class = MarketType
            ob = '0;Tipo'
        elif escolha == '3':
            test_class = Market
            ob = '0;Titulo;Categoria'
        elif escolha == '4':
            test_class = Transactions
            ob = '0;1;1;2026-01-01;0.0'
        elif escolha == '5':
            test_class = Worker
            ob = '0;Info;1'
        else:
            print("Opção inválida!")
            continue

        # Carrega os dados
        test_class.read(db_path)

        op = ''
        while op != 'q':
            print('')
            print(f'GESTÃO DE: {test_class.__name__}')
            print('Choose one letter for select the option')
            print('---------------')
            print('l - list')
            print('b - beginning')
            print('n - next')
            print('p - previous')
            print('e - end')
            print('---------------')
            print('i - insert')
            print('m - modify')
            print('r - remove')
            print('---------------')
            print('s - sort by attribute')
            print('f - find by attribute')
            print('---------------')
            print('q - back to main menu')
            print('---------------')
            
            p = test_class.current()
            print(f'\nREGISTO ATUAL: {p}')
            
            op = input('?')
            
            if op == 'b':
                test_class.first()
            elif op == 'n':
                test_class.nextrec()
            elif op == 'p':
                test_class.previous()
            elif op == 'e':
                test_class.last()
                
            elif op == 'i':
                p1 = None
                # Se a lista estiver vazia, cria um objeto temporário para ler os atributos
                if len(test_class.lst) == 0:
                    p = eval('test_class.from_string("' + ob + '")')
                    p1 = p
                
                str_list = list(p.__dict__.keys())
                attrib = str_list[0]
                print('leave blank to auto-increment')
                id_val = input(f'{attrib[1:]} = ')
                
                if id_val == "":
                    id_val = 0
                else:
                    id_val = int(id_val)
                
                strarg = f'test_class({id_val}'
                for i in range(1, len(str_list)):
                    attrib = str_list[i]
                    # Tenta obter o tipo do atributo atual do objeto p
                    atype = type(getattr(p, attrib))
                    value = input(f'{attrib[1:]} = ')
                    
                    if atype == datetime.date or atype == str:
                        strarg += f',"{value}"'
                    else:
                        strarg += f',{atype(value)}'
                strarg += ')'
                
                if p1 != None:
                    test_class.remove(getattr(p, str_list[0]))
                
                print(f"Executing: {strarg}")
                pobj = eval(strarg)
                code = getattr(pobj, str_list[0])
                test_class.insert(code)

            elif op == 'm':
                if p:
                    str_list = list(p.__dict__.keys())
                    attrib = str_list[0]
                    id_val = input(f'Record {attrib[1:]} to modify = ') 
                    if id_val != "":
                        id_val = int(id_val)
                        obj = test_class.current(id_val)
                        if obj:
                            print('Leave blank or new value to modify')
                            for attrib in str_list[1:]:
                                value = input(f'{attrib[1:]} = ') 
                                if value != "":
                                    atype = type(getattr(p, attrib))
                                    if atype == datetime.date:
                                        setattr(obj, attrib, datetime.date.fromisoformat(value))
                                    else:
                                        setattr(obj, attrib, atype(value))
                            test_class.update(id_val)
                else:
                    print("Nenhum registo selecionado.")

            elif op == 'r':
                if p:
                    str_list = list(p.__dict__.keys())
                    attrib = str_list[0]
                    cod = int(input(f'ID {attrib[1:]} to remove = '))
                    if cod in test_class.lst:
                        print(test_class.obj[cod])
                        if input('Confirm delete (y/n)? ').upper() == 'Y':
                            test_class.remove(cod)
                else:
                    print("Lista vazia.")

            elif op == 'l':
                print(f"\nLISTA DE {test_class.__name__.upper()}:")
                for code in test_class.lst:
                    print(test_class.obj[code])

            elif op == 's':
                attrib = input('Sort by attribute name (without _): ')
                if '_' + attrib in list(p.__dict__.keys()):
                    rev = input('Reverse (y/n)? ').lower() == 'y'
                    codep = p.id if p else None
                    test_class.sort('_' + attrib, rev) # Adiciona o _ automaticamente
                    for code in test_class.lst:
                        print(test_class.obj[code])
                    if codep: test_class.current(codep)

            elif op == 'f':
                attrib = input('Attribute name (without _): ')
                if '_' + attrib in list(p.__dict__.keys()):
                    atype = type(getattr(p, '_' + attrib))
                    val = atype(input('Value to find: '))
                    fobjs = test_class.find(val, '_' + attrib)
                    if len(fobjs) > 0:
                        test_class.current(fobjs[0].id)
                        for o in fobjs: print(o)
                    else:
                        print("Nada encontrado.")

if __name__ == "__main__":
    run_app()