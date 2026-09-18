# app/config.py
"""
Configuración centralizada de la aplicación
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Modo demo: toda la app queda local y reiniciable sin base de datos externa
    DEMO_MODE = os.getenv('DEMO_MODE', 'true').lower() == 'true'

    # Base de datos PostgreSQL (no usada en demo)
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'servicios')
    DB_USER = os.getenv('DB_USER', 'usuario')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '12345678')
    
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', '12345678')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'