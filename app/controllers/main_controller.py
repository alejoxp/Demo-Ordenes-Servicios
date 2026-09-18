# app/controllers/main_controller.py
"""
Controlador principal - Dashboard
"""
from flask import Blueprint, render_template, redirect, url_for, flash
from app.demo_store import demo_store

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Página principal con dashboard"""
    return render_template('index.html')

@main_bp.route('/reset-demo', methods=['POST'])
def reset_demo():
    """Reinicia todos los datos del modo demo."""
    demo_store.reset()
    flash('La demo ha sido reiniciada correctamente.', 'success')
    return redirect(url_for('main.index'))