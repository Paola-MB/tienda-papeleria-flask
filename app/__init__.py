from flask import Flask, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, current_user, UserMixin
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from config import Config
from flask_mail import Mail # Importa Flask-Mail


# Inicialización de la aplicación Flask y sus extensiones
app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
login_manager.login_message = "Por favor, inicia sesión para acceder a esta página."
mail = Mail(app)

# Crea una clase de vista de modelo personalizada para proteger las tablas
class MyModelView(ModelView):
    # Método que verifica si el usuario tiene permiso para acceder a la vista
    def is_accessible(self):
        # El acceso es permitido si el usuario está autenticado y su rol es 'admin'
        return current_user.is_authenticated and current_user.rol == 'admin'
    
    # Método para manejar el caso cuando el usuario no tiene permisos
    def inaccessible_callback(self, name, **kwargs):
        # Redirige al usuario a la página de inicio de sesión
        return redirect(url_for('login', next=request.url))

# Inicializa Flask-Admin y usa una vista personalizada para la página principal del panel
class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.rol == 'admin'
        
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login', next=request.url))

admin = Admin(app, name='Panel de Administración', template_mode='bootstrap3', index_view=MyAdminIndexView())

# Importar las rutas y los modelos después de inicializar las extensiones para evitar errores de importación circular
from app import routes, models

# Flask-Login necesita una función para cargar un usuario de la base de datos
@login_manager.user_loader
def load_user(user_id):
    # Si el usuario no existe, devuelve None para indicar que la sesión es inválida
    return Usuario.query.get(int(user_id)) if Usuario.query.get(int(user_id)) else None

# Asegúrate de importar todos los modelos que quieres gestionar en el panel de administración
from app.models import (Usuario, Producto, Categoria, Proveedor,
                        VarianteProducto, ImagenProducto, Pedido,
                        DetallePedido, CarritoCompras, DetalleCarrito,
                        Resena, Descuento)

# Añade los modelos a Flask-Admin para crear la interfaz CRUD
# Usa la clase MyModelView para proteger cada vista del panel
admin.add_view(MyModelView(Usuario, db.session, name='Usuarios'))
admin.add_view(MyModelView(Producto, db.session, name='Productos'))
admin.add_view(MyModelView(Categoria, db.session, name='Categorías'))
admin.add_view(MyModelView(Proveedor, db.session, name='Proveedores'))
admin.add_view(MyModelView(VarianteProducto, db.session, name='Variantes de Producto'))
admin.add_view(MyModelView(ImagenProducto, db.session, name='Imágenes de Producto'))
admin.add_view(MyModelView(Pedido, db.session, name='Pedidos'))
admin.add_view(MyModelView(DetallePedido, db.session, name='Detalles de Pedido'))
admin.add_view(MyModelView(CarritoCompras, db.session, name='Carritos de Compras'))
admin.add_view(MyModelView(DetalleCarrito, db.session, name='Detalles de Carrito'))
admin.add_view(MyModelView(Resena, db.session, name='Reseñas'))
admin.add_view(MyModelView(Descuento, db.session, name='Descuentos'))