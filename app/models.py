from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime
from sqlalchemy.dialects.postgresql import ENUM

# El mixin UserMixin de Flask-Login proporciona métodos esenciales para la autenticación
class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    telefono = db.Column(db.String(20))
    direccion_envio = db.Column(db.Text)
    direccion_facturacion = db.Column(db.Text)
    rol = db.Column(db.String(50), default='cliente')
    creado_en = db.Column(db.TIMESTAMP(timezone=True), default=datetime.now)

    def __repr__(self):
        return f"Usuario('{self.nombre}', '{self.email}')"

class Categoria(db.Model):
    __tablename__ = 'categorias'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False, unique=True)
    productos = db.relationship('Producto', backref='categoria', lazy=True)

class Proveedor(db.Model):
    __tablename__ = 'proveedores'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    contacto = db.Column(db.String(100))
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(100), unique=True)
    productos = db.relationship('Producto', backref='proveedor', lazy=True)

class Producto(db.Model):
    __tablename__ = 'productos'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    precio_compra = db.Column(db.Numeric(10, 2), nullable=False)
    precio_venta = db.Column(db.Numeric(10, 2), nullable=False)
    stock = db.Column(db.Integer, nullable=False, default=0)
    id_categoria = db.Column(db.Integer, db.ForeignKey('categorias.id'))
    id_proveedor = db.Column(db.Integer, db.ForeignKey('proveedores.id'))

    variantes = db.relationship('VarianteProducto', backref='producto', lazy=True, cascade="all, delete-orphan")
    imagenes = db.relationship('ImagenProducto', backref='producto', lazy=True, cascade="all, delete-orphan")
    pedidos_detalle = db.relationship('DetallePedido', backref='producto', lazy=True)
    resenas = db.relationship('Resena', backref='producto', lazy=True)
    carrito_detalle = db.relationship('DetalleCarrito', backref='producto', lazy=True)

class VarianteProducto(db.Model):
    __tablename__ = 'variantes_producto'
    id = db.Column(db.Integer, primary_key=True)
    id_producto = db.Column(db.Integer, db.ForeignKey('productos.id', ondelete='CASCADE'), nullable=False)
    nombre_variante = db.Column(db.String(50), nullable=False)
    valor_variante = db.Column(db.String(50), nullable=False)
    precio_adicional = db.Column(db.Numeric(10, 2), default=0)
    stock_variante = db.Column(db.Integer, nullable=False, default=0)
    __table_args__ = (db.UniqueConstraint('id_producto', 'nombre_variante', 'valor_variante'),)

class ImagenProducto(db.Model):
    __tablename__ = 'imagenes_producto'
    id = db.Column(db.Integer, primary_key=True)
    id_producto = db.Column(db.Integer, db.ForeignKey('productos.id', ondelete='CASCADE'), nullable=False)
    url_imagen = db.Column(db.String(255), nullable=False)
    es_principal = db.Column(db.Boolean, default=False)

class Pedido(db.Model):
    __tablename__ = 'pedidos'
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.TIMESTAMP(timezone=True), default=datetime.now)
    total = db.Column(db.Numeric(10, 2), nullable=False)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    estado_pedido = db.Column(db.String(50), default='pendiente')
    metodo_pago = db.Column(db.String(50))
    metodo_envio = db.Column(db.String(50))
    numero_seguimiento = db.Column(db.String(100))
    detalles = db.relationship('DetallePedido', backref='pedido', lazy=True)

class DetallePedido(db.Model):
    __tablename__ = 'detalle_pedidos'
    id = db.Column(db.Integer, primary_key=True)
    id_pedido = db.Column(db.Integer, db.ForeignKey('pedidos.id', ondelete='CASCADE'), nullable=False)
    id_producto = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Numeric(10, 2), nullable=False)

class CarritoCompras(db.Model):
    __tablename__ = 'carrito_compras'
    id = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='CASCADE'), unique=True, nullable=False)
    creado_en = db.Column(db.TIMESTAMP(timezone=True), default=datetime.now)
    detalles = db.relationship('DetalleCarrito', backref='carrito', lazy=True, cascade="all, delete-orphan")

class DetalleCarrito(db.Model):
    __tablename__ = 'detalle_carrito'
    id = db.Column(db.Integer, primary_key=True)
    id_carrito = db.Column(db.Integer, db.ForeignKey('carrito_compras.id', ondelete='CASCADE'), nullable=False)
    id_producto = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    __table_args__ = (db.UniqueConstraint('id_carrito', 'id_producto'),)

class Resena(db.Model):
    __tablename__ = 'resenas'
    id = db.Column(db.Integer, primary_key=True)
    id_producto = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    calificacion = db.Column(db.Integer, nullable=False)
    comentario = db.Column(db.Text)
    fecha_resena = db.Column(db.TIMESTAMP(timezone=True), default=datetime.now)
    __table_args__ = (db.UniqueConstraint('id_producto', 'id_usuario'),)

class Descuento(db.Model):
    __tablename__ = 'descuentos'
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    descripcion = db.Column(db.String(255))
    tipo_descuento = db.Column(db.String(20), nullable=False)
    valor = db.Column(db.Numeric(10, 2), nullable=False)
    fecha_inicio = db.Column(db.TIMESTAMP(timezone=True), default=datetime.now)
    fecha_fin = db.Column(db.TIMESTAMP(timezone=True))
    usos_maximos = db.Column(db.Integer)
    usos_actuales = db.Column(db.Integer, default=0)