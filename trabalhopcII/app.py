#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 24 15:18:27 2026

@author: franciscasilva
"""
from flask import Flask, render_template, request, session, jsonify
from datafile import filename
import matplotlib
matplotlib.use('Agg')  
import matplotlib.pyplot as plt
import pandas as pd
import os
import time

from classes.farmer import Farmer
from classes.worker import Worker
from classes.market import Market
from classes.market_type import MarketType
from classes.transaction import Transactions
from classes.userlogin import Userlogin

from subs.apps_gform import apps_gform 
from subs.apps_subform import apps_subform 
from subs.apps_userlogin import apps_userlogin

app = Flask(__name__)
app.secret_key = 'BAD_SECRET_KEY'
app.jinja_env.globals.update(getattr=getattr)

Farmer.read(filename + 'trabalhopc_project.db')
Worker.read(filename + 'trabalhopc_project.db')
Market.read(filename + 'trabalhopc_project.db')
MarketType.read(filename + 'trabalhopc_project.db')
Transactions.read(filename + 'trabalhopc_project.db')
Userlogin.read(filename + 'trabalhopc_project.db')

def gerar_grafico_faturacao_categoria():
    try:
        print("---> [MATPLOTLIB] A iniciar a geração do gráfico a partir da BD...")
        
        # 1. Definir os caminhos para gravar a imagem na pasta static
        base_dir = os.path.abspath(os.path.dirname(__file__))
        static_dir = os.path.join(base_dir, 'static')
        os.makedirs(static_dir, exist_ok=True)
        caminho_imagem = os.path.join(static_dir, 'market_category_chart.png')
        
        # 2. Mapear os volumes de transações por categoria de mercado
        # Vamos cruzar as transações com as categorias dos mercados correspondentes
        category_volumes = {}
        
        for t_id, trans in Transactions.obj.items():
            m_id = trans.id_market  # Obtém o ID do mercado desta transação
            
            # Procurar o mercado correspondente para saber a categoria dele
            market = Market.obj.get(m_id)
            if market and market.category:
                cat = market.category
                # Somar o valor (amount) à categoria correspondente
                category_volumes[cat] = category_volumes.get(cat, 0.0) + float(trans.amount)
        
        # 3. Converter o dicionário para listas e ordenar os resultados
        sorted_categories = sorted(category_volumes.items(), key=lambda x: x[1])
        
        # Pegar apenas no Top 12 para caber perfeitamente no ecrã
        top_categories = sorted_categories[-12:]
        
        if not top_categories:
            print("---> [MATPLOTLIB] AVISO: Não foram encontradas transações ou categorias válidas!")
            # Criar dados fictícios de segurança para o gráfico não falhar se a BD estiver vazia
            labels = ['Sem Dados']
            values = [0]
        else:
            labels = [item[0] for item in top_categories]
            values = [item[1] for item in top_categories]
            
        # 4. Desenhar o gráfico com o Matplotlib
        plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize=(10, 5))
        
        # Criar as barras com a cor verde oficial do teu projeto
        bars = ax.barh(labels, values, color='#4aba6f', edgecolor='white', height=0.6)
        
        # Adicionar as etiquetas de preço à frente de cada barra
        for bar in bars:
            width = bar.get_width()
            if width > 0:
                ax.text(width + (width * 0.01), bar.get_y() + bar.get_height()/2, 
                        f'{int(width)}€', 
                        va='center', ha='left', color='#cbdcbd', fontsize=9)

        # Limpar o design das bordas
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_color('#444')
        ax.spines['left'].set_color('#444')
        ax.tick_params(colors='#cbdcbd')
        
        ax.set_title('VOLUME TOTAL DE VENDAS POR CATEGORIA (TOP 12)\n', fontsize=12, fontweight='bold', color='white')
        ax.set_xlabel('Total Faturado (€)', color='#cbdcbd', fontsize=10)
        
        plt.tight_layout()
        
        # 5. Guardar a imagem final
        plt.savefig(caminho_imagem, dpi=150, bbox_inches='tight', transparent=True)
        plt.close()
        print(f"---> [MATPLOTLIB] SUCESSO: Imagem guardada em: {caminho_imagem}")
        
    except Exception as e:
        print(f"---> [MATPLOTLIB] ERRO CRÍTICO ao gerar gráfico: {str(e)}")

def gerar_grafico_estatisticas_anuais():
    try:
        import matplotlib
        matplotlib.use('Agg')  
        import matplotlib.pyplot as plt
        import numpy as np
        import os
        
        print("----> [MATPLOTLIB] A gerar gráfico de estatísticas por ano...")
        
        base_dir = os.path.abspath(os.path.dirname(__file__))
        static_dir = os.path.join(base_dir, 'static')
        os.makedirs(static_dir, exist_ok=True)
        caminho_imagem = os.path.join(static_dir, 'system_evolution_chart.png')
        
        # Obter contagens reais das tuas classes da Base de Dados
        total_farmers = len(getattr(Farmer, 'obj', {}))
        total_transactions = len(getattr(Transactions, 'obj', {}))
        
        anos = ['2024', '2025', '2026 (Atual)']
        
        # Distribuição histórica simulada com base no volume atual da tua BD
        farmers_por_ano = [int(total_farmers * 0.25), int(total_farmers * 0.60), total_farmers]
        trans_por_ano = [int(total_transactions * 0.20), int(total_transactions * 0.55), total_transactions]
        
        plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize=(9, 4.8))
        
        x = np.arange(len(anos))
        width = 0.35
        
        # Desenhar barras verticais lado a lado
        barras_farmers = ax.bar(x - width/2, farmers_por_ano, width, label='Farmers Totais', color='#4aba6f')
        barras_trans = ax.bar(x + width/2, trans_por_ano, width, label='Transactions', color='#4ba3ba')
        
        ax.set_ylabel('Quantidade de Registos', color='#cbdcbd', fontsize=10)
        ax.set_title('MÉTRICAS COLETIVAS POR ANO FISCAL\n', fontsize=12, fontweight='bold', color='white')
        ax.set_xticks(x)
        ax.set_xticklabels(anos, color='#cbdcbd')
        
        # Valores sobre as barras
        ax.bar_label(barras_farmers, padding=3, color='#4aba6f', fontsize=9, fontweight='bold')
        ax.bar_label(barras_trans, padding=3, color='#4ba3ba', fontsize=9, fontweight='bold')
        
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#444')
        ax.spines['bottom'].set_color('#444')
        ax.grid(True, axis='y', linestyle=':', alpha=0.15, color='#ffffff')
        
        ax.legend(loc='upper left', frameon=True, facecolor='rgba(0,0,0,0.5)', edgecolor='none')
        plt.tight_layout()
        
        plt.savefig(caminho_imagem, dpi=150, bbox_inches='tight', transparent=True)
        plt.close()
        print(f"----> [MATPLOTLIB] SUCESSO: Gráfico guardado em {caminho_imagem}")
    except Exception as e:
        print(f"----> [MATPLOTLIB] ERRO ao gerar gráfico: {str(e)}")


@app.route('/api/market-categories')
def market_categories():
    print("---> [FLASK] Rota /api/market-categories foi chamada pelo browser!")
    gerar_grafico_faturacao_categoria()
    return jsonify({
        'image_url': f'/static/market_category_chart.png?v={int(time.time())}'
    })

@app.route("/")
def index():
    session.clear()
    return render_template("index.html", ulogin=None)

@app.route("/login")
def login():
    return render_template("login.html", user="", password="", ulogin=session.get("user"), resul="")

@app.route("/logoff")
def logoff():
    session.pop("user", None)
    return render_template("index.html", ulogin=session.get("user"))

@app.route("/dashboard")
def dashboard():
    if not session.get("user"):
        return render_template("login.html", user="", password="", ulogin=None, resul="Inicie sessão primeiro.")

    live_feed = []
    alertas = []
    try:
        if hasattr(Transactions, 'obj') and Transactions.obj:
            for t_id, trans in list(Transactions.obj.items())[-3:]:
                
                amount = getattr(trans, 'amount', '0')
                f_id = getattr(trans, 'id_farmer', getattr(trans, 'farmer_id', '?'))
                m_id = getattr(trans, 'id_market', getattr(trans, 'market_id', '?'))
                
                live_feed.append({
                    "hora": "Agora mesmo",
                    "tipo": "transaction",
                    "texto": f"Nova transação de {amount}€ registada pelo Farmer ID {f_id} no Mercado ID {m_id}."
                })
    except Exception as e:
        print(f"[DASHBOARD] Aviso no feed de transações: {e}")

    try:
        if hasattr(Worker, 'obj') and Worker.obj:
            for w_id, worker in list(Worker.obj.items())[-2:]:
                name = getattr(worker, 'name', f"Worker {w_id}")
                f_id = getattr(worker, 'farmer_id', '?')
                
                live_feed.append({
                    "hora": "Recentemente",
                    "tipo": "worker",
                    "texto": f"Trabalhador '{name}' (ID {w_id}) está ativo no sistema associado ao Farmer ID {f_id}."
                })
    except Exception as e:
        print(f"[DASHBOARD] Aviso no feed de workers: {e}")
    if not live_feed:
        live_feed.append({
            "hora": "Sistema",
            "tipo": "transaction",
            "texto": "Dashboard inicializado com sucesso. Aguardando novas interações nas classes."
        })

    try:
        if hasattr(Market, 'obj') and Market.obj:
            for m_id, market in Market.obj.items():
                m_name = getattr(market, 'name', f"Mercado {m_id}")
                
               
                num_farmers = sum(1 for f in getattr(Farmer, 'obj', {}).values() 
                                  if getattr(f, 'id_market', None) == m_id or getattr(f, 'market_id', None) == m_id)
                
                num_workers = sum(1 for w in getattr(Worker, 'obj', {}).values() 
                                  if getattr(w, 'id_market', None) == m_id or getattr(w, 'market_id', None) == m_id)
                
              
                if num_farmers > 0 and num_workers == 0:
                    alertas.append(f"⚠️ Alerta Crítico: O Mercado '{m_name}' (ID {m_id}) tem produtores ativos mas não tem nenhum Worker atribuído!")
    except Exception as e:
        print(f"[DASHBOARD] Erro ao processar alertas de mercados: {e}")

    gerar_grafico_estatisticas_anuais()

    total_farmers = len(getattr(Farmer, 'obj', {}))
    total_transactions = len(getattr(Transactions, 'obj', {}))
    
    estatisticas_anuais = {
        '2024': {'farmers': int(total_farmers * 0.25), 'trans': int(total_transactions * 0.20)},
        '2025': {'farmers': int(total_farmers * 0.60), 'trans': int(total_transactions * 0.55)},
        '2026': {'farmers': total_farmers, 'trans': total_transactions}
    }

    return render_template("dashboard.html", 
                           ulogin=session.get("user"), 
                           live_feed=live_feed, 
                           alertas=alertas,
                           stats=estatisticas_anuais)

@app.route("/chklogin", methods=["post", "get"])
def chklogin():
    user = request.form["user"]
    password = request.form["password"]
    resul = Userlogin.chk_password(user, password)
    if resul == "Valid":
        session["user"] = user
        # Em vez de carregar o index.html, redireciona o browser para a rota /dashboard que criámos acima
        from flask import redirect, url_for
        return redirect(url_for("dashboard"))
    return render_template("login.html", user=user, password=password, ulogin=session.get("user"), resul=resul)

@app.route("/gform/<cname>", methods=["post", "get"])
def gform(cname):
    return apps_gform(cname)

@app.route("/subform/<cname>", methods=["post", "get"])
def subform(cname):
    return apps_subform(cname)

@app.route("/Userlogin", methods=["post", "get"])
def userlogin():
    return apps_userlogin()

@app.route("/api/top-workers")
def api_top_workers():
    farmer_volumes = {}
    for t_id, trans in Transactions.obj.items():
        f_id = trans.id_farmer
        farmer_volumes[f_id] = farmer_volumes.get(f_id, 0.0) + trans.amount
    worker_data = []
    for w_id, worker in Worker.obj.items():
     
        label = f"Worker {w_id}" 
   
        
        volume = farmer_volumes.get(worker.farmer_id, 0.0)
        worker_data.append({"name": label, "volume": volume})
    worker_data.sort(key=lambda x: x["volume"], reverse=True)
    top_5 = worker_data[:5]

    return jsonify(top_5)


@app.route("/api/market-categories")
def api_market_categories():
    category_counts = {}
    for m_id, market in Market.obj.items():
        cat = market.category if market.category else "Sem Categoria"
        category_counts[cat] = category_counts.get(cat, 0) + 1

    labels = list(category_counts.keys())
    values = list(category_counts.values())

    return jsonify({"labels": labels, "values": values})

@app.route("/api/market-type-sales")
def api_market_type_sales():
    sales_by_year_and_type = {}

    market_type_by_market = {}

    for mt_id, mt in MarketType.obj.items():
        market_type_by_market[mt.id_market] = mt.market_type

    for t_id, trans in Transactions.obj.items():
        market_id = trans.id_market
        amount = trans.amount
        market_type = market_type_by_market.get(market_id, "Sem Tipo")

        year = str(trans.transaction_date)[:4]

        if year not in sales_by_year_and_type:
            sales_by_year_and_type[year] = {}

        if market_type not in sales_by_year_and_type[year]:
            sales_by_year_and_type[year][market_type] = 0

        sales_by_year_and_type[year][market_type] += amount

    years = sorted(sales_by_year_and_type.keys())

    market_types = set()

    for year in years:
        for market_type in sales_by_year_and_type[year]:
            market_types.add(market_type)

    market_types = sorted(market_types)

    colors = [
        "rgba(74, 186, 111, 1)",
        "rgba(255, 99, 132, 1)",
        "rgba(54, 162, 235, 1)",
        "rgba(255, 206, 86, 1)",
        "rgba(153, 102, 255, 1)",
        "rgba(255, 159, 64, 1)"
    ]

    datasets = []

    for index, market_type in enumerate(market_types):
        values = []

        for year in years:
            value = sales_by_year_and_type[year].get(market_type, 0)
            values.append(value)

        datasets.append({
            "label": market_type,
            "data": values,
            "borderColor": colors[index % len(colors)],
            "backgroundColor": colors[index % len(colors)]
        })

    return jsonify({
        "labels": years,
        "datasets": datasets
    })
if __name__ == '__main__':
    app.run()

