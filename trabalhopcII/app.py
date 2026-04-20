# -*- coding: utf-8 -*-
"""
Created on Mon Apr 20 01:47:26 2026

@author: crism
"""

from flask import Flask, render_template, request, session
from classes.farmer import Farmer
from classes.market import Market
from classes.market_type import MarketType
from classes.worker import Worker
from classes.transaction import Transactions
from datafile import filename

app = Flask(__name__)
app.secret_key = 'BAD_SECRET_KEY' #

# No teu app.py, define o caminho correto
db_path = filename + 'trabalhopc_project.db'

# Indica o nome da tabela (segundo argumento) para as que estão no plural
Farmer.read(db_path)   
Market.read(db_path)   
Worker.read(db_path)      
Transactions.read(db_path) 
MarketType.read(db_path)

prev_option = ""

@app.route("/", methods=["post","get"])
def index():
    global prev_option
    butshow, butedit = "enabled", "disabled"
    option = request.args.get("option")
    
    # Lógica de Navegação e Edição para Farmer
    if option == "edit":
        butshow, butedit = "disabled", "enabled"
    elif option == "delete":
        obj = Farmer.current()
        Farmer.remove(obj.id)
        if not Farmer.previous():
            Farmer.first()
    elif option == "insert":
        butshow, butedit = "disabled", "enabled"
    elif option == 'cancel':
        pass
    
    # Gravar Novo Agricultor
    elif prev_option == 'insert' and option == 'save':
        # Nota: Farmer tem id;name;creation_date
        strobj = str(Farmer.get_id(0))
        strobj = strobj + ';' + request.form["name"] + ';' + request.form["creation_date"]
        obj = Farmer.from_string(strobj)
        Farmer.insert(obj.id)
        Farmer.last()
        
    # Editar Agricultor Existente
    elif prev_option == 'edit' and option == 'save':
        obj = Farmer.current()
        obj.name = request.form["name"]
        obj.creation_date = request.form["creation_date"]
        Farmer.update(obj.id)
        
    # Navegação
    elif option == "first":
        Farmer.first()
    elif option == "previous":
        Farmer.previous()
    elif option == "next":
        Farmer.nextrec()
    elif option == "last":
        Farmer.last()
        
    elif option == 'exit':
        return "<h1>Obrigado por usar a App das Feiras</h1>"

    prev_option = option
    obj = Farmer.current()
    
    # Preparar dados para o template index.html
    if option == 'insert' or len(Farmer.lst) == 0:
        id = Farmer.get_id(0)
        name = creation_date = ""
    else:
        id = obj.id
        name = obj.name
        creation_date = obj.creation_date

    return render_template("index.html", 
                           butshow=butshow, 
                           butedit=butedit, 
                           id=id, 
                           name=name, 
                           creation_date=creation_date, # Substitui 'dob'
                           ulogin=session.get("user"))

if __name__ == '__main__':
    app.run(debug=True)