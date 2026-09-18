# app/dao/conexion.py 
"""
Capa de Persistencia - Módulo de Conexión
Gestiona la conexión a PostgreSQL usando psycopg2
"""
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import sql
from app.config import Config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConexionDB:
    """
    Clase Singleton para gestionar la conexión.
    En modo demo no se conecta a PostgreSQL; usa memoria local reiniciable.
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._connection = None
        return cls._instance
    
    def conectar(self):
        """Establece conexión con la base de datos PostgreSQL."""
        if Config.DEMO_MODE:
            logger.info("Modo demo activo: sin base de datos externa")
            return None
        try:
            if self._connection is None or self._connection.closed:
                self._connection = psycopg2.connect(
                    host=Config.DB_HOST,
                    port=Config.DB_PORT,
                    database=Config.DB_NAME,
                    user=Config.DB_USER,
                    password=Config.DB_PASSWORD
                )
                self._connection.autocommit = False
                logger.info(" Conexión a PostgreSQL establecida")
            return self._connection
        except psycopg2.Error as e:
            logger.error(f" Error de conexión: {e}")
            raise
    
    def cerrar(self):
        """Cierra la conexión actual"""
        if self._connection and not self._connection.closed:
            self._connection.close()
            logger.info(" Conexión cerrada")
    
    def get_cursor(self, dictionary=True):
        """Devuelve un cursor o None en modo demo."""
        if Config.DEMO_MODE:
            return None
        conn = self.conectar()
        if conn is None:
            return None
        if conn.get_transaction_status() == psycopg2.extensions.TRANSACTION_STATUS_INERROR:
            logger.warning(" Transacción abortada detectada, haciendo ROLLBACK...")
            conn.rollback()
        if dictionary:
            return conn.cursor(cursor_factory=RealDictCursor)
        return conn.cursor()
    
    def commit(self):
        """Confirma transacción actual"""
        if self._connection:
            self._connection.commit()
    
    def rollback(self):
        """Revierte transacción actual en caso de error"""
        if self._connection:
            self._connection.rollback()
            logger.info(" Rollback ejecutado")


# Instancia global para uso en DAOs
db = ConexionDB()