# app/dao/estatus_orden_dao.py
"""
DAO para la entidad EstatusOrden
"""
from app.dao.base_dao import BaseDAO
from app.models.estatus_orden import EstatusOrden

class EstatusOrdenDAO(BaseDAO):
    @property
    def tabla(self):
        return "estatus_orden"
    
    @property
    def primary_key(self):
        return "id_estatus"
    
    def mapear_a_objeto(self, fila):
        if fila is None:
            return None
        return EstatusOrden(
            id_estatus=fila.get('id_estatus'),
            nombre_estatus=fila.get('nombre_estatus'),
            descripcion=fila.get('descripcion'),
            color_hex=fila.get('color_hex'),
            orden_secuencial=fila.get('orden_secuencial'),
            activo=fila.get('activo')
        )
    
    def listar_todos(self, limite=None, offset=None):
        """Sobrescribe para ordenar por secuencia de flujo de trabajo"""
        from app.config import Config
        if Config.DEMO_MODE:
            registros = [
                fila for fila in self.buscar_por_criterio('activo', True)
            ]
            registros.sort(key=lambda fila: (fila.orden_secuencial, fila.id_estatus))
            if offset:
                registros = registros[offset:]
            if limite is not None:
                registros = registros[:limite]
            return registros

        query = """
            SELECT * FROM estatus_orden 
            WHERE activo = TRUE 
            ORDER BY orden_secuencial, id_estatus
        """
        params = []
        if limite:
            query += f" LIMIT %s"
            params.append(limite)
        if offset:
            query += f" OFFSET %s"
            params.append(offset)
            
        try:
            from app.dao.conexion import db
            cursor = db.get_cursor()
            cursor.execute(query, params)
            return [self.mapear_a_objeto(fila) for fila in cursor.fetchall()]
        except Exception as e:
            raise
    
    def buscar_por_nombre(self, nombre):
        from app.config import Config
        if Config.DEMO_MODE:
            texto = (nombre or '').lower()
            return [
                fila for fila in self.listar_todos()
                if texto in (fila.nombre_estatus or '').lower()
            ]

        query = """
            SELECT * FROM estatus_orden 
            WHERE nombre_estatus ILIKE %s AND activo = TRUE
        """
        try:
            from app.dao.conexion import db
            cursor = db.get_cursor()
            cursor.execute(query, (f'%{nombre}%',))
            return [self.mapear_a_objeto(fila) for fila in cursor.fetchall()]
        except Exception as e:
            raise
    
    def obtener_siguiente_estatus(self, orden_secuencial_actual):
        """Obtiene el siguiente estatus en el flujo de trabajo"""
        from app.config import Config
        if Config.DEMO_MODE:
            for fila in self.listar_todos():
                if fila.orden_secuencial > orden_secuencial_actual:
                    return fila
            return None

        query = """
            SELECT * FROM estatus_orden 
            WHERE orden_secuencial > %s AND activo = TRUE
            ORDER BY orden_secuencial
            LIMIT 1
        """
        try:
            from app.dao.conexion import db
            cursor = db.get_cursor()
            cursor.execute(query, (orden_secuencial_actual,))
            fila = cursor.fetchone()
            return self.mapear_a_objeto(fila) if fila else None
        except Exception as e:
            raise

estatus_orden_dao = EstatusOrdenDAO()