# app/controllers/orden_servicio_controller.py
"""
Controlador para la entidad OrdenServicio
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.services.orden_servicio_service import orden_servicio_service
from app.services.cliente_service import cliente_service
from app.services.equipo_service import equipo_service
from app.services.tecnico_service import tecnico_service
from app.services.servicio_service import servicio_service
from app.services.tipo_orden_service import tipo_orden_service
from app.services.prioridad_service import prioridad_service
from app.services.estatus_orden_service import estatus_orden_service

orden_servicio_bp = Blueprint('orden_servicio', __name__)

def _get_contexto_formulario():
    """Helper para obtener todos los datos necesarios para los dropdowns del formulario."""
    contexto = {
        'clientes': cliente_service.listar()['data'],
        'equipos': equipo_service.listar()['data'],
        'tecnicos': tecnico_service.listar()['data'],
        'servicios': servicio_service.listar()['data'],
        'tipos_orden': tipo_orden_service.listar()['data'],
        'prioridades': prioridad_service.listar()['data'],
        'estatus_orden': estatus_orden_service.listar()['data']
    }
    return contexto

@orden_servicio_bp.route('/')
def listar_ordenes():
    resultado = orden_servicio_service.listar()
    if resultado['exito']:
        # Aquí sería ideal enriquecer cada orden con los nombres en vez de solo IDs
        return render_template('orden_servicio/listar.html', ordenes=resultado['data'])
    flash(resultado['mensaje'], 'error')
    return render_template('orden_servicio/listar.html', ordenes=[])

@orden_servicio_bp.route('/nuevo', methods=['GET', 'POST'])
def crear_orden():
    if request.method == 'POST':
        datos = {
            'id_cliente': request.form.get('id_cliente', type=int),
            'id_equipo': request.form.get('id_equipo', type=int),
            'id_tecnico': request.form.get('id_tecnico', type=int),
            'id_servicio': request.form.get('id_servicio', type=int),
            'id_tipo_orden': request.form.get('id_tipo_orden', type=int),
            'id_prioridad': request.form.get('id_prioridad', type=int),
            'id_estatus': request.form.get('id_estatus', type=int),
            'descripcion_problema': request.form.get('descripcion_problema')
        }
        resultado = orden_servicio_service.crear(datos)
        if resultado['exito']:
            flash('Orden de servicio creada exitosamente', 'success')
            return redirect(url_for('orden_servicio.listar_ordenes'))
        else:
            flash(resultado['mensaje'], 'error')
    
    contexto = _get_contexto_formulario()
    return render_template('orden_servicio/crear.html', **contexto)

@orden_servicio_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
def editar_orden(id):
    if request.method == 'POST':
        datos = {
            'id_cliente': request.form.get('id_cliente', type=int),
            'id_equipo': request.form.get('id_equipo', type=int),
            'id_tecnico': request.form.get('id_tecnico', type=int),
            'id_servicio': request.form.get('id_servicio', type=int),
            'id_tipo_orden': request.form.get('id_tipo_orden', type=int),
            'id_prioridad': request.form.get('id_prioridad', type=int),
            'id_estatus': request.form.get('id_estatus', type=int),
            'descripcion_problema': request.form.get('descripcion_problema'),
            'diagnostico_tecnico': request.form.get('diagnostico_tecnico'),
            'solucion_problema': request.form.get('solucion_problema')
        }
        resultado = orden_servicio_service.actualizar(id, datos)
        if resultado['exito']:
            flash('Orden de servicio actualizada exitosamente', 'success')
            return redirect(url_for('orden_servicio.listar_ordenes'))
        else:
            flash(resultado['mensaje'], 'error')

    resultado_orden = orden_servicio_service.consultar(id)
    if not resultado_orden['exito']:
        flash(resultado_orden['mensaje'], 'error')
        return redirect(url_for('orden_servicio.listar_ordenes'))

    contexto = _get_contexto_formulario()
    contexto['orden'] = resultado_orden['data']
    return render_template('orden_servicio/editar.html', **contexto)

@orden_servicio_bp.route('/<int:id>')
def ver_orden(id):
    resultado = orden_servicio_service.consultar(id)
    if resultado['exito']:
        return render_template('orden_servicio/ver.html', orden=resultado['data'])
    flash(resultado['mensaje'], 'error')
    return redirect(url_for('orden_servicio.listar_ordenes'))


@orden_servicio_bp.route('/<int:id>/eliminar', methods=['POST'])
def eliminar_orden(id):
    resultado = orden_servicio_service.eliminar(id)
    if resultado['exito']:
        flash('Orden de servicio eliminada exitosamente', 'success')
    else:
        flash(resultado['mensaje'], 'error')
    return redirect(url_for('orden_servicio.listar_ordenes'))
