# app/dao/orden_servicio_dao.py
"""
DAO para la entidad OrdenServicio
"""
from app.dao.base_dao import BaseDAO
from app.models.orden_servicio import OrdenServicio

class OrdenServicioDAO(BaseDAO):
    @property
    def tabla(self):
        return "orden_servicio"
    
    @property
    def primary_key(self):
        return "id_orden_servicio"
    
    def mapear_a_objeto(self, fila):
        if fila is None:
            return None
        return OrdenServicio(
            id_orden_servicio=fila.get('id_orden_servicio'),
            id_cliente=fila.get('id_cliente'),
            id_equipo=fila.get('id_equipo'),
            id_tecnico=fila.get('id_tecnico'),
            id_servicio=fila.get('id_servicio'),
            id_tipo_orden=fila.get('id_tipo_orden'),
            id_prioridad=fila.get('id_prioridad'),
            id_estatus=fila.get('id_estatus'),
            descripcion_problema=fila.get('descripcion_problema'),
            diagnostico_tecnico=fila.get('diagnostico_tecnico'),
            solucion_problema=fila.get('solucion_problema'),
            fecha_creacion=fila.get('fecha_creacion'),
            fecha_cierre=fila.get('fecha_cierre'),
            activo=fila.get('activo'),
            # Campos de joins
            nombre_cliente=fila.get('nombre_cliente'),
            apellido_cliente=fila.get('apellido_cliente'),
            marca_equipo=fila.get('marca_equipo'),
            modelo_equipo=fila.get('modelo_equipo'),
            nombre_tecnico=fila.get('nombre_tecnico'),
            apellido_tecnico=fila.get('apellido_tecnico'),
            nombre_servicio=fila.get('nombre_servicio'),
            nombre_estatus=fila.get('nombre_estatus'),
            email_cliente=fila.get('email_cliente'),
            especialidad_tecnico=fila.get('especialidad_tecnico'),
            nombre_tipo_orden=fila.get('nombre_tipo_orden'),
            nombre_prioridad=fila.get('nombre_prioridad'),
            nivel_prioridad=fila.get('nivel_prioridad'),
            color_prioridad=fila.get('color_prioridad'),
            color_estatus=fila.get('color_estatus')
        )

    def _consulta_con_joins(self, condicion="", orden=""):
        """Construye la consulta común para listar y consultar órdenes."""
        return f"""
            SELECT
                os.*,
                c.nombre AS nombre_cliente, c.apellido AS apellido_cliente,
                c.email AS email_cliente,
                eq.marca AS marca_equipo, eq.modelo AS modelo_equipo,
                t.nombre AS nombre_tecnico, t.apellido AS apellido_tecnico,
                t.especialidad AS especialidad_tecnico,
                s.nombre_servicio,
                tor.nombre_tipo AS nombre_tipo_orden,
                p.nombre_prioridad, p.nivel AS nivel_prioridad,
                p.color_hex AS color_prioridad,
                eo.nombre_estatus, eo.color_hex AS color_estatus
            FROM orden_servicio os
            LEFT JOIN cliente c ON os.id_cliente = c.id_cliente
            LEFT JOIN equipo eq ON os.id_equipo = eq.id_equipo
            LEFT JOIN tecnico t ON os.id_tecnico = t.id_tecnico
            LEFT JOIN servicio s ON os.id_servicio = s.id_servicio
            LEFT JOIN tipo_orden tor ON os.id_tipo_orden = tor.id_tipo_orden
            LEFT JOIN prioridad p ON os.id_prioridad = p.id_prioridad
            LEFT JOIN estatus_orden eo ON os.id_estatus = eo.id_estatus
            WHERE os.activo = TRUE {condicion}
            {orden}
        """

    def listar_todos(self, limite=None, offset=None):
        """Sobrescribe para incluir nombres de entidades relacionadas (JOIN)"""
        from app.config import Config
        if Config.DEMO_MODE:
            registros = [
                self.mapear_a_objeto(fila) for fila in self._demo_table()
                if fila.get('activo', True)
            ]
            registros = sorted(registros, key=lambda fila: fila.id_orden_servicio, reverse=True)
            if offset:
                registros = registros[offset:]
            if limite is not None:
                registros = registros[:limite]
            return registros

        query = self._consulta_con_joins(orden="ORDER BY os.id_orden_servicio DESC")
        params = []
        if limite:
            query += " LIMIT %s"
            params.append(limite)
        if offset:
            query += " OFFSET %s"
            params.append(offset)
            
        try:
            from app.dao.conexion import db
            cursor = db.get_cursor()
            cursor.execute(query, params)
            return [self.mapear_a_objeto(fila) for fila in cursor.fetchall()]
        except Exception as e:
            raise

    def buscar_por_id_con_joins(self, id_valor):
        """Busca una orden por ID con todos los datos de las relaciones."""
        from app.config import Config
        if Config.DEMO_MODE:
            fila = next((r for r in self._demo_table() if r.get('id_orden_servicio') == id_valor and r.get('activo', True)), None)
            return self.mapear_a_objeto(fila) if fila else None

        query = self._consulta_con_joins("AND os.id_orden_servicio = %s")
        try:
            from app.dao.conexion import db
            cursor = db.get_cursor()
            cursor.execute(query, (id_valor,))
            fila = cursor.fetchone()
            return self.mapear_a_objeto(fila) if fila else None
        except Exception as e:
            raise

    def buscar_por_id(self, id_valor):
        """Consulta una orden con sus relaciones para todas las vistas."""
        return self.buscar_por_id_con_joins(id_valor)


orden_servicio_dao = OrdenServicioDAO()
