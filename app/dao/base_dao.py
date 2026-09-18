# app/dao/base_dao.py - VERSIÓN CORREGIDA
"""
Clase base abstracta para todos los DAOs.
Implementa operaciones CRUD genéricas.
"""
from abc import ABC, abstractmethod
from copy import deepcopy
from app.dao.conexion import db
from app.demo_store import demo_store
import logging

logger = logging.getLogger(__name__)

class BaseDAO(ABC):
    """
    Clase base para todos los DAOs del sistema.
    Define la interfaz común CRUD.
    """

    @staticmethod
    def _modo_demo():
        from app.config import Config
        return getattr(Config, 'DEMO_MODE', True)

    @property
    @abstractmethod
    def tabla(self):
        """Nombre de la tabla en la base de datos"""
        pass

    @property
    @abstractmethod
    def primary_key(self):
        """Nombre de la columna clave primaria"""
        pass

    @abstractmethod
    def mapear_a_objeto(self, fila):
        """Convierte una fila de BD a objeto modelo"""
        pass

    def _demo_table(self):
        return demo_store.get_table(self.tabla)

    def _ejecutar_query(self, query, params=None, fetch=False, fetch_one=False):
        """Método helper para ejecutar queries con manejo de transacciones."""
        if self._modo_demo():
            return None
        cursor = None
        try:
            cursor = db.get_cursor()
            cursor.execute(query, params or ())

            if fetch_one:
                resultado = cursor.fetchone()
                return resultado
            elif fetch:
                resultado = cursor.fetchall()
                return resultado
            else:
                db.commit()
                return cursor.rowcount

        except Exception as e:
            logger.error(f" Error en query: {e}")
            logger.error(f"   Query: {query}")
            logger.error(f"   Params: {params}")
            db.rollback()
            raise
        finally:
            if cursor:
                cursor.close()

    def insertar(self, datos: dict) -> int:
        """Inserta un nuevo registro en la tabla."""
        if self._modo_demo():
            table = self._demo_table()
            registro = deepcopy(dict(datos))
            pk = self.primary_key
            if pk not in registro or registro[pk] is None:
                registro[pk] = demo_store.next_id(self.tabla)
            if 'activo' not in registro:
                registro['activo'] = True
            table.append(registro)
            logger.info(f" Insertado en {self.tabla}: ID {registro[pk]}")
            return registro[pk]

        columnas = list(datos.keys())
        valores = list(datos.values())
        placeholders = ', '.join(['%s'] * len(valores))
        cols_str = ', '.join(columnas)

        query = f"""
            INSERT INTO {self.tabla} ({cols_str})
            VALUES ({placeholders})
            RETURNING {self.primary_key}
        """

        try:
            cursor = db.get_cursor()
            cursor.execute(query, valores)
            id_generado = cursor.fetchone()[self.primary_key]
            db.commit()
            logger.info(f" Insertado en {self.tabla}: ID {id_generado}")
            return id_generado
        except Exception as e:
            db.rollback()
            logger.error(f" Error insertando en {self.tabla}: {e}")
            raise

    def buscar_por_id(self, id_valor):
        """Busca un registro por su ID"""
        if self._modo_demo():
            fila = next((r for r in self._demo_table() if r.get(self.primary_key) == id_valor and r.get('activo', True)), None)
            return self.mapear_a_objeto(deepcopy(fila)) if fila else None

        query = f"SELECT * FROM {self.tabla} WHERE {self.primary_key} = %s AND activo = TRUE"

        try:
            cursor = db.get_cursor()
            cursor.execute(query, (id_valor,))
            fila = cursor.fetchone()
            return self.mapear_a_objeto(fila) if fila else None
        except Exception as e:
            logger.error(f" Error buscando en {self.tabla}: {e}")
            raise

    def listar_todos(self, limite=None, offset=None):
        """Lista todos los registros activos con paginación opcional"""
        if self._modo_demo():
            registros = [deepcopy(r) for r in self._demo_table() if r.get('activo', True)]
            if offset:
                registros = registros[offset:]
            if limite is not None:
                registros = registros[:limite]
            return [self.mapear_a_objeto(f) for f in registros]

        query = f"SELECT * FROM {self.tabla} WHERE activo = TRUE ORDER BY {self.primary_key}"
        params = []

        if limite:
            query += f" LIMIT %s"
            params.append(limite)
        if offset:
            query += f" OFFSET %s"
            params.append(offset)

        try:
            cursor = db.get_cursor()
            cursor.execute(query, params)
            return [self.mapear_a_objeto(fila) for fila in cursor.fetchall()]
        except Exception as e:
            logger.error(f" Error listando {self.tabla}: {e}")
            raise

    def buscar_por_criterio(self, columna, valor):
        """Búsqueda genérica por cualquier columna"""
        if self._modo_demo():
            registros = [deepcopy(r) for r in self._demo_table() if r.get('activo', True) and r.get(columna) == valor]
            return [self.mapear_a_objeto(f) for f in registros]

        query = f"SELECT * FROM {self.tabla} WHERE {columna} = %s AND activo = TRUE"

        try:
            cursor = db.get_cursor()
            cursor.execute(query, (valor,))
            return [self.mapear_a_objeto(fila) for fila in cursor.fetchall()]
        except Exception as e:
            logger.error(f" Error buscando en {self.tabla}: {e}")
            raise

    def actualizar(self, id_valor, datos: dict):
        """Actualiza un registro existente."""
        if not datos:
            return False

        if self._modo_demo():
            for index, fila in enumerate(self._demo_table()):
                if fila.get(self.primary_key) == id_valor and fila.get('activo', True):
                    self._demo_table()[index].update(datos)
                    return True
            return False

        campos = [f"{k} = %s" for k in datos.keys()]
        valores = list(datos.values())
        valores.append(id_valor)

        query = f"""
            UPDATE {self.tabla}
            SET {', '.join(campos)}
            WHERE {self.primary_key} = %s AND activo = TRUE
        """

        try:
            cursor = db.get_cursor()
            cursor.execute(query, valores)
            db.commit()
            actualizado = cursor.rowcount > 0
            if actualizado:
                logger.info(f" Actualizado {self.tabla} ID {id_valor}")
            return actualizado
        except Exception as e:
            db.rollback()
            logger.error(f" Error actualizando {self.tabla}: {e}")
            raise

    def eliminar_logico(self, id_valor):
        """Eliminación lógica (cambia activo a FALSE)"""
        if self._modo_demo():
            for fila in self._demo_table():
                if fila.get(self.primary_key) == id_valor:
                    fila['activo'] = False
                    return True
            return False

        query = f"""
            UPDATE {self.tabla}
            SET activo = FALSE
            WHERE {self.primary_key} = %s
        """

        try:
            cursor = db.get_cursor()
            cursor.execute(query, (id_valor,))
            db.commit()
            eliminado = cursor.rowcount > 0
            if eliminado:
                logger.info(f" Eliminado  {self.tabla} ID {id_valor}")
            return eliminado
        except Exception as e:
            db.rollback()
            logger.error(f" Error eliminando {self.tabla}: {e}")
            raise

    def eliminar_fisico(self, id_valor):
        """Eliminación física permanente (USAR CON PRECAUCIÓN)"""
        if self._modo_demo():
            table = self._demo_table()
            original_len = len(table)
            table[:] = [r for r in table if r.get(self.primary_key) != id_valor]
            return len(table) != original_len

        query = f"DELETE FROM {self.tabla} WHERE {self.primary_key} = %s"

        try:
            cursor = db.get_cursor()
            cursor.execute(query, (id_valor,))
            db.commit()
            return cursor.rowcount > 0
        except Exception as e:
            db.rollback()
            logger.error(f" Error eliminando físico {self.tabla}: {e}")
            raise