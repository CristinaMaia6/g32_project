#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 24 15:18:27 2026

@author: franciscasilva
"""
from flask import Flask, render_template, request, session, jsonify
from datafile import filename

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

@app.route("/chklogin", methods=["post", "get"])
def chklogin():
    user = request.form["user"]
    password = request.form["password"]
    resul = Userlogin.chk_password(user, password)
    if resul == "Valid":
        session["user"] = user
        return render_template("index.html", ulogin=session.get("user"))
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

