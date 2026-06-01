from flask import Flask, render_template, request, session
from classes.userlogin import Userlogin

prev_option = ""

def apps_userlogin():
    global prev_option
    ulogin = session.get("user")
    user_id = Userlogin.get_user_id(ulogin)
    
    if ulogin is not None:
        # Busca o grupo do utilizador atual. Garante que o ID existe.
        group = Userlogin.obj[user_id].usergroup if user_id != 0 else "guest"
        
        # Se NÃO for administrador ou root, ele fica preso apenas no seu próprio registo
        if group not in ["admin", "root"]:
            Userlogin.current(user_id)
            
        butshow = "enabled"
        butedit = "disabled"
        option = request.args.get("option")
        
        # Segurança: impede utilizadores normais de forçarem edição/remoção/inserção
        if group not in ["admin", "root"] and option in ["edit", "delete", "insert"]:
            option = "cancel"

        if option == "edit":
            butshow = "disabled"
            butedit = "enabled"
            
        elif option == "delete":
            obj = Userlogin.current()
            Userlogin.remove(obj.id)
            if not Userlogin.previous():
                Userlogin.first()
                
        elif option == "insert":
            butshow = "disabled"
            butedit = "enabled"
            
        elif option == 'cancel':
            pass
            
        elif prev_option == 'insert' and option == 'save':
            # Cria o utilizador e passa pelo set_password() para encriptar texto limpo automaticamente
            obj = Userlogin(0, request.form["user"], request.form["usergroup"], 
                            Userlogin.set_password(request.form["password"]))
            Userlogin.insert(obj.id)
            Userlogin.last()
            
        elif prev_option == 'edit' and option == 'save':
            obj = Userlogin.current()
            if group in ["admin", "root"]:
                obj.usergroup = request.form["usergroup"]
            
            # Se o utilizador escreveu uma nova password na caixa, encripta-a
            if request.form["password"] != "":
                obj.password = Userlogin.set_password(request.form["password"])
            Userlogin.update(obj.id)
            
        elif option == "first":
            Userlogin.first()
        elif option == "previous":
            Userlogin.previous()
        elif option == "next":
            Userlogin.nextrec()
        elif option == "last":
            Userlogin.last()
        elif option == 'exit':
            return render_template("index.html", ulogin=session.get("user"))
            
        prev_option = option
        obj = Userlogin.current()
        
        if option == 'insert' or len(Userlogin.lst) == 0:
            user = ""
            usergroup = ""
            password = ""
        else:
            user = obj.user
            usergroup = obj.usergroup
            password = ""
            
        return render_template("userlogin.html", butshow=butshow, butedit=butedit, 
                               user=user, usergroup=usergroup, password=password, 
                               ulogin=session.get("user"), group=group)
    else:
        return render_template("index.html", ulogin=ulogin)