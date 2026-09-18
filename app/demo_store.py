from __future__ import annotations

from copy import deepcopy
from threading import Lock
from typing import Dict, List


class DemoStore:
    def __init__(self):
        self._lock = Lock()
        self._tables: Dict[str, List[dict]] = {}
        self._counters: Dict[str, int] = {}
        self._seeded = False

    def reset(self):
        with self._lock:
            self._tables.clear()
            self._counters.clear()
            self._seeded = False
            self._seed_default_data()

    def _seed_default_data(self):
        if self._seeded:
            return

        self._tables = {
            'cliente': [
                {
                    'id_cliente': 1,
                    'nombre': 'Cliente',
                    'apellido': 'Demo',
                    'cedula': '11111111',
                    'telefono': '0414-0000000',
                    'email': 'cliente@demo.com',
                    'direccion': 'Dirección demo',
                    'fecha_registro': '2026-01-01T00:00:00',
                    'activo': True,
                }
            ],
            'tecnico': [
                {
                    'id_tecnico': 1,
                    'nombre': 'Técnico',
                    'apellido': 'Demo',
                    'cedula': '22222222',
                    'especialidad': 'Hardware',
                    'telefono': '0414-1111111',
                    'email': 'tecnico@demo.com',
                    'fecha_contratacion': '2026-01-01',
                    'activo': True,
                }
            ],
            'equipo': [
                {
                    'id_equipo': 1,
                    'nombre_equipo': 'Laptop Demo',
                    'tipo': 'Laptop',
                    'marca': 'Dell',
                    'modelo': 'Latitude 5420',
                    'numero_serie': 'SN-DEMO-001',
                    'id_cliente': 1,
                    'fecha_registro': '2026-01-01T00:00:00',
                    'activo': True,
                }
            ],
            'servicio': [
                {
                    'id_servicio': 1,
                    'nombre_servicio': 'Revisión general',
                    'descripcion': 'Diagnóstico y mantenimiento básico.',
                    'costo_base': 120.00,
                    'tiempo_estimado_horas': 3,
                    'activo': True,
                }
            ],
            'tipo_orden': [
                {
                    'id_tipo_orden': 1,
                    'nombre_tipo': 'Reparación',
                    'descripcion': 'Orden de reparación',
                    'requiere_aprobacion': False,
                    'activo': True,
                },
                {
                    'id_tipo_orden': 2,
                    'nombre_tipo': 'Mantenimiento',
                    'descripcion': 'Mantenimiento preventivo',
                    'requiere_aprobacion': False,
                    'activo': True,
                }
            ],
            'estatus_orden': [
                {
                    'id_estatus': 1,
                    'nombre_estatus': 'Recibida',
                    'descripcion': 'Orden recibida',
                    'color_hex': '#6C757D',
                    'orden_secuencial': 1,
                    'activo': True,
                },
                {
                    'id_estatus': 2,
                    'nombre_estatus': 'En Proceso',
                    'descripcion': 'Trabajo en curso',
                    'color_hex': '#FFC107',
                    'orden_secuencial': 2,
                    'activo': True,
                },
                {
                    'id_estatus': 3,
                    'nombre_estatus': 'Completada',
                    'descripcion': 'Trabajo finalizado',
                    'color_hex': '#28A745',
                    'orden_secuencial': 3,
                    'activo': True,
                }
            ],
            'prioridad': [
                {
                    'id_prioridad': 1,
                    'nombre_prioridad': 'Media',
                    'nivel': 2,
                    'tiempo_respuesta_horas': 72,
                    'color_hex': '#FFC107',
                    'activo': True,
                },
                {
                    'id_prioridad': 2,
                    'nombre_prioridad': 'Alta',
                    'nivel': 1,
                    'tiempo_respuesta_horas': 24,
                    'color_hex': '#FD7E14',
                    'activo': True,
                }
            ],
            'orden_servicio': [
                {
                    'id_orden_servicio': 1,
                    'id_cliente': 1,
                    'id_equipo': 1,
                    'id_tecnico': 1,
                    'id_servicio': 1,
                    'id_tipo_orden': 1,
                    'id_prioridad': 1,
                    'id_estatus': 1,
                    'descripcion_problema': 'La laptop tarda mucho en encender.',
                    'diagnostico_tecnico': 'Se recomienda limpieza de sistema.',
                    'solucion_problema': 'Revisión realizada en demo.',
                    'fecha_creacion': '2026-01-01T00:00:00',
                    'fecha_cierre': None,
                    'activo': True,
                }
            ],
        }

        for table_name, rows in self._tables.items():
            max_id = max((row.get(self._pk_for_table(table_name), 0) for row in rows), default=0)
            self._counters[table_name] = max_id

        self._seeded = True

    def _pk_for_table(self, table_name: str) -> str:
        mapping = {
            'cliente': 'id_cliente',
            'tecnico': 'id_tecnico',
            'equipo': 'id_equipo',
            'servicio': 'id_servicio',
            'tipo_orden': 'id_tipo_orden',
            'estatus_orden': 'id_estatus',
            'prioridad': 'id_prioridad',
            'orden_servicio': 'id_orden_servicio',
        }
        return mapping.get(table_name, 'id')

    def get_table(self, table_name: str):
        if not self._seeded:
            self._seed_default_data()
        if table_name not in self._tables:
            self._tables[table_name] = []
            self._counters[table_name] = 0
        return self._tables[table_name]

    def next_id(self, table_name: str):
        if not self._seeded:
            self._seed_default_data()
        self._counters[table_name] = self._counters.get(table_name, 0) + 1
        return self._counters[table_name]

    def snapshot(self):
        return deepcopy(self._tables)


demo_store = DemoStore()
demo_store.reset()
