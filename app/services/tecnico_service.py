# app/services/tecnico_service.py
"""
Servicio de Lógica de Negocio para Técnico
Implementa reglas específicas: validaciones, duplicados, dependencias.
"""
from app.services.base_service import BaseService
from app.dao.tecnico_dao import tecnico_dao
from app.models.tecnico import Tecnico

class TecnicoService(BaseService):
    """
    Servicio de negocio para gestión de técnicos.
    Implementa casos de uso CU-G01 al CU-G05 específicos para técnicos.
    """
    
    def __init__(self):
        super().__init__(tecnico_dao)
    
    def validar_datos(self, datos, es_creacion=True):
        """
        Validaciones de negocio para técnicos.
        """
        # Crear objeto temporal para validar
        tecnico = Tecnico(**datos)
        return tecnico.validar()
    
    def _verificar_duplicados(self, datos):
        """
        Verifica duplicados según CU-G01 (inclusión CU-G05).
        La cédula debe ser única.
        """
        cedula = datos.get('cedula')
        if cedula:
            existente = self.dao.buscar_por_cedula(cedula)
            if existente:
                return f"Ya existe un técnico con la cédula {cedula}"
        return None
    
    def _verificar_dependencias(self, id_tecnico):
        """
        Verifica si el técnico tiene órdenes asignadas antes de eliminar.
        (Para cuando implementemos la entidad OrdenServicio)
        """
        # TODO: Verificar en tabla orden_servicio cuando exista
        # Por ahora, permitir eliminación
        return None
    
    # Métodos específicos de negocio
    def listar_por_especialidad(self, especialidad):
        """Caso de uso específico: Listar técnicos por especialidad"""
        try:
            tecnicos = self.dao.buscar_por_especialidad(especialidad)
            return {
                "exito": True,
                "data": [t.to_dict() for t in tecnicos]
            }
        except Exception as e:
            return {"exito": False, "mensaje": str(e)}
    
    def obtener_disponibles(self):
        """Obtiene técnicos disponibles para asignación"""
        # Lógica futura: filtrar por carga de trabajo
        return self.listar()


# Instancia singleton
tecnico_service = TecnicoService()