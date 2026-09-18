# app/models/orden_servicio.py
from dataclasses import dataclass, asdict
from typing import Optional
from datetime import datetime

@dataclass
class OrdenServicio:
    """Representa una orden y los datos relacionados usados por las vistas."""
    id_orden_servicio: Optional[int] = None
    id_cliente: Optional[int] = None
    id_equipo: Optional[int] = None
    id_tecnico: Optional[int] = None
    id_servicio: Optional[int] = None
    id_tipo_orden: Optional[int] = None
    id_prioridad: Optional[int] = None
    id_estatus: Optional[int] = None
    descripcion_problema: Optional[str] = None
    diagnostico_tecnico: Optional[str] = None
    solucion_problema: Optional[str] = None
    fecha_creacion: Optional[datetime] = None
    fecha_cierre: Optional[datetime] = None
    activo: bool = True

    # Campos de joins para vistas
    nombre_cliente: Optional[str] = None
    apellido_cliente: Optional[str] = None
    marca_equipo: Optional[str] = None
    modelo_equipo: Optional[str] = None
    nombre_tecnico: Optional[str] = None
    apellido_tecnico: Optional[str] = None
    nombre_servicio: Optional[str] = None
    nombre_tipo_orden: Optional[str] = None
    nombre_prioridad: Optional[str] = None
    nivel_prioridad: Optional[int] = None
    color_prioridad: Optional[str] = None
    nombre_estatus: Optional[str] = None
    color_estatus: Optional[str] = None
    email_cliente: Optional[str] = None
    especialidad_tecnico: Optional[str] = None


    def to_dict(self):
        return asdict(self)

    def validar(self):
        referencias_requeridas = {
            'cliente': self.id_cliente,
            'equipo': self.id_equipo,
            'técnico': self.id_tecnico,
            'servicio': self.id_servicio,
            'tipo de orden': self.id_tipo_orden,
            'prioridad': self.id_prioridad,
            'estatus': self.id_estatus,
        }
        for nombre, valor in referencias_requeridas.items():
            if not isinstance(valor, int) or valor <= 0:
                return False, f"El {nombre} es requerido y debe ser válido"

        if not self.descripcion_problema or len(self.descripcion_problema.strip()) < 10:
            return False, "La descripción del problema debe tener al menos 10 caracteres"

        if self.fecha_cierre and self.fecha_creacion and self.fecha_cierre < self.fecha_creacion:
            return False, "La fecha de cierre no puede ser anterior a la fecha de creación"

        return True, ""
