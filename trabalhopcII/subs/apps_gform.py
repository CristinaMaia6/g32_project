from flask import Flask, render_template, request, session

from classes.farmer import Farmer 
from classes.market_type import MarketType
from classes.market import Market
from classes.transaction import Transactions
from classes.worker import Worker
from classes.userlogin import Userlogin

prev_option = ""

def apps_gform(cname=''):
    global prev_option
    ulogin = session.get("user")
    
    if ulogin is not None:
        # Bloqueio de segurança: Se for a classe Userlogin, proíbe o gform genérico
        if cname == 'Userlogin':
            return render_template("index.html", ulogin=session.get("user"))
            
        cl = eval(cname)
        butshow = "enabled"
        butedit = "disabled"
        
        # Procura o utilizador logado para validar o grupo dele
        user_id = Userlogin.get_user_id(ulogin)
        is_admin = True 
        
        if user_id != 0:
            user_obj = Userlogin.obj[user_id]
            is_admin = (user_obj.usergroup in ['root', 'admin'])
        
        option = request.args.get("option")
        
        if not is_admin and option in ['insert', 'edit', 'delete', 'save']:
            option = "cancel"

        if prev_option == 'insert' and option == 'save':
            strobj = request.form[cl.att[0]]
            for i in range(1, len(cl.att)):
                strobj += ";" + request.form[cl.att[i]]
            obj = cl.from_string(strobj)
            cl.insert(getattr(obj, cl.att[0]))
            cl.last()
            
        elif prev_option == 'edit' and option == 'save':
            obj = cl.current()
            for i in range(1, len(cl.att)):
                setattr(obj, cl.att[i], request.form[cl.att[i]])
            cl.update(getattr(obj, cl.att[0]))
            
        else:
            if option == "edit":
                butshow = "disabled"
                butedit = "enabled"
            elif option == "delete":
                obj = cl.current()
                id_attr = cl.att[0]
                cl.remove(getattr(obj, id_attr))
                if not cl.previous():
                    cl.first()
            elif option == "insert":
                butshow = "disabled"
                butedit = "enabled"
            elif option == 'cancel':
                pass
            elif option == "first":
                cl.first()
            elif option == "previous":
                cl.previous()
            elif option == "next":
                cl.nextrec() 
            elif option == "last":
                cl.last()
            elif option == 'exit':
                return render_template("index.html", ulogin=session.get("user"))
                
        prev_option = option
        obj = cl.current()
        
        if option == 'insert' or len(cl.lst) == 0:
            obj = dict()
            obj[cl.att[0]] = 0
            for i in range(1, len(cl.att)):
                obj[cl.att[i]] = ""
        
        return render_template(
            "gform.html", 
            butshow=butshow, 
            butedit=butedit, 
            cname=cname, 
            obj=obj, 
            att=cl.att, 
            des=cl.des, 
            ulogin=session.get("user"),
            is_admin=is_admin
        )
    else:
        return render_template("index.html", ulogin=ulogin)