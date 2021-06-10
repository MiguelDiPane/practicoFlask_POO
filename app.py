from datetime import datetime
import hashlib
from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash,check_password_hash

app = Flask(__name__)
app.config.from_pyfile('config.py')

from models import db
from models import Usuario, Movil, Viaje


#http://127.0.0.1:5000/inicio
@app.route('/inicio')
def inicio():
    return render_template('index.html')

@app.route('/iniciar_sesion')
def iniciar_sesion():
    return render_template('iniciar_sesion.html', iniciarSesion=True)

@app.route('/usuario', methods=['GET','POST'])
def usuario():
    if request.method == 'POST':
        usuario_actual =  Usuario.query.filter_by(dni=request.form['usuario']).first()
        if usuario_actual is None:
            return render_template('iniciar_sesion.html', iniciarSesion=True, usuario = False)
        else:
            #verifico password
            clave = request.form['password']
            clave_cifrada = hashlib.md5(bytes(clave, encoding='utf-8'))
            if clave_cifrada.hexdigest() == usuario_actual.clave or clave == usuario_actual.clave:
                #Envio como dato el usuario para saber que funcionalidades tiene y tipo
                if usuario_actual.tipo == 'cli':
                    #Cargo viajes del usuario
                    viajes_usuario_actual = cargar_viajes_usuario(request.form['usuario'])
                    return render_template('funcionalidades_cliente.html', datos=usuario_actual, viajes = viajes_usuario_actual)
                elif usuario_actual.tipo == 'op':
                    return render_template('funcionalidades_operador.html', datos=usuario_actual)
            else:
                return render_template('iniciar_sesion.html',iniciarSesion=True, password = False)
    elif request.method == 'GET':
        pass

@app.route('/formulario_registrar_usuario')
def formulario_registrar_usuario():
    return render_template('iniciar_sesion.html',registrarUsuario=True)

@app.route('/registrar_usuario', methods=['GET','POST'])
def registrar_usuario():
    if request.method == 'POST':
        #chequear si el usuario ya esta registrado o no y mostrar el mensaje
        usuario =  Usuario.query.filter_by(dni=request.form['dni']).first()
        if usuario == None:
            #Cifro contraseña antes de crear el usuario:
            clave = request.form['password']
            clave_cifrada = hashlib.md5(bytes(clave, encoding='utf-8'))
            #Agrego el nuevo usuario por defecto de tipo cliente
            nuevo_usuario = Usuario(
                dni = request.form['dni'],
                nombre = request.form['nombre'],
                clave = clave_cifrada.hexdigest(),
                tipo = 'cli'
            )
            db.session.add(nuevo_usuario)
            db.session.commit()
            #Mostrar el mensaje en la planilla
            return render_template('iniciar_sesion.html', registrarUsuario=True, exito=True)
        else:
            return render_template('iniciar_sesion.html', registrarUsuario=True, usuarioRegistrado=True)


#-------------------------------------#
#       FUNCIONALIDADES CLIENTE       #
#-------------------------------------#
@app.route('/solicitar_viaje', methods=['GET','POST'])
def solicitar_viaje():
    if request.method == 'POST':
        nuevo_viaje = Viaje(
            #idViaje se carga solo?
            origen = request.form['dirOrigen'],
            destino = request.form['dirDestino'],
            fecha = datetime.today(),
            importe = 0.0,
            dniCliente = request.form['dni'] #el numero de movil lo asigna el operario
        )
        usuario_actual =  Usuario.query.filter_by(dni=request.form['dni']).first()
        db.session.add(nuevo_viaje)
        db.session.commit()
        return  render_template('funcionalidades_cliente.html', datos = usuario_actual, exito = True)

#Carga viajes del usuario
def cargar_viajes_usuario(dni):
     viajes =  Viaje.query.all()
     print(viajes)
     return viajes







if __name__ == '__main__':
    db.create_all()
    app.run(debug = True)