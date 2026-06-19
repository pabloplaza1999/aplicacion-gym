"""Módulos Premium de Gym Platform.

Convención para cada módulo nuevo:
1. Declarar su feature flag en app/core/config.py con default=False (opt-in).
2. Registrar su router condicionalmente en app/main.py.
3. Exponer su estado en GET /api/config/features (routes/config.py).
"""
