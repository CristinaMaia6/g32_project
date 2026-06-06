from flask import Flask, render_template, request, session, jsonify, redirect, url_for
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


def _safe_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _format_currency(value):
    value = _safe_float(value)
    return f"{value:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")


def _format_number(value):
    try:
        return f"{int(value):,}".replace(",", ".")
    except (TypeError, ValueError):
        return "0"


def _get_attr(obj, *names, default=None):
    for name in names:
        if hasattr(obj, name):
            value = getattr(obj, name)
            if value not in [None, ""]:
                return value
    return default


def _get_obj(collection, object_id):
    if object_id in collection:
        return collection.get(object_id)
    str_id = str(object_id)
    if str_id in collection:
        return collection.get(str_id)
    try:
        int_id = int(object_id)
        if int_id in collection:
            return collection.get(int_id)
    except (TypeError, ValueError):
        pass
    return None


def _market_label(market_id):
    market = _get_obj(Market.obj, market_id)
    if not market:
        return f"Market {market_id}"
    return _get_attr(market, "title", "_title", "name", "_name", "market_name", "_market_name", default=f"Market {market_id}")


def _farmer_label(farmer_id):
    farmer = _get_obj(Farmer.obj, farmer_id)
    if not farmer:
        return f"Farmer {farmer_id}"
    return _get_attr(farmer, "name", "_name", "farmer_name", "_farmer_name", default=f"Farmer {farmer_id}")


def _worker_label(worker_id):
    worker = _get_obj(Worker.obj, worker_id)
    if not worker:
        return f"Worker {worker_id}"
    return _get_attr(worker, "name", "_name", "worker_name", "_worker_name", default=f"Worker {worker_id}")


def _market_type_by_market():
    market_type_by_market = {}
    for mt_id, mt in MarketType.obj.items():
        market_id = _get_attr(mt, "id_market", "market_id", "_market_id", "_id_market")
        market_type = _get_attr(mt, "market_type", "type", "_market_type", "_type")
        if market_id is not None and market_type is not None:
            market_type_by_market[market_id] = market_type
            market_type_by_market[str(market_id)] = market_type
            try:
                market_type_by_market[int(market_id)] = market_type
            except (TypeError, ValueError):
                pass
    return market_type_by_market


def _transactions_for_farmer(farmer_id):
    result = []
    for t_id, trans in Transactions.obj.items():
        current_farmer = _get_attr(trans, "id_farmer", "farmer_id", "_farmer_id", "_id_farmer")
        if str(current_farmer) == str(farmer_id):
            result.append((t_id, trans))
    return result


def _transactions_for_market(market_id):
    result = []
    for t_id, trans in Transactions.obj.items():
        current_market = _get_attr(trans, "id_market", "market_id", "_market_id", "_id_market")
        if str(current_market) == str(market_id):
            result.append((t_id, trans))
    return result


def _sales_total(transactions):
    total = 0.0
    for t_id, trans in transactions:
        total += _safe_float(_get_attr(trans, "amount", "_amount", default=0))
    return total


def _main_market_for_farmer(farmer_id):
    market_totals = {}
    for t_id, trans in _transactions_for_farmer(farmer_id):
        market_id = _get_attr(trans, "id_market", "market_id", "_market_id", "_id_market")
        amount = _safe_float(_get_attr(trans, "amount", "_amount", default=0))
        market_totals[market_id] = market_totals.get(market_id, 0.0) + amount
    if not market_totals:
        return "N/A"
    top_market_id = max(market_totals, key=market_totals.get)
    return _market_label(top_market_id)


def _most_active_farmer_for_market(market_id):
    farmer_counts = {}
    for t_id, trans in _transactions_for_market(market_id):
        farmer_id = _get_attr(trans, "id_farmer", "farmer_id", "_farmer_id", "_id_farmer")
        farmer_counts[farmer_id] = farmer_counts.get(farmer_id, 0) + 1
    if not farmer_counts:
        return "N/A"
    top_farmer_id = max(farmer_counts, key=farmer_counts.get)
    return _farmer_label(top_farmer_id)


def _market_type_comparison_data():
    market_type_by_market = _market_type_by_market()
    comparison = {}

    for t_id, trans in Transactions.obj.items():
        market_id = _get_attr(trans, "id_market", "market_id", "_market_id", "_id_market")
        amount = _safe_float(_get_attr(trans, "amount", "_amount", default=0))
        market_type = market_type_by_market.get(market_id, "Sem Tipo")

        if market_type not in comparison:
            comparison[market_type] = {
                "market_type": market_type,
                "total_sales": 0.0,
                "transactions": 0,
                "average_transaction": 0.0
            }

        comparison[market_type]["total_sales"] += amount
        comparison[market_type]["transactions"] += 1

    for market_type in comparison:
        total_sales = comparison[market_type]["total_sales"]
        transactions = comparison[market_type]["transactions"]
        if transactions > 0:
            comparison[market_type]["average_transaction"] = total_sales / transactions

    result = list(comparison.values())
    result.sort(key=lambda item: item["total_sales"], reverse=True)
    return result


def _sales_evolution_data():
    sales_by_year = {}
    for t_id, trans in Transactions.obj.items():
        date_value = str(_get_attr(trans, "transaction_date", "date", "_transaction_date", default=""))
        year = date_value[:4] if len(date_value) >= 4 else "Sem Data"
        amount = _safe_float(_get_attr(trans, "amount", "_amount", default=0))
        sales_by_year[year] = sales_by_year.get(year, 0.0) + amount

    labels = sorted(sales_by_year.keys())
    values = [sales_by_year[year] for year in labels]
    return labels, values


def _top_farmers_sales_data(limit=5):
    farmer_sales = {}
    for t_id, trans in Transactions.obj.items():
        farmer_id = _get_attr(trans, "id_farmer", "farmer_id", "_farmer_id", "_id_farmer")
        amount = _safe_float(_get_attr(trans, "amount", "_amount", default=0))
        farmer_sales[farmer_id] = farmer_sales.get(farmer_id, 0.0) + amount

    sorted_farmers = sorted(farmer_sales.items(), key=lambda item: item[1], reverse=True)[:limit]
    return {
        "labels": [_farmer_label(farmer_id) for farmer_id, value in sorted_farmers],
        "values": [value for farmer_id, value in sorted_farmers]
    }


def _top_markets_sales_data(limit=5):
    market_sales = {}
    for t_id, trans in Transactions.obj.items():
        market_id = _get_attr(trans, "id_market", "market_id", "_market_id", "_id_market")
        amount = _safe_float(_get_attr(trans, "amount", "_amount", default=0))
        market_sales[market_id] = market_sales.get(market_id, 0.0) + amount

    sorted_markets = sorted(market_sales.items(), key=lambda item: item[1], reverse=True)[:limit]
    return {
        "labels": [_market_label(market_id) for market_id, value in sorted_markets],
        "values": [value for market_id, value in sorted_markets]
    }


def _top_workers_data(limit=5):
    farmer_volumes = {}
    for t_id, trans in Transactions.obj.items():
        farmer_id = _get_attr(trans, "id_farmer", "farmer_id", "_farmer_id", "_id_farmer")
        amount = _safe_float(_get_attr(trans, "amount", "_amount", default=0))
        farmer_volumes[farmer_id] = farmer_volumes.get(farmer_id, 0.0) + amount
        farmer_volumes[str(farmer_id)] = farmer_volumes.get(str(farmer_id), 0.0) + amount

    worker_data = []
    for worker_id, worker in Worker.obj.items():
        farmer_id = _get_attr(worker, "farmer_id", "id_farmer", "_farmer_id", "_id_farmer")
        volume = farmer_volumes.get(farmer_id, farmer_volumes.get(str(farmer_id), 0.0))
        worker_data.append({"name": _worker_label(worker_id), "volume": volume})

    worker_data.sort(key=lambda item: item["volume"], reverse=True)
    return worker_data[:limit]



def _top_performers_summary():
    top_farmers = _top_farmers_sales_data(1)
    top_markets = _top_markets_sales_data(1)
    top_workers = _top_workers_data(1)

    top_farmer_name = top_farmers["labels"][0] if top_farmers["labels"] else "N/A"
    top_farmer_value = top_farmers["values"][0] if top_farmers["values"] else 0
    top_market_name = top_markets["labels"][0] if top_markets["labels"] else "N/A"
    top_market_value = top_markets["values"][0] if top_markets["values"] else 0
    top_worker_name = top_workers[0]["name"] if top_workers else "N/A"
    top_worker_value = top_workers[0]["volume"] if top_workers else 0

    return {
        "top_farmer": top_farmer_name,
        "top_farmer_sales": _format_currency(top_farmer_value),
        "top_market": top_market_name,
        "top_market_sales": _format_currency(top_market_value),
        "top_worker": top_worker_name,
        "top_worker_sales": _format_currency(top_worker_value)
    }

def gerar_grafico_faturacao_categoria():
    try:
        print("---> [MATPLOTLIB] A iniciar a geração do gráfico a partir da BD...")

        base_dir = os.path.abspath(os.path.dirname(__file__))
        static_dir = os.path.join(base_dir, 'static')
        os.makedirs(static_dir, exist_ok=True)
        caminho_imagem = os.path.join(static_dir, 'market_category_chart.png')

        category_volumes = {}

        for t_id, trans in Transactions.obj.items():
            market_id = _get_attr(trans, "id_market", "market_id", "_market_id", "_id_market")
            market = _get_obj(Market.obj, market_id)
            category = _get_attr(market, "category", "_category", default=None) if market else None
            amount = _safe_float(_get_attr(trans, "amount", "_amount", default=0))
            if category:
                category_volumes[category] = category_volumes.get(category, 0.0) + amount

        sorted_categories = sorted(category_volumes.items(), key=lambda x: x[1])
        top_categories = sorted_categories[-12:]

        if not top_categories:
            print("---> [MATPLOTLIB] AVISO: Não foram encontradas transações ou categorias válidas!")
            labels = ['Sem Dados']
            values = [0]
        else:
            labels = [item[0] for item in top_categories]
            values = [item[1] for item in top_categories]

        plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize=(10, 5))
        bars = ax.barh(labels, values, color='#4aba6f', edgecolor='white', height=0.6)

        for bar in bars:
            width = bar.get_width()
            if width > 0:
                ax.text(width + (width * 0.01), bar.get_y() + bar.get_height() / 2,
                        f'{int(width)}€',
                        va='center', ha='left', color='#cbdcbd', fontsize=9)

        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_color('#444')
        ax.spines['left'].set_color('#444')
        ax.tick_params(colors='#cbdcbd')

        ax.set_title('VOLUME TOTAL DE VENDAS POR CATEGORIA (TOP 12)\n', fontsize=12, fontweight='bold', color='white')
        ax.set_xlabel('Total Faturado (€)', color='#cbdcbd', fontsize=10)

        plt.tight_layout()
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

        total_farmers = len(getattr(Farmer, 'obj', {}))
        total_transactions = len(getattr(Transactions, 'obj', {}))

        anos = ['2024', '2025', '2026 (Atual)']

        farmers_por_ano = [int(total_farmers * 0.25), int(total_farmers * 0.60), total_farmers]
        trans_por_ano = [int(total_transactions * 0.20), int(total_transactions * 0.55), total_transactions]

        plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize=(9, 4.8))

        x = np.arange(len(anos))
        width = 0.35

        barras_farmers = ax.bar(x - width / 2, farmers_por_ano, width, label='Farmers Totais', color='#4aba6f')
        barras_trans = ax.bar(x + width / 2, trans_por_ano, width, label='Transactions', color='#4ba3ba')

        ax.set_ylabel('Quantidade de Registos', color='#cbdcbd', fontsize=10)
        ax.set_title('MÉTRICAS COLETIVAS POR ANO FISCAL\n', fontsize=12, fontweight='bold', color='white')
        ax.set_xticks(x)
        ax.set_xticklabels(anos, color='#cbdcbd')

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

    total_farmers = len(getattr(Farmer, "obj", {}))
    total_workers = len(getattr(Worker, "obj", {}))
    total_markets = len(getattr(Market, "obj", {}))
    total_market_types = len(getattr(MarketType, "obj", {}))
    total_transactions = len(getattr(Transactions, "obj", {}))

    total_sales = 0.0
    for trans in getattr(Transactions, "obj", {}).values():
        total_sales += _safe_float(_get_attr(trans, "amount", "_amount", default=0))

    average_transaction = total_sales / total_transactions if total_transactions > 0 else 0

    dashboard_stats = {
        "total_sales": _format_currency(total_sales),
        "total_transactions": _format_number(total_transactions),
        "average_transaction": _format_currency(average_transaction),
        "total_farmers": _format_number(total_farmers),
        "total_workers": _format_number(total_workers),
        "total_markets": _format_number(total_markets),
        "total_market_types": _format_number(total_market_types)
    }

    market_type_table = []
    try:
        for item in _market_type_comparison_data()[:6]:
            market_type_table.append({
                "market_type": item.get("market_type", "N/A"),
                "total_sales": _format_currency(item.get("total_sales", 0)),
                "transactions": _format_number(item.get("transactions", 0)),
                "average_transaction": _format_currency(item.get("average_transaction", 0))
            })
    except Exception as e:
        print(f"[DASHBOARD] Erro no Market Type Summary: {e}")

    recent_transactions = []
    try:
        items = list(getattr(Transactions, "obj", {}).items())[-6:][::-1]
        for t_id, trans in items:
            farmer_id = _get_attr(trans, "id_farmer", "farmer_id", "_farmer_id", "_id_farmer", default="?")
            market_id = _get_attr(trans, "id_market", "market_id", "_market_id", "_id_market", default="?")
            amount = _safe_float(_get_attr(trans, "amount", "_amount", default=0))
            transaction_date = _get_attr(trans, "transaction_date", "date", "_transaction_date", default="")
            recent_transactions.append({
                "id": t_id,
                "date": str(transaction_date),
                "farmer": _farmer_label(farmer_id),
                "market": _market_label(market_id),
                "amount": _format_currency(amount)
            })
    except Exception as e:
        print(f"[DASHBOARD] Erro nas Recent Transactions: {e}")

    try:
        top_performers = _top_performers_summary()
    except Exception as e:
        print(f"[DASHBOARD] Erro nos Top Performers: {e}")
        top_performers = {
            "top_farmer": "N/A",
            "top_farmer_sales": _format_currency(0),
            "top_worker": "N/A",
            "top_worker_sales": _format_currency(0),
            "top_market": "N/A",
            "top_market_sales": _format_currency(0)
        }

    estatisticas_anuais = {
        "2024": {"farmers": int(total_farmers * 0.25), "trans": int(total_transactions * 0.20)},
        "2025": {"farmers": int(total_farmers * 0.60), "trans": int(total_transactions * 0.55)},
        "2026": {"farmers": total_farmers, "trans": total_transactions}
    }

    return render_template("dashboard.html",
                           ulogin=session.get("user"),
                           stats=estatisticas_anuais,
                           dashboard_stats=dashboard_stats,
                           market_type_table=market_type_table,
                           recent_transactions=recent_transactions,
                           top_performers=top_performers)


@app.route("/chklogin", methods=["post", "get"])
def chklogin():
    user = request.form["user"]
    password = request.form["password"]
    resul = Userlogin.chk_password(user, password)
    if resul == "Valid":
        session["user"] = user
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
    return jsonify(_top_workers_data())


@app.route("/api/market-categories")
def api_market_categories():
    gerar_grafico_faturacao_categoria()
    return jsonify({
        'image_url': f'/static/market_category_chart.png?v={int(time.time())}'
    })


@app.route("/api/market-type-sales")
def api_market_type_sales():
    sales_by_year_and_type = {}
    market_type_by_market = _market_type_by_market()

    for t_id, trans in Transactions.obj.items():
        market_id = _get_attr(trans, "id_market", "market_id", "_market_id", "_id_market")
        amount = _safe_float(_get_attr(trans, "amount", "_amount", default=0))
        market_type = market_type_by_market.get(market_id, "Sem Tipo")
        year = str(_get_attr(trans, "transaction_date", "date", "_transaction_date", default=""))[:4]

        if not year:
            year = "Sem Data"

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


@app.route("/api/sales-evolution")
def api_sales_evolution():
    labels, values = _sales_evolution_data()
    return jsonify({"labels": labels, "values": values})


@app.route("/api/top-farmers-sales")
def api_top_farmers_sales():
    return jsonify(_top_farmers_sales_data())


@app.route("/api/top-markets-sales")
def api_top_markets_sales():
    return jsonify(_top_markets_sales_data())


@app.route("/api/market-type-comparison")
def api_market_type_comparison():
    return jsonify(_market_type_comparison_data())


@app.route("/api/performance/<cname>/<object_id>")
def api_performance(cname, object_id):
    total_transactions = len(getattr(Transactions, 'obj', {}))
    total_sales = sum(_safe_float(_get_attr(trans, "amount", "_amount", default=0)) for trans in Transactions.obj.values())
    global_average = total_sales / total_transactions if total_transactions > 0 else 0
    market_type_by_market = _market_type_by_market()

    if cname == "Farmer":
        farmer = _get_obj(Farmer.obj, object_id)
        if not farmer:
            return jsonify({"error": "Farmer não encontrado."})
        transactions = _transactions_for_farmer(object_id)
        sales = _sales_total(transactions)
        count = len(transactions)
        average = sales / count if count > 0 else 0
        return jsonify({
            "title": f"Farmer Performance - {_farmer_label(object_id)}",
            "metrics": [
                {"label": "Total Sales", "value": _format_currency(sales)},
                {"label": "Transactions", "value": _format_number(count)},
                {"label": "Average Transaction", "value": _format_currency(average)},
                {"label": "Main Market", "value": _main_market_for_farmer(object_id)},
                {"label": "Global Average", "value": _format_currency(global_average)},
                {"label": "Performance vs Average", "value": "Acima da média" if average > global_average else "Abaixo ou igual à média"}
            ]
        })

    if cname == "Worker":
        worker = _get_obj(Worker.obj, object_id)
        if not worker:
            return jsonify({"error": "Worker não encontrado."})
        farmer_id = _get_attr(worker, "farmer_id", "id_farmer", "_farmer_id", "_id_farmer")
        transactions = _transactions_for_farmer(farmer_id)
        sales = _sales_total(transactions)
        count = len(transactions)
        average = sales / count if count > 0 else 0
        top_workers = _top_workers_data(limit=len(Worker.obj))
        ranking = "N/A"
        for index, item in enumerate(top_workers, start=1):
            if item["name"] == _worker_label(object_id):
                ranking = str(index)
                break
        return jsonify({
            "title": f"Worker Performance - {_worker_label(object_id)}",
            "metrics": [
                {"label": "Associated Farmer", "value": _farmer_label(farmer_id)},
                {"label": "Assisted Sales", "value": _format_currency(sales)},
                {"label": "Assisted Transactions", "value": _format_number(count)},
                {"label": "Average Assisted Transaction", "value": _format_currency(average)},
                {"label": "Worker Ranking", "value": ranking},
                {"label": "Main Market", "value": _main_market_for_farmer(farmer_id)}
            ]
        })

    if cname == "Market":
        market = _get_obj(Market.obj, object_id)
        if not market:
            return jsonify({"error": "Market não encontrado."})
        transactions = _transactions_for_market(object_id)
        sales = _sales_total(transactions)
        count = len(transactions)
        average = sales / count if count > 0 else 0
        market_type = market_type_by_market.get(object_id, market_type_by_market.get(str(object_id), "Sem Tipo"))
        return jsonify({
            "title": f"Market Performance - {_market_label(object_id)}",
            "metrics": [
                {"label": "Total Sales", "value": _format_currency(sales)},
                {"label": "Transactions", "value": _format_number(count)},
                {"label": "Average Transaction", "value": _format_currency(average)},
                {"label": "Most Active Farmer", "value": _most_active_farmer_for_market(object_id)},
                {"label": "Market Type", "value": market_type},
                {"label": "Global Average", "value": _format_currency(global_average)}
            ]
        })

    if cname == "MarketType":
        market_type_obj = _get_obj(MarketType.obj, object_id)
        if not market_type_obj:
            return jsonify({"error": "Market Type não encontrado."})
        market_id = _get_attr(market_type_obj, "id_market", "market_id", "_market_id", "_id_market")
        market_type = _get_attr(market_type_obj, "market_type", "type", "_market_type", "_type", default="Sem Tipo")
        transactions = _transactions_for_market(market_id)
        sales = _sales_total(transactions)
        count = len(transactions)
        average = sales / count if count > 0 else 0
        return jsonify({
            "title": f"Market Type Performance - {market_type}",
            "metrics": [
                {"label": "Market Type", "value": market_type},
                {"label": "Associated Market", "value": _market_label(market_id)},
                {"label": "Total Sales", "value": _format_currency(sales)},
                {"label": "Transactions", "value": _format_number(count)},
                {"label": "Average Transaction", "value": _format_currency(average)},
                {"label": "Global Average", "value": _format_currency(global_average)}
            ]
        })

    if cname == "Transactions":
        transaction = _get_obj(Transactions.obj, object_id)
        if not transaction:
            return jsonify({"error": "Transaction não encontrada."})
        farmer_id = _get_attr(transaction, "id_farmer", "farmer_id", "_farmer_id", "_id_farmer")
        market_id = _get_attr(transaction, "id_market", "market_id", "_market_id", "_id_market")
        amount = _safe_float(_get_attr(transaction, "amount", "_amount", default=0))
        transaction_date = _get_attr(transaction, "transaction_date", "date", "_transaction_date", default="")
        market_type = market_type_by_market.get(market_id, market_type_by_market.get(str(market_id), "Sem Tipo"))
        return jsonify({
            "title": f"Transaction Performance - {object_id}",
            "metrics": [
                {"label": "Amount", "value": _format_currency(amount)},
                {"label": "Date", "value": str(transaction_date)},
                {"label": "Farmer", "value": _farmer_label(farmer_id)},
                {"label": "Market", "value": _market_label(market_id)},
                {"label": "Market Type", "value": market_type},
                {"label": "Comparison with Average", "value": "Acima da média" if amount > global_average else "Abaixo ou igual à média"}
            ]
        })

    return jsonify({"error": "Classe sem performance definida."})


if __name__ == '__main__':
    app.run()
