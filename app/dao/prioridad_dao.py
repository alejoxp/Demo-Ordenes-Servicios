# app/dao/prioridad_dao.py
"""
DAO para la entidad Prioridad
"""
from copy import deepcopy

from app.dao.base_dao import BaseDAO
from app.models.prioridad import Prioridad

class PrioridadDAO(BaseDAO):
    @property
    def tabla(self):
        return "prioridad"
    
    @property
    def primary_key(self):
        return "id_prioridad"
    
    def mapear_a_objeto(self, fila):
        if fila is None:
            return None
        return Prioridad(
            id_prioridad=fila.get('id_prioridad'),
            nombre_prioridad=fila.get('nombre_prioridad'),
            nivel=fila.get('nivel'),
            tiempo_respuesta_horas=fila.get('tiempo_respuesta_horas'),
            color_hex=fila.get('color_hex'),
            activo=fila.get('activo')
        )
    
    def listar_todos(self, limite=None, offset=None):
        """Sobrescribe para ordenar por nivel (más crítico primero)"""
        from app.config import Config
        if Config.DEMO_MODE:
            registros = [
                deepcopy(r) for r in self.buscar_por_criterio('activo', True)
            ]
            registros.sort(key=lambda fila: fila.nivel)
            if offset:
                registros = registros[offset:]
            if limite is not None:
                registros = registros[:limite]
            return registros

        query = """
            SELECT * FROM prioridad 
            WHERE activo = TRUE 
            ORDER BY nivel
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
                if texto in (fila.nombre_prioridad or '').lower()
            ]
        return self.buscar_por_criterio('nombre_prioridad', nombre)
    
    def buscar_por_nivel(self, nivel):
        from app.config import Config
        if Config.DEMO_MODE:
            for fila in self.listar_todos():
                if fila.nivel == nivel:
                    return fila
            return None
        resultados = self.buscar_por_criterio('nivel', nivel)
        return resultados[0] if resultados else None
    
    def obtener_para_sla(self, horas_maximas):
        """Obtiene prioridades con SLA menor o igual a las horas especificadas"""
        from app.config import Config
        if Config.DEMO_MODE:
            return [
                fila for fila in self.listar_todos()
                if fila.tiempo_respuesta_horas is not None and fila.tiempo_respuesta_horas <= horas_maximas
            ]

        query = """
            SELECT * FROM prioridad 
            WHERE tiempo_respuesta_horas <= %s AND activo = TRUE
            ORDER BY nivel
        """
        try:
            from app.dao.conexion import db
            cursor = db.get_cursor()
            cursor.execute(query, (horas_maximas,))
            return [self.mapear_a_objeto(fila) for fila in cursor.fetchall()]
        except Exception as e:
            raise

prioridad_dao = PrioridadDAO()