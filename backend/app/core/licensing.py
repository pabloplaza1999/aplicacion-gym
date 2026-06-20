"""Platform licensing constants — plan catalog, module registry, and dependencies.

Catalog is defined in code (not in DB) because every new module requires a code deploy.
The database stores per-gym state (active/inactive, source). See Paso 3 ADR.
"""

MODULE_REGISTRY: dict[str, dict] = {
    "MODULE_NOTIFICATIONS":     {"name": "Comunicación Automatizada", "settings_key": "module_notifications"},
    "MODULE_BODY_TRACKING":     {"name": "Seguimiento Corporal",       "settings_key": "module_body_tracking"},
    "MODULE_STORE":             {"name": "Tienda",                     "settings_key": "module_store"},
    "MODULE_ANALYTICS":         {"name": "Analítica Avanzada",         "settings_key": None},
    "MODULE_PAYMENTS_ONLINE":   {"name": "Cobros Online",              "settings_key": None},
    "MODULE_DIGITAL_ECOSYSTEM": {"name": "Ecosistema Digital",         "settings_key": None},
    "MODULE_ACCESS_CONTROL":    {"name": "Control de Acceso SW",       "settings_key": None},
    "MODULE_MOBILE_APP":        {"name": "Aplicación Móvil",           "settings_key": None},
    "MODULE_AI":                {"name": "IA Predictiva",              "settings_key": None},
}

# Modules included by each commercial plan (defines source='plan' vs source='addon').
# A module not in the plan can still be active as an individual addon.
PLAN_MODULES: dict[str, list[str]] = {
    "starter":      [],
    "professional": ["MODULE_STORE", "MODULE_NOTIFICATIONS", "MODULE_BODY_TRACKING", "MODULE_ANALYTICS"],
    "premium":      list(MODULE_REGISTRY.keys()),
}

# Hard dependencies: activating the key requires all listed values to be active first.
# Enforced at service layer; informational for UI.
MODULE_DEPENDENCIES: dict[str, list[str]] = {
    "MODULE_AI":         ["MODULE_ANALYTICS"],
    "MODULE_MOBILE_APP": ["MODULE_PAYMENTS_ONLINE"],
}
