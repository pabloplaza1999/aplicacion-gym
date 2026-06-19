"""Gym Platform — módulos de la plataforma.

Convención de organización:
- modules/premium/   Módulos Premium activados por feature flags (MODULE_* en .env).
                     Cada módulo nuevo nace aquí directamente.
- El código Core existente permanece en app/api/routes/, app/services/, etc.
  La migración física a modules/core/ ocurrirá cuando haya suficiente masa
  crítica que justifique la reorganización (F5+).
"""
