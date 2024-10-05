from flask import Flask, url_for, render_template, flash, redirect, session, request, jsonify, Blueprint
from flask_pymongo import PyMongo, pymongo
from flask_bcrypt import Bcrypt
from formularios import Register, Login, Edit, Saldo, Mazo
from flask_login import login_user, logout_user
from datetime import date
from flask_paginate import Pagination, get_page_parameter
import requests
from random import *

app=Flask(__name__)
app.config['SECRET_KEY']='1b7ac948df1adf68ceeb48fc5deed21bb3e5fa6bb0bca2607ee0cf7e0711d997'
app.config['MONGO_URI']="mongodb://localhost:27017/final"
mongo=PyMongo(app)
bcrypt=Bcrypt(app)

db=mongo.db.Usuarios
cartas=mongo.db.cartas
sobres=mongo.db.sobres



@app.route("/")
@app.route("/home")
def index():
    if 'user' not in session:
        return render_template('home.html')
    else:
        return render_template('new_home.html')



@app.route("/user")
def usuario():
    if 'user' not in session:
        return render_template('home.html')
    else:
        filter={'nom':session['user']}
        datos=mongo.db.Usuarios.find_one(filter)
        return render_template('usuario.html',posts=datos)

@app.route("/editar", methods=['GET','POST'])
def editar():
    if 'user' not in session:
        return render_template('home.html')
    else:
        form=Edit()
        if form.validate_on_submit():
            filter={'nom':session['user']}
            datos=mongo.db.Usuarios.find_one(filter)
            if bcrypt.check_password_hash(datos['password'],form.password.data):
                datos1={"$set":{"password":bcrypt.generate_password_hash(form.new_password.data).decode('utf-8')}}
                datos2={"$set":{"nom":form.username.data}}
                cambio1=mongo.db.Usuarios.update_one(filter,datos1)
                cambio2=mongo.db.Usuarios.update_one(filter,datos2)
                session['user']=form.username.data
                return redirect(url_for('usuario'))
    return render_template('edit.html',form=form)

@app.route("/saldo", methods=['GET','POST'])
def saldo():
    if 'user' not in session:
        return render_template('home.html')
    else:
        form=Saldo()
        if form.validate_on_submit():
            filter={'nom':session['user']}
            datos=mongo.db.Usuarios.find_one(filter)
            saldo_actual=datos['saldo']
            saldo_actual+=form.saldo.data
            datos1={"$set":{"saldo":saldo_actual}}
            cambio1=mongo.db.Usuarios.update_one(filter,datos1)
            return redirect(url_for('usuario'))
    return render_template('saldo.html',form=form)

@app.route("/logout")
def logout():
    session.pop('user',None)
    return redirect(url_for('index'))



@app.route("/delete")
def delete():
    filter={'nom':session['user']}
    db.delete_one(filter)
    session.pop('user',None)
    return redirect(url_for('index'))



@app.route("/registro", methods=['GET','POST'])
def registro():
    if 'user' in session:
        flash(f"Ya estas logeado porfavor cierre sesion", "success")
        return redirect(url_for('index'))
    else:
        form=Register()
        if form.validate_on_submit():
            aux=db.find_one({"email":form.email.data})
            aux2=db.find_one({"nom":form.username.data})
            if aux==None and aux2==None:
                criptado=bcrypt.generate_password_hash(form.password.data).decode('utf-8')
                new_user={
                "nom":form.username.data,
                "email":form.email.data,
                "password":criptado,
                "saldo":0.00
                }
                db.insert_one(new_user)
                filter={'email':form.email.data}
                llave_usuario=db.find_one(filter)
                cesta_usuario={}
                coleccion_usuario={}
                mazos_usuario={}
                historial_usuario={}
                llave=str(llave_usuario["_id"])
                cesta_usuario[llave]=[]
                coleccion_usuario[llave]=[]
                mazos_usuario[llave]=[]
                historial_usuario[llave]=[]
                mongo.db.cesta.insert_one(cesta_usuario)
                mongo.db.coleccion.insert_one(coleccion_usuario)
                mongo.db.mazos.insert_one(mazos_usuario)
                mongo.db.historial.insert_one(historial_usuario)
                flash(f"Cuenta creada exitosamente para {form.username.data}!, Bienvenido.", "success")
                session['user']=form.username.data
                return redirect(url_for('index'))
            else:
                flash(f"Usuario con email {form.email.data} o nombre de usuario {form.username.data} ya existe", "danger")
                return redirect(url_for('registro'))
    return render_template('registro.html', form=form)

@app.route("/como_jugar")
def como_jugar():
    if 'user' not in session:
        return render_template('ajuda.html')
    else:
        return render_template('ajuda2.html')

@app.route("/login", methods=['GET','POST'])
def login():
    if 'user' in session:
        flash(f"Ya estas logeado porfavor cierre sesion", "success")
        return redirect(url_for('index'))
    else:
        form=Login()
        if form.validate_on_submit():
            aux=db.find_one({"email":form.email.data})
            if aux!=None:
                if aux['email']==form.email.data and bcrypt.check_password_hash(aux['password'],form.password.data):
                    flash(f"Logeado correctamente bienvenido!", "success")
                    filter={'email':form.email.data}
                    inicio=db.find_one(filter)
                    session['user']=inicio['nom']
                    return redirect(url_for('index'))
                elif aux['email']==form.email.data and not bcrypt.check_password_hash(aux['password'],form.password.data):
                    flash(f"Logeado incorrecto!, contraseña incorrecta.", "danger")
                    return redirect(url_for('login'))
            else:
                flash(f"Logeado incorrecto!, No se encontro el usuario", "danger")
                return redirect(url_for('login'))
    return render_template('login.html', form=form)

@app.route("/cartas", methods=['GET', 'POST'])
def cartas():

    search=False

    q=request.args.get('q')

    if q:
        search=True

    page = request.args.get(get_page_parameter(), type=int, default=1)

    carta=mongo.db.cartas

    print(page)

    if page>1:
        cartas=carta.find().skip((page-1)*10).limit(10)
    else:
        cartas=carta.find().limit(10)

    pagination= Pagination(page=page, total=cartas.count(), search=search, record_name='cartas')

    if 'user' not in session:
        return render_template('cartas2.html',posts=cartas,pagination=pagination)
    else:
        return render_template('cartas.html',posts=cartas,pagination=pagination)

@app.route("/carta", methods=['GET', 'POST'])
def vista_carta_generica():
    id=int(request.args.get('valor'))
    filter={'id':id}
    carta=mongo.db.cartas.find_one(filter)
    if carta["type"]=="Spell Card" or carta["type"]=="Trap Card" or carta["type"]=="Link Monster":
        if 'user' not in session:
            return render_template('carta2.html', posts=carta, sesion='no')
        else:
            return render_template('carta2.html', posts=carta, sesion='si')
    else:
        if 'user' not in session:
            return render_template('carta.html', posts=carta, sesion='no')
        else:
            return render_template('carta.html', posts=carta, sesion='si')

@app.route("/sobre", methods=['GET', 'POST'])
def vista_sobre_generico():
    codigo=request.args.get('valor')
    nombre_set=request.args.get('nombre')
    filtro_sobre={'set_code':codigo}
    sobre=mongo.db.sobres.find_one(filtro_sobre)
    print(sobre)
    if 'user' not in session:
        return render_template('sobre.html', posts=sobre, sesion='no')
    else:
        return render_template('sobre.html', posts=sobre, sesion='si')

@app.route("/comprar_sobre", methods=['GET', 'POST'])
def comprar_sobre():


    codigo_sobre=request.args.get('codigo_sobre')
    precio=float(request.args.get('precio'))
    nombre_sobre=request.args.get('nombre_sobre')
        #print(datos)

    return redirect(url_for('compra_sobre', codigo_sobre=codigo_sobre,nombre_sobre=nombre_sobre))

@app.route("/compra_sobre", methods=['GET', 'POST'])
def compra_sobre():
    codigo_sobre=request.args.get('codigo_sobre')
    nombre_sobre=request.args.get('nombre_sobre')


    nombre_prev=nombre_sobre.lower()
    nombre_prev=nombre_prev.split(" ")
    nombre_final=""
    print(len(nombre_prev))
    for i in range(len(nombre_prev)):
        if i==len(nombre_prev):
            nombre_final+=nombre_prev[i]
        else:
            nombre_final+=nombre_prev[i]+"%20"
    url = "https://db.ygoprodeck.com/api/v7/cardinfo.php?cardset="+nombre_final

    headers = {'user-agent': 'my-app/0.0.1'}
    response = requests.get(url, headers=headers)

    r=response.json()

    final=r["data"]

    n_cartas=len(final)

    cartas=[]
    for aleatorio in range(6):
        cartas.append(final[randrange(n_cartas)])

    return render_template("compra_sobre.html",codigo_sobre=codigo_sobre,cartas=cartas)

@app.route("/agregar_producto", methods=['GET', 'POST'])
def agregar_producto():
    if 'user' not in session:
        flash(f"Por favor inicie sesion", "success")
        return redirect(url_for('index'))
    else:
        id_carta=int(request.args.get('id_carta'))
        precio_carta=float(request.args.get('precio_carta'))
        producto={}
        producto[str(id_carta)]=[1,precio_carta,precio_carta]
        filter={'nom':session['user']}
        llave_usuario=db.find_one(filter)
        llave=str(llave_usuario["_id"])
        aux=[]
        aux2=[]
        aux=mongo.db.cesta.distinct(llave)
        cont=0
        if len(aux)==0:
            aux2.append(producto)
            print(aux2)
            filter={llave:aux}
            datos1={"$set":{llave:aux2}}
            mongo.db.cesta.update_one(filter,datos1)
        else:
            intento=mongo.db.cesta.find({},{llave:1})
            for i in intento:
                if len(i)==2:
                    flag=i
            nuevo=flag[llave]
            for i in range(len(nuevo)):
                for j in nuevo[i]:
                    if j==str(id_carta):
                        nuevo2=[]
                        producto[str(id_carta)][0]=nuevo[i][j][0]+1
                        producto[str(id_carta)][1]=(nuevo[i][j][0]+1)*precio_carta
                        nuevo2.append(producto)
                        for k in range(len(nuevo)):
                            if k!=i:
                                nuevo2.append(nuevo[k])
                        cont=1
                        filter={llave:nuevo}
                        modificar=mongo.db.cesta.update_one(filter,{"$set":{llave:nuevo2}})
            if cont==0:
                filter={llave:nuevo}
                nuevo2=[]
                nuevo2.append(producto)
                #print(nuevo2)
                for i in nuevo:
                    nuevo2.append(i)
                mongo.db.cesta.update_one(filter,{"$set":{llave:nuevo2}})
        return redirect(url_for('cesta'))

@app.route("/cesta")
def cesta():
    if 'user' not in session:
        return render_template('home.html')
    else:
        filter={'nom':session['user']}
        llave_usuario=db.find_one(filter)
        llave=str(llave_usuario["_id"])
        intento=mongo.db.cesta.find({},{llave:1})
        for i in intento:
            if len(i)==2:
                flag=i
        nuevo=flag[llave]
        longitud=len(nuevo)
        total=0.0
        for j in nuevo:
            for k in j:
                total+=j[k][1]
        total=round(total,2)
        return render_template("cesta.html", posts=nuevo, longitud=longitud, pagar=total)

@app.route("/cambio_cantidad", methods=['GET', 'POST'])
def cambio_cantidad():
    id=int(request.args.get('id_carta'))
    nueva_cantidad=int(request.args.get('nueva_cantidad'))
    filter={'nom':session['user']}
    llave_usuario=db.find_one(filter)
    llave=str(llave_usuario["_id"])
    if nueva_cantidad==0:
        cesta=mongo.db.cesta.find({},{llave:1})
        for i in cesta:
            if len(i)==2:
                flag=i
        cesta_usuario=flag[llave]
        for j in range(len(cesta_usuario)):
            for k in cesta_usuario[j]:
                if k==str(id):
                    filter={llave:cesta_usuario}
                    nueva_cesta=[]
                    for l in range(len(cesta_usuario)):
                        if l!=j:
                            nueva_cesta.append(cesta_usuario[l])
                    mongo.db.cesta.update_one(filter,{"$set":{llave:nueva_cesta}})
    else:
        cesta=mongo.db.cesta.find({},{llave:1})
        for i in cesta:
            if len(i)==2:
                flag=i
        cesta_usuario=flag[llave]
        for j in range(len(cesta_usuario)):
            for k in cesta_usuario[j]:
                if k==str(id):
                    filter={llave:cesta_usuario}
                    nuevos_datos=[]
                    nuevos_datos.append(nueva_cantidad)
                    print(cesta_usuario[j][k])
                    nuevos_datos.append(round(cesta_usuario[j][k][2]*nueva_cantidad,2))
                    nuevos_datos.append(cesta_usuario[j][k][2])
                    cambio_producto={}
                    cambio_producto[str(id)]=nuevos_datos
                    nueva_cesta=[]
                    nueva_cesta.append(cambio_producto)
                    for l in range(len(cesta_usuario)):
                        if l!=j:
                            nueva_cesta.append(cesta_usuario[l])
                    mongo.db.cesta.update_one(filter,{"$set":{llave:nueva_cesta}})
    return redirect(url_for('cesta'))

@app.route("/transaccion", methods=['GET', 'POST'])
def transaccion():
    print("transaccion")
    id=int(request.args.get('id_carta'))
    precio=float(request.args.get('precio'))
    print(id)
    print(precio)
    filter={'nom':session['user']}
    llave_usuario=db.find_one(filter)
    llave=str(llave_usuario["_id"])
    usuario=mongo.db.Usuarios.find_one(filter)
    #print(datos)
    if usuario["saldo"]-precio<0.0:
        #print("no se puede comprar")
        return render_template('compra_error.html', posts="Saldo Insuficiente.")
    else:
        #print("compra aceptada")
        cesta=mongo.db.cesta.find({},{llave:1})
        for i in cesta:
            if len(i)==2:
                flag=i


        cesta_usuario=flag[llave]



        coleccion=mongo.db.coleccion.find({},{llave:1})
        for l in coleccion:
            if len(l)==2:
                comodin=l


        coleccion_usuario=comodin[llave]


        historial=mongo.db.historial.find({},{llave:1})
        for m in historial:
            if len(m)==2:
                comodin2=m


        historial_usuario=comodin2[llave]


        #print("coleccion_actual",coleccion_usuario)
        #print("cesta_actual",cesta_usuario)
        #print("historial_actual",historial_usuario)

        filtro_coleccion={llave:coleccion_usuario}
        filtro_cesta={llave:cesta_usuario}
        filtro_historial={llave:historial_usuario}

        historial_final=[]
        coleccion_final=[]
        cesta_final=[]
        fecha=str(date.today())

        if id==0:
            #print("toda la cesta")

            if len(coleccion_usuario)==0:
                #print("no hada en coleccion")
                for j in cesta_usuario:
                    for k in j:

                        historial_mod={}
                        coleccion_mod={}

                        producto_con_fecha=[]
                        producto_con_fecha.append(j[k][0])
                        producto_con_fecha.append(j[k][1])
                        producto_con_fecha.append(j[k][2])
                        producto_con_fecha.append(fecha)

                        coleccion_mod[k]=producto_con_fecha
                        coleccion_final.append(coleccion_mod)

                        historial_mod[k]=producto_con_fecha
                        historial_final.append(historial_mod)

                #print("cesta_final",cesta_final)
                #print("coleccion_final",coleccion_final)
                #print("historial_final",historial_final)

                mod_cesta={"$set":{llave:cesta_final}}
                mod_coleccion={"$set":{llave:coleccion_final}}
                mod_historial={"$set":{llave:historial_final}}
                mod_saldo={"$set":{"saldo":round(usuario["saldo"]-precio,2)}}

                editar_cesta=mongo.db.cesta.update_one(filtro_cesta,mod_cesta)
                editar_coleccion=mongo.db.coleccion.update_one(filtro_coleccion,mod_coleccion)
                editar_historial=mongo.db.historial.update_one(filtro_historial,mod_historial)
                editar_saldo=mongo.db.Usuarios.update_one(filter,mod_saldo)

            else:
                comparaciones=[]
                aux=5
                #print("ya hay cosas en coleccion")
                for p in historial_usuario:
                    for q in p:

                        historial_mod={}

                        producto_con_fecha=[]
                        producto_con_fecha.append(p[q][0])
                        producto_con_fecha.append(p[q][1])
                        producto_con_fecha.append(p[q][2])
                        producto_con_fecha.append(fecha)

                        historial_mod[q]=producto_con_fecha
                        historial_final.append(historial_mod)

                for j in range(len(cesta_usuario)):
                    for k in cesta_usuario[j]:
                        for n in range(len(coleccion_usuario)):
                            for o in coleccion_usuario[n]:
                                if k!=o:
                                    #print("diferentes")
                                    #print("id cesta",k)
                                    #print("id col",o)
                                    aux=0
                                    comparaciones.append(aux)
                                else:
                                    #print("iguales")
                                    #print("id cesta",k)
                                    #print("id col",o)
                                    aux=1
                                    id_col=n
                                    comparaciones.append(aux)
                            if len(comparaciones)!=0:
                                if 1 in comparaciones:
                                    #print("si existe")
                                    if len(comparaciones)==len(coleccion_usuario):
                                        comparaciones=[]

                                        historial_mod={}
                                        coleccion_mod={}
                                        #print("coleccion",n)
                                        #print("cesta",j)
                                        #print("coleccion",coleccion_usuario[id_col])
                                        #print("cesta",cesta_usuario[j])
                                        producto_con_fecha=[]
                                        producto_con_fecha.append(cesta_usuario[j][k][0]+coleccion_usuario[id_col][k][0])
                                        producto_con_fecha.append((cesta_usuario[j][k][0]+coleccion_usuario[id_col][k][0])*cesta_usuario[j][k][2])
                                        producto_con_fecha.append(cesta_usuario[j][k][2])
                                        producto_con_fecha.append(cesta_usuario[j][k][3])

                                        coleccion_mod[k]=producto_con_fecha
                                        coleccion_final.append(coleccion_mod)

                                        historial_mod[k]=producto_con_fecha
                                        historial_final.append(historial_mod)

                                else:
                                    #print("no existe")

                                    if len(comparaciones)==len(coleccion_usuario):
                                        comparaciones=[]
                                        historial_mod={}
                                        coleccion_mod={}
                                        #print("coleccion",n)
                                        #print("cesta",j)

                                        producto_con_fecha=[]
                                        producto_con_fecha.append(cesta_usuario[j][k][0])
                                        producto_con_fecha.append(cesta_usuario[j][k][1])
                                        producto_con_fecha.append(cesta_usuario[j][k][2])
                                        producto_con_fecha.append(fecha)

                                        coleccion_mod[k]=producto_con_fecha
                                        coleccion_final.append(coleccion_mod)

                                        historial_mod[k]=producto_con_fecha
                                        historial_final.append(historial_mod)

                aux=5
                comparaciones=[]
                for r in range(len(coleccion_usuario)):
                    for s in coleccion_usuario[r]:
                        for t in range(len(coleccion_final)):
                            for u in coleccion_final[t]:
                                if s!=u:
                                    #print("id coleccion_final",u)
                                    #print("id coleccion_usuario",s)
                                    aux=0
                                    id_col=s
                                    comparaciones.append(aux)
                                else:
                                    #print("id coleccion_final",u)
                                    #print("id coleccion_usuario",s)
                                    aux=1
                                    comparaciones.append(aux)
                            if len(comparaciones)!=0:
                                if 1 in comparaciones:

                                    if len(comparaciones)==len(coleccion_final):
                                        #print("si existe")
                                        comparaciones=[]

                                        #print("coleccion",n)
                                        #print("cesta",j)


                                else:

                                    if len(comparaciones)==len(coleccion_final):
                                        #print("no existe")
                                        #print("id no repetida",coleccion_usuario[r])
                                        comparaciones=[]

                                        coleccion_mod={}
                                        producto_con_fecha=[]
                                        producto_con_fecha.append(coleccion_usuario[r][s][0])
                                        producto_con_fecha.append(coleccion_usuario[r][s][1])
                                        producto_con_fecha.append(coleccion_usuario[r][s][2])
                                        producto_con_fecha.append(coleccion_usuario[r][s][3])

                                        #print("producto a insertar",producto_con_fecha)

                                        coleccion_mod[id_col]=producto_con_fecha
                                        coleccion_final.append(coleccion_mod)
                                        #print("coleccion",n)
                                        #print("cesta",j)


                #print("coleccion",coleccion_final)
                #print("historial",historial_final)

                mod_cesta={"$set":{llave:cesta_final}}
                mod_coleccion={"$set":{llave:coleccion_final}}
                mod_historial={"$set":{llave:historial_final}}
                mod_saldo={"$set":{"saldo":round(usuario["saldo"]-precio,2)}}

                editar_cesta=mongo.db.cesta.update_one(filtro_cesta,mod_cesta)
                editar_coleccion=mongo.db.coleccion.update_one(filtro_coleccion,mod_coleccion)
                editar_historial=mongo.db.historial.update_one(filtro_historial,mod_historial)
                editar_saldo=mongo.db.Usuarios.update_one(filter,mod_saldo)

        else:
            print("elemento unico de la cesta")
            aux=0
            elemento_cesta={}
            for l in range(len(cesta_usuario)):
                for m in cesta_usuario[l]:
                    if int(m) == id:
                        elemento_cesta[m]=cesta_usuario[l][m]
            #print("elemento_cesta", elemento_cesta)

            if len(coleccion_usuario)==0:
                print("no hay nada en coleccion")

                historial_mod={}
                coleccion_mod={}

                producto_con_fecha=[]
                producto_con_fecha.append(elemento_cesta[str(id)][0])
                producto_con_fecha.append(elemento_cesta[str(id)][1])
                producto_con_fecha.append(elemento_cesta[str(id)][2])
                producto_con_fecha.append(fecha)

                coleccion_mod[str(id)]=producto_con_fecha
                coleccion_final.append(coleccion_mod)

                historial_mod[str(id)]=producto_con_fecha
                historial_final.append(historial_mod)

                for j in range(len(cesta_usuario)):
                    for k in cesta_usuario[j]:
                        if int(k) != id:
                            cesta_final.append(cesta_usuario[j])

            else:
                print("ya ha comprado antes")
                aux=5
                comparaciones=[]
                for j in range(len(coleccion_usuario)):
                    #print(coleccion_usuario[j])
                    for k in coleccion_usuario[j]:
                        #print("id_col",k)
                        #print("id_pro",id)
                        if int(k)==id:

                            print("producto encontrado")

                            aux=1
                            comparaciones.append(aux)


                        else:
                            print("producto no encontrado")

                            aux=0
                            comparaciones.append(aux)

                    if len(comparaciones)==len(coleccion_usuario):
                        if 1 in comparaciones:

                            for s in coleccion_usuario:
                                for t in s:
                                    if t == str(id):


                                        historial_mod={}
                                        coleccion_mod={}


                                        producto_con_fecha=[]
                                        producto_con_fecha.append(s[t][0]+elemento_cesta[str(id)][0])
                                        producto_con_fecha.append(s[t][1]+elemento_cesta[str(id)][1])
                                        producto_con_fecha.append(s[t][2])
                                        producto_con_fecha.append(fecha)

                                        producto_con_fecha_historial=[]
                                        producto_con_fecha_historial.append(elemento_cesta[str(id)][0])
                                        producto_con_fecha_historial.append(elemento_cesta[str(id)][1])
                                        producto_con_fecha_historial.append(s[t][2])
                                        producto_con_fecha_historial.append(fecha)

                                        coleccion_mod[t]=producto_con_fecha
                                        coleccion_final.append(coleccion_mod)

                                        historial_mod[t]=producto_con_fecha_historial
                                        historial_final.append(historial_mod)

                        else:


                            historial_mod={}
                            coleccion_mod={}

                            producto_con_fecha=[]
                            producto_con_fecha.append(elemento_cesta[str(id)][0])
                            producto_con_fecha.append(elemento_cesta[str(id)][1])
                            producto_con_fecha.append(elemento_cesta[str(id)][2])
                            producto_con_fecha.append(fecha)

                            coleccion_mod[str(id)]=producto_con_fecha
                            coleccion_final.append(coleccion_mod)

                            historial_mod[str(id)]=producto_con_fecha
                            historial_final.append(historial_mod)


                for m in range(len(coleccion_usuario)):
                    for n in coleccion_usuario[m]:
                        if int(n)!=id:
                            coleccion_final.append(coleccion_usuario[m])

                for o in range(len(historial_usuario)):
                    for p in historial_usuario[o]:
                        historial_final.append(historial_usuario[o])

                for q in range(len(cesta_usuario)):
                    for r in cesta_usuario[q]:
                        if int(r) != id:
                            cesta_final.append(cesta_usuario[q])

            print("coleccion_final",coleccion_final)
            print("historial_final",historial_final)
            print("cesta_final",cesta_final)

            mod_cesta={"$set":{llave:cesta_final}}
            mod_coleccion={"$set":{llave:coleccion_final}}
            mod_historial={"$set":{llave:historial_final}}
            mod_saldo={"$set":{"saldo":round(usuario["saldo"]-precio,2)}}

            editar_cesta=mongo.db.cesta.update_one(filtro_cesta,mod_cesta)
            editar_coleccion=mongo.db.coleccion.update_one(filtro_coleccion,mod_coleccion)
            editar_historial=mongo.db.historial.update_one(filtro_historial,mod_historial)
            editar_saldo=mongo.db.Usuarios.update_one(filter,mod_saldo)

        return render_template('compra_aceptada.html', posts="Transaccion aceptada.")
    return redirect(url_for('usuario'))

@app.route("/mis_cartas")
def mis_cartas():
    if 'user' not in session:
        return render_template('home.html')
    else:
        filter={'nom':session['user']}
        llave_usuario=db.find_one(filter)
        llave=str(llave_usuario["_id"])
        intento=mongo.db.coleccion.find({},{llave:1})
        for i in intento:
            if len(i)==2:
                flag=i
        coleccion_usuario=flag[llave]
        longitud=len(coleccion_usuario)
        return render_template('mis_cartas.html', posts=coleccion_usuario, longitud=longitud)

@app.route("/mis_mazos", methods=['GET','POST'])
def mis_mazos():

    if 'user' not in session:
        return render_template('home.html')

    else:
        nombre=""
        aux=0
        filter={'nom':session['user']}
        llave_usuario=db.find_one(filter)
        llave=str(llave_usuario["_id"])
        intento=mongo.db.mazos.find({},{llave:1})
        nuevo_mazo={}

        for i in intento:
            if len(i)==2:
                flag=i

        mazos_usuario=flag[llave]
        longitud=len(mazos_usuario)
        print("mazos_actuales",mazos_usuario)

        form=Mazo()

        if form.validate_on_submit():

            print("funciona")

            for j in mazos_usuario:
                    corte=slice(0,len(j)-3)
                    if form.nombre.data==j or form.nombre.data==j[corte]:
                        aux+=1
            if aux>0:
                nombre=form.nombre.data+"("+str(aux)+")"
                mazo_final={}
                mazo_final[nombre]=[]
            else:
                nuevo_mazo[form.nombre.data]={}
                mazo_final={}
                mazo_final[form.nombre.data]=[]
            for i in mazos_usuario:
                mazo_final[i]=mazos_usuario[i]
            print("mazos_nuevos",mazos_usuario)
            mongo.db.mazos.update_one({llave:mazos_usuario},{"$set":{llave:mazo_final}})
            return redirect(url_for('mis_mazos'))

        return render_template('mis_mazos.html', posts=mazos_usuario, longitud=longitud, form=form)

@app.route("/borrar_mazo", methods=['GET','POST'])
def borrar_mazo():
    if 'user' not in session:
        return render_template('home.html')

    else:
        nombre_mazo=request.args.get('nombre_mazo')
        nombre=""
        aux=0
        filter={'nom':session['user']}
        llave_usuario=db.find_one(filter)
        llave=str(llave_usuario["_id"])
        intento=mongo.db.mazos.find({},{llave:1})
        mazos_final={}

        for i in intento:
            if len(i)==2:
                flag=i

        mazos_usuario=flag[llave]
        #print(nombre_mazo)
        #print(mazos_usuario)


        for j in mazos_usuario:
                if j!=nombre_mazo:
                    nuevo_mazo={}
                    nuevo_mazo[j]=mazos_usuario[j]

                    mazos_final[j]=nuevo_mazo[j]

        print("mazos final",mazos_final)
        filtro_mazos={llave:mazos_usuario}
        mod_mazos={"$set":{llave:mazos_final}}
        mongo.db.mazos.update_one(filtro_mazos,mod_mazos)

        return redirect(url_for('mis_mazos'))


#tocarlo cambio de estructura bbdd
@app.route("/editar_mazo", methods=['GET','POST'])
def editar_mazo():
    if 'user' not in session:
        return render_template('home.html')

    else:
        nombre_mazo=request.args.get('nombre_mazo')
        carta_editar=request.args.get('carta_editar')
        estado=str(request.args.get('estado'))
        print(estado)
        print(carta_editar)
        nombre=""
        aux=0
        filter={'nom':session['user']}
        llave_usuario=db.find_one(filter)
        llave=str(llave_usuario["_id"])
        intento=mongo.db.mazos.find({},{llave:1})
        intento2=mongo.db.coleccion.find({},{llave:1})
        for i in intento:
            if len(i)==2:
                flag=i
        for j in intento2:
            if len(j)==2:
                flag2=j
        coleccion_usuario=flag2[llave]
        mazos_usuario=flag[llave]
        longitud=0
        print(mazos_usuario)
        for k in mazos_usuario[nombre_mazo]:
            for l in k:
                print(l)
                longitud+=k[l]
        print("longitud",longitud)
        aux=0
        aux2=0
        mazo_mod={}
        if estado=='True':
            print("añadir")
            mazo_mod={}
            mazo_mod[nombre_mazo]=[]
            print(mazos_usuario[nombre_mazo])
            for carta in mazos_usuario[nombre_mazo]:
                for id_carta in carta:
                    print(id_carta)
                    print(carta_editar)
                    if id_carta==carta_editar:
                        carta_mod={}
                        aux2=1
                        aux=0
                        if carta[id_carta]<3:
                            carta_mod[id_carta]=carta[id_carta]+1
                            longitud+=1
                            mazo_mod[nombre_mazo].append(carta_mod)
                        else:
                            carta_mod[id_carta]=3
                            mazo_mod[nombre_mazo].append(carta_mod)
                    else:

                        carta_mod={}
                        print(carta)
                        carta_mod[id_carta]=carta[id_carta]
                        mazo_mod[nombre_mazo].append(carta_mod)
                        aux=0
            if aux==0 and aux2==0:
                print("no encontrada")
                carta_mod={}
                carta_mod[carta_editar]=1
                mazo_mod[nombre_mazo].append(carta_mod)
                print(mazo_mod)
                longitud+=1
            else :
                print("encontrada")
        else:
            print("eliminar")
            mazo_mod={}
            mazo_mod[nombre_mazo]=[]
            for carta in mazos_usuario[nombre_mazo]:
                for id_carta in carta:
                    if id_carta==carta_editar:
                        carta_mod={}
                        if carta[id_carta]>1:
                            carta_mod[id_carta]=carta[id_carta]-1
                            mazo_mod[nombre_mazo].append(carta_mod)
                            longitud-=1
                    else:
                        carta_mod={}
                        print(carta)
                        carta_mod[id_carta]=carta[id_carta]
                        mazo_mod[nombre_mazo].append(carta_mod)

        for mazos in mazos_usuario:
            print("for raro",mazos)
            if mazos!=nombre_mazo:
                mazo_mod[mazos]=mazos_usuario[mazos]



        carta_mod={}
        filtro_mazos={}
        mod_mazos={}

        print("mazos_final",mazo_mod)
        print("no cambies crack",mazos_usuario)
        filtro_mazos={llave:mazos_usuario}
        print("filtros",filtro_mazos)
        mod_mazos={"$set":{llave:mazo_mod}}
        print("mod_mazos",mod_mazos)
        mongo.db.mazos.update_one(filtro_mazos,mod_mazos)
        print("actualizado")


        #elif estado==False:
        #print(nombre_mazo)
        #print(longitud)
        #print("estado",estado)
        print(type(coleccion_usuario))
        return redirect(url_for('vista_mazo',mazo=nombre_mazo,longitud=longitud))


@app.route("/vista_mazo", methods=['GET','POST'])
def vista_mazo():
    filter={'nom':session['user']}
    llave_usuario=db.find_one(filter)
    llave=str(llave_usuario["_id"])
    intento=mongo.db.mazos.find({},{llave:1})
    intento2=mongo.db.coleccion.find({},{llave:1})
    for i in intento:
        if len(i)==2:
            flag=i
    for j in intento2:
        if len(j)==2:
            flag2=j
    coleccion_usuario=flag2[llave]
    mazos_usuario=flag[llave]
    nombre_mazo=request.args.get('mazo')
    if request.args.get('longitud'):
        longitud=int(request.args.get('longitud'))
    else:
        longitud=0
    return render_template('editar_mazo.html',mazo=nombre_mazo,cartas=coleccion_usuario,longitud=longitud,mazo_actual=mazos_usuario[nombre_mazo])

@app.route("/sobres")
def sobres():
    search=False

    q=request.args.get('q')

    if q:
        search=True

    page = request.args.get(get_page_parameter(), type=int, default=1)

    sobre=mongo.db.sobres

    if page>1:
        sobres=sobre.find().skip((page-1)*10).limit(10)
    else:
        sobres=sobre.find().limit(10)

    pagination= Pagination(page=page, total=sobres.count(), search=search, record_name='sobres')
    if 'user' not in session:
        return render_template('sobres.html', posts=sobres, pagination=pagination, sesion='no')
    else:
        return render_template('sobres.html', posts=sobres, pagination=pagination, sesion='si')

@app.route("/historial")
def historial():
    if 'user' not in session:
        return render_template('home.html')
    else:
        filter={'nom':session['user']}
        llave_usuario=db.find_one(filter)
        llave=str(llave_usuario["_id"])
        intento=mongo.db.historial.find({},{llave:1})
        for i in intento:
            if len(i)==2:
                flag=i
        historial_usuario=flag[llave]
        longitud=len(historial_usuario)
        return render_template('historial.html', posts=historial_usuario, longitud=longitud)



if __name__=='__main__':
    app.run(debug=True)
    app.run(ssl_context='adhoc')
