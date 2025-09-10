import os

class Config:
    # Configuración de la base de datos PostgreSQL
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:12345@localhost:5432/mipap'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Clave secreta para la seguridad de las sesiones de la aplicación.
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'una_clave_secreta_muy_larga_y_dificil_de_adivinar'


    # Configuración de correo electrónico para Flask-Mail
    # IMPORTANTE: Reemplaza estos valores con los de tu cuenta de correo real.
    # Si usas Gmail, necesitas generar una 'contraseña de aplicación' en la configuración de seguridad de Google.
    # No uses tu contraseña normal.
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('EMAIL_USER') or 'tiendapapeleria8@gmail.com'  # <-- TU CORREO DE GMAIL AQUÍ
    MAIL_PASSWORD = os.environ.get('EMAIL_PASS') or 'fvalwlbzxuxydbae' # <-- TU CONTRASEÑA DE APLICACIÓN AQUÍ

