# -*- coding: utf-8 -*-
"""
Created on Mon Apr 20 02:17:02 2026

@author: crism
"""

from classes.farmer import Farmer
from classes.market import Market
from classes.market_type import MarketType
from classes.worker import Worker
from classes.transaction import Transactions
from datafile import filename
import datetime

# 1. Configuração inicial
db_path = filename + 'trabalhopc_project.db'
classes_disponiveis = {
    'f': Farmer,
    'm': Market,
    'mt': MarketType,
    'w': Worker,
    't': Transactions
}

# Carregar dados
for cls in classes_disponiveis.values():
    cls.read(db_path)

def mostrar_registos(cls):
    print(f"\n--- {cls.header.upper()} ---")
    
    # 1. Criar a legenda das colunas usando a lista 'des' da classe
    # Isto vai imprimir algo como: "Estrutura: Id | Name | Creation Date"
    guia = " | ".join(cls.des)
    print(f"{guia}")

    print("-" * 50)

    # 2. Verificar se há dados
    if not cls.lst:
        print("Ainda não existem registos nesta tabela.")
        return

    # 3. Listar os dados reais
    for idx in cls.lst:
        obj = cls.obj[idx]
        # Vamos buscar os valores usando a lista 'att' (_id, _name, etc)
        valores = [str(getattr(obj, attr)) for attr in cls.att]
        print(" | ".join(valores))


def adicionar_registo(cls):
    print(f"\n--- Adicionar {cls.header} ---")
    obj = None  # Inicializamos a None para evitar o erro de 'UnboundLocalError'

    # Se for um farmer
    if cls == Farmer:
        id = Farmer.get_id(0)
        nome = input("Nome: ")
        data = input("Data de Criação (AAAA-MM-DD): ")
        obj = Farmer(id, nome, data)

    # Se for um market
    elif cls == Market:
        id = Market.get_id(0)
        titulo = input("Título do Mercado: ")
        categoria = input("Categoria: ")
        obj = Market(id, titulo, categoria)

    # Se for uma transaction
    elif cls == Transactions:
        id = Transactions.get_id(0)
        f_id = input("ID do Agricultor: ")
        m_id = input("ID do Mercado: ")
        data = input("Data da Venda (AAAA-MM-DD): ")
        valor = input("Valor da Venda: ")
        # Criar o objeto com a ordem correta que definimos na classe
        obj = Transactions(id, f_id, m_id, data, valor)

    # Se for um worker
    elif cls == Worker:
        id = Worker.get_id(0)
        info = input("Informação Extra: ")
        f_id = input("ID do Agricultor responsável: ")
        obj = Worker(id, info, f_id)

    if obj is not None:
        cls.insert(obj.id)
        print(f"{cls.__name__} {obj.id} guardado com sucesso na base de dados!")
    else:
        print(f"Erro: Ainda não definiste como ler os dados para a classe {cls.__name__}.")

def remover_registo(cls):
    id_apagar = int(input(f"Qual o ID de {cls.__name__} a remover? "))
    if id_apagar in cls.lst:
        cls.remove(id_apagar)
        print("Removido com sucesso!")
    else:
        print("ID não encontrado.")

def menu():
    while True:
        print("\n" + "="*30)
        print("  SISTEMA DE GESTÃO - FEIRAS")
        print("="*30)
        print("(v) Ver registos")
        print("(a) Adicionar novo")
        print("(r) Remover")
        print("(s) Sair")
        
        op = input("\nO que quer fazer? ").lower()
        
        if op == 's':
            print("A sair...")
            break
            
        if op in ['v', 'a', 'r']:
            print("\nClasses: (f)Farmer, (m)Market, (mt)MarketType, (w)Worker, (t)Transaction")
            cl_op = input("Sobre qual classe? ").lower()
            
            if cl_op in classes_disponiveis:
                target_cls = classes_disponiveis[cl_op]
                
                if op == 'v': mostrar_registos(target_cls)
                elif op == 'a': adicionar_registo(target_cls)
                elif op == 'r': remover_registo(target_cls)
            else:
                print("Classe inválida!")
        else:
            print("Opção inválida!")

if __name__ == "__main__":
    menu()