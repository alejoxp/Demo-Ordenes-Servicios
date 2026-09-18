# app/services/orden_servicio_service.py
"""
Servicio de Lógica de Negocio para OrdenServicio
"""
from app.services.base_service import BaseService
from app.dao.orden_servicio_dao import orden_servicio_dao
from app.dao.cliente_dao import cliente_dao
from app.dao.equipo_dao import equipo_dao
from app.dao.tecnico_dao import tecnico_dao
from app.dao.servicio_dao import servicio_dao
from app.dao.tipo_orden_dao import tipo_orden_dao
from app.dao.prioridad_dao import prioridad_dao
from app.dao.estatus_orden_dao import estatus_orden_dao
from app.models.orden_servicio import OrdenServicio

class OrdenServicioService(BaseService):
    def __init__(self):
        super().__init__(orden_servicio_dao)
    
    def validar_datos(self, datos, es_creacion=True):
        datos_normalizados = self._normalizar_datos(datos)
        orden = OrdenServicio(**datos_normalizados)
        valido, mensaje = orden.validar()
        if not valido:
            return valido, mensaje
        return self._validar_referencias(orden)

    @staticmethod
    def _normalizar_datos(datos):
        datos = datos.copy()
        for campo in ('descripcion_problema', 'diagnostico_tecnico', 'solucion_problema'):
            valor = datos.get(campo)
            datos[campo] = valor.strip() if isinstance(valor, str) else valor
        return datos

    def crear(self, datos):
        return super().crear(self._normalizar_datos(datos))

    def actualizar(self, id_valor, datos):
        return super().actualizar(id_valor, self._normalizar_datos(datos))

    @staticmethod
    def _validar_referencias(orden):
        referencias = (
            ('cliente', cliente_dao, orden.id_cliente),
            ('técnico', tecnico_dao, orden.id_tecnico),
            ('servicio', servicio_dao, orden.id_servicio),
            ('tipo de orden', tipo_orden_dao, orden.id_tipo_orden),
            ('prioridad', prioridad_dao, orden.id_prioridad),
            ('estatus', estatus_orden_dao, orden.id_estatus),
        )
        for nombre, dao, referencia in referencias:
            if not dao.buscar_por_id(referencia):
                return False, f"El {nombre} seleccionado no existe o está inactivo"

        equipo = equipo_dao.buscar_por_id(orden.id_equipo)
        if not equipo:
            return False, "El equipo seleccionado no existe o está inactivo"
        if equipo.id_cliente != orden.id_cliente:
            return False, "El equipo seleccionado no pertenece al cliente indicado"

        return True, ""

    def _verificar_dependencias(self, id_valor):
        orden = self.dao.buscar_por_id(id_valor)
        if not orden:
            return "La orden de servicio no existe"
        return None

    # No se implementa _verificar_duplicados ya que no hay un criterio obvio de unicidad
    # más allá del ID autogenerado.

    # No se implementa _verificar_dependencias porque una orden de servicio
    # es una entidad de alto nivel y no se espera que otras entidades dependan de ella
    # para su eliminación.

orden_servicio_service = OrdenServicioService()
