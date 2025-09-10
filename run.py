from app import app, db
from flask_migrate import Migrate
from app.models import Usuario, Producto, Categoria, Proveedor, CarritoCompras, DetalleCarrito, Pedido, DetallePedido, Resena, Descuento, VarianteProducto, ImagenProducto

migrate = Migrate(app, db)
if __name__ == '__main__':
    app.run(debug=True)
    # Crea todas las tablas en la base de datos si no existen
    # Nota: Esto es solo para desarrollo. En producción, se usan migraciones (Flask-Migrate)
    with app.app_context():
        db.create_all()
    
    # Inicia el servidor de desarrollo de Flask
    # debug=True permite que el servidor se recargue automáticamente al hacer cambios
    app.run(debug=True)