from flask import render_template, url_for, flash, redirect, request
from app import app, db, bcrypt
from app.models import Usuario, Producto, CarritoCompras, DetalleCarrito
from flask_login import login_user, current_user, logout_user, login_required
from sqlalchemy.exc import IntegrityError # Importa esto para manejar errores de duplicidad


# La página de inicio, visible para todos los usuarios
@app.route("/")
@app.route("/inicio")
def inicio():
    # Consulta todos los productos de la base de datos
    productos = Producto.query.all()
    # Pasa la lista de productos a la plantilla 'inicio.html'
    return render_template('inicio.html', titulo='Inicio', productos=productos)

# ---

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
        
        nuevo_usuario = Usuario(
            nombre=nombre,
            email=email,
            password_hash=hashed_password,
            telefono=telefono,
            direccion_envio=direccion_envio,
            direccion_facturacion=direccion_facturacion
        )
        
        try:
            db.session.add(nuevo_usuario)
            db.session.commit()
            flash('¡Tu cuenta ha sido creada exitosamente! Ahora puedes iniciar sesión.', 'success')
            return redirect(url_for('login'))
        except IntegrityError:
            db.session.rollback()
            flash('El correo electrónico ya está registrado. Por favor, utiliza otro.', 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f'Ocurrió un error inesperado al crear la cuenta: {e}', 'danger')
    
    return render_template('registro.html', titulo='Registro')
# ---

# Ruta para el inicio de sesión
@app.route("/login", methods=['GET', 'POST'])
def login():
    # Si el usuario ya está autenticado, redirigirlo a la página de inicio
    if current_user.is_authenticated:
        return redirect(url_for('inicio'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # 1. Depuración: Imprime los datos recibidos del formulario
        print(f"Intento de inicio de sesión para el email: {email}")
        
        # Busca al usuario en la base de datos por su email
        usuario = Usuario.query.filter_by(email=email).first()
        
        # 2. Depuración: Verifica si el usuario fue encontrado en la base de datos
        if not usuario:
            print("Usuario no encontrado en la base de datos.")
            flash('Error de inicio de sesión. Por favor, verifica tu correo electrónico y contraseña.', 'danger')
            return render_template('login.html', titulo='Iniciar Sesión')

        # 3. Depuración: Verifica si la contraseña es correcta
        if bcrypt.check_password_hash(usuario.password_hash, password):
            print("Contraseña correcta. Iniciando sesión...")
            login_user(usuario)
            flash('Has iniciado sesión exitosamente.', 'success')
            # 4. Depuración: Verifica si la redirección ocurre
            print("Redireccionando a la página de inicio...")
            return redirect(url_for('inicio'))
        else:
            print("Contraseña incorrecta.")
            flash('Error de inicio de sesión. Por favor, verifica tu correo electrónico y contraseña.', 'danger')
            
    # Muestra el formulario de inicio de sesión (método GET)
    return render_template('login.html', titulo='Iniciar Sesión')


# ---

# Ruta para cerrar la sesión
@app.route("/logout")
@login_required # Requiere que el usuario esté autenticado para acceder
def logout():
    logout_user()
    flash('Has cerrado sesión exitosamente.', 'info')
    return redirect(url_for('inicio'))

# ---

# Ruta para el perfil del usuario
@app.route("/perfil")
@login_required # Solo los usuarios autenticados pueden ver esta página
def perfil():
    return render_template('perfil.html', titulo='Perfil')


# Ruta para ver el carrito de compras del usuario actual
@app.route("/carrito")
@login_required
def carrito():
    # Obtener el carrito del usuario actual
    carrito_usuario = CarritoCompras.query.filter_by(id_usuario=current_user.id).first()
    
    # Si el usuario no tiene carrito, se crea uno
    if not carrito_usuario:
        carrito_usuario = CarritoCompras(id_usuario=current_user.id)
        db.session.add(carrito_usuario)
        db.session.commit()
    
    # Cargar los detalles del carrito
    detalles_carrito = DetalleCarrito.query.filter_by(id_carrito=carrito_usuario.id).all()
    
    # Aquí puedes calcular el total del carrito si lo necesitas
    total_carrito = sum(detalle.producto.precio_venta * detalle.cantidad for detalle in detalles_carrito)
    
    return render_template('carrito.html', titulo='Tu Carrito de Compras', detalles=detalles_carrito, total=total_carrito)

# ---
#
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
    flash(f'{producto.nombre} se ha añadido a tu carrito.', 'success')
    return redirect(url_for('inicio')) # Redirige a la página de inicio o a la que desees