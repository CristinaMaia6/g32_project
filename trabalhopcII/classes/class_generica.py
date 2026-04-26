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
    
    # 1. Criar a legenda das colunas atraves da lista 'des' da classe
    # "Estrutura: Id | Name | Creation Date"
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
        # Vamos buscar os valores atraves da lista 'att' (_id, _name, etc)
        valores = [str(getattr(obj, attr)) for attr in cls.att]
        print(" | ".join(valores))


def adicionar_registo(cls):
    print(f"\n--- Adicionar {cls.header} ---")
    obj = None 
    id_a_gravar = None  # <--- Nova variável para evitar o erro de atributo

    # Se for um farmer
    if cls == Farmer:
        id_a_gravar = Farmer.get_id(0)
        nome = input("Nome: ")
        data = input("Data de Criação (AAAA-MM-DD): ")
        obj = Farmer(id_a_gravar, nome, data)

    # Se for um market
    elif cls == Market:
        id_a_gravar = Market.get_id(0)
        titulo = input("Título do Mercado: ")
        categoria = input("Categoria: ")
        obj = Market(id_a_gravar, titulo, categoria)

    # Se for uma transaction
    elif cls == Transactions:
        id_a_gravar = Transactions.get_id(0)
        f_id = input("ID do Agricultor: ")
        m_id = input("ID do Mercado: ")
        data = input("Data da Venda (AAAA-MM-DD): ")
        valor = input("Valor da Venda: ")
        obj = Transactions(id_a_gravar, f_id, m_id, data, valor)

    # Se for um worker
    elif cls == Worker:
        id_a_gravar = Worker.get_id(0)
        info = input("Informação Extra: ")
        f_id = input("ID do Agricultor responsável: ")
        obj = Worker(id_a_gravar, info, f_id)

    # Se for um tipo de mercado
    elif cls == MarketType:
        tipo = input("Que tipo de mercado? (Flores/Fruta/Roupa): ")
        # Aqui o ID é o que o utilizador digita
        id_a_gravar = int(input("A que ID de Market quer atribuir este tipo? "))
        obj = MarketType(id_a_gravar, "Mercado de " + tipo)

    # --- PARTE FINAL CORRIGIDA ---
    if obj is not None:
        # 1. Só adicionamos à lista 'lst' se o ID ainda não existir lá
        if id_a_gravar not in cls.lst:
            cls.lst.append(id_a_gravar)
        
        # 2. Atualizamos o dicionário de objetos (isto substitui o antigo pelo novo)
        cls.obj[id_a_gravar] = obj
        
        # 3. Gravamos na base de dados
        cls.insert(id_a_gravar)
        print(f"\n[Sucesso] {cls.__name__} {id_a_gravar} atualizado/guardado!")
    else:
        print(f"Erro: Classe {cls.__name__} não reconhecida.")    


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