from flask import render_template, url_for, flash, redirect, request
from app import app, db, bcrypt
from app.models import Usuario, Producto, CarritoCompras, DetalleCarrito
from flask_login import login_user, current_user, logout_user, login_required
from sqlalchemy.exc import IntegrityError
from flask_mail import Message, Mail
from itsdangerous import URLSafeTimedSerializer
import os


# Inicializa el serializador para crear tokens seguros
# Debe usar la misma clave secreta de la app
s = URLSafeTimedSerializer(app.config['SECRET_KEY'])
mail = Mail(app)

# -- Rutas existentes --

# La página de inicio, visible para todos los usuarios
@app.route("/")
@app.route("/inicio")
def inicio():
    productos = Producto.query.all()
    return render_template('inicio.html', titulo='Inicio', productos=productos)

# -- Rutas de Autenticación --

# Ruta para el registro de nuevos usuarios
@app.route("/registro", methods=['GET', 'POST'])
def registro():
    if current_user.is_authenticated:
        return redirect(url_for('inicio'))
    
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        email = request.form.get('email')
        password = request.form.get('password')
        telefono = request.form.get('telefono')
        direccion_envio = request.form.get('direccion_envio')
        direccion_facturacion = request.form.get('direccion_facturacion')

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        
        try:
            nuevo_usuario = Usuario(
                nombre=nombre,
                email=email,
                password_hash=hashed_password,
                telefono=telefono,
                direccion_envio=direccion_envio,
                direccion_facturacion=direccion_facturacion
            )
            db.session.add(nuevo_usuario)
            db.session.commit()
            
            # Genera el token de confirmación
            token = s.dumps(email, salt='email-confirm')
            
            # Crea y envía el mensaje de correo
            msg = Message(
                'Confirma tu correo electrónico',
                sender='tienda_papeleria@gmail.com', # Cambia esto a un correo real si no usas la variable de entorno
                recipients=[email]
            )
            link = url_for('confirmar_email', token=token, _external=True)
            msg.body = f'Tu enlace de confirmación es {link}'
            msg.html = render_template('email_confirmacion.html', link=link)
            mail.send(msg)
            
            flash('¡Registro exitoso! Por favor, revisa tu correo electrónico para confirmar tu cuenta.', 'success')
            return redirect(url_for('login'))
        
        except IntegrityError:
            db.session.rollback()
            flash('El correo electrónico ya está en uso. Por favor, elige uno diferente.', 'danger')
            return redirect(url_for('registro'))
        
    return render_template('registro.html', titulo='Registro')


# Ruta para iniciar sesión
@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('inicio'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        usuario = Usuario.query.filter_by(email=email).first()

        if usuario and bcrypt.check_password_hash(usuario.password_hash, password):
            login_user(usuario, remember=True)
            flash(f'¡Bienvenido de nuevo, {usuario.nombre}!', 'success')
            return redirect(url_for('inicio'))
        else:
            flash('Inicio de sesión fallido. Por favor, verifica tu correo electrónico y contraseña.', 'danger')
    
    return render_template('login.html', titulo='Iniciar Sesión')

# Ruta para cerrar sesión
@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión exitosamente.', 'success')
    return redirect(url_for('inicio'))

# -- Nuevas rutas para la confirmación de correo --

@app.route('/confirmar/<token>')
def confirmar_email(token):
    try:
        email = s.loads(token, salt='email-confirm', max_age=3600)  # Token válido por 1 hora
    except:
        flash('El enlace de confirmación es inválido o ha expirado.', 'danger')
        return redirect(url_for('email_fallido'))

    usuario = Usuario.query.filter_by(email=email).first_or_404()
    if usuario.email_confirmado:
        flash('Tu cuenta ya ha sido confirmada.', 'info')
        return redirect(url_for('login'))
    
    usuario.email_confirmado = True
    db.session.commit()

    flash('¡Tu cuenta ha sido confirmada exitosamente! Ahora puedes iniciar sesión.', 'success')
    return redirect(url_for('email_exitoso'))


@app.route("/email_exitoso")
def email_exitoso():
    return render_template("email_exitoso.html")

@app.route("/email_fallido")
def email_fallido():
    return render_template("email_fallido.html")


# -- Rutas restantes --
# (perfil, carrito, etc.)
@app.route("/perfil")
@login_required
def perfil():
    return render_template('perfil.html', titulo='Perfil de Usuario')


@app.route("/carrito")
@login_required
def carrito():
    # Obtener el carrito del usuario actual
    carrito_usuario = CarritoCompras.query.filter_by(id_usuario=current_user.id).first()
    detalles_carrito = []
    total_carrito = 0

    if carrito_usuario:
        detalles_carrito = DetalleCarrito.query.filter_by(id_carrito=carrito_usuario.id).all()
        for detalle in detalles_carrito:
            total_carrito += detalle.producto.precio_venta * detalle.cantidad
    
    return render_template('carrito.html', titulo='Tu Carrito de Compras', detalles=detalles_carrito, total=total_carrito)


# Ruta para añadir un producto al carrito
@app.route("/anadir_al_carrito/<int:producto_id>", methods=['POST'])
@login_required
def anadir_al_carrito(producto_id):
    producto = Producto.query.get_or_404(producto_id)
    cantidad = int(request.form.get('cantidad', 1))

    # Obtener o crear el carrito del usuario
    carrito_usuario = CarritoCompras.query.filter_by(id_usuario=current_user.id).first()
    if not carrito_usuario:
        carrito_usuario = CarritoCompras(id_usuario=current_user.id)
        db.session.add(carrito_usuario)
        db.session.commit()

    # Buscar si el producto ya está en el carrito
    detalle_existente = DetalleCarrito.query.filter_by(id_carrito=carrito_usuario.id, id_producto=producto_id).first()

    if detalle_existente:
        # Si ya existe, solo actualiza la cantidad
        detalle_existente.cantidad += cantidad
    else:
        # Si no existe, crea una nueva entrada en detalle_carrito
        nuevo_detalle = DetalleCarrito(
            id_carrito=carrito_usuario.id,
            id_producto=producto_id,
            cantidad=cantidad
        )
        db.session.add(nuevo_detalle)
    
    db.session.commit()
    flash(f'{cantidad} x {producto.nombre} añadido a tu carrito.', 'success')
    return redirect(url_for('carrito'))
