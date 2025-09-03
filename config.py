import os

class Config:
    # Configuración de la base de datos PostgreSQL
    # 'postgresql://usuario:contraseña@host:puerto/nombre_base_de_datos'
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:12345@localhost:5432/mipap'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Clave secreta para la seguridad de las sesiones de la aplicación.
    # Es recomendable usar una variable de entorno para esto en producción.
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'una_clave_secreta_muy_larga_y_dificil_de_adivinar'