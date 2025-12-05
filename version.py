"""
Versión de la aplicación Punto de Venta
Formato: Semantic Versioning (MAJOR.MINOR.PATCH)
"""

VERSION = "1.0.7"

def get_version():
    """Retorna la versión actual de la aplicación"""
    return VERSION

def parse_version(version_string):
    """
    Parsea una cadena de versión en un tuple (major, minor, patch)
    
    Args:
        version_string: String en formato "X.Y.Z"
    
    Returns:
        tuple: (major, minor, patch) como enteros
    """
    try:
        parts = version_string.split('.')
        if len(parts) != 3:
            raise ValueError("Formato de versión inválido")
        return tuple(int(p) for p in parts)
    except (ValueError, AttributeError):
        raise ValueError(f"Formato de versión inválido: {version_string}")

def compare_versions(version1, version2):
    """
    Compara dos versiones
    
    Args:
        version1: String de versión "X.Y.Z"
        version2: String de versión "X.Y.Z"
    
    Returns:
        int: 1 si version1 > version2, -1 si version1 < version2, 0 si son iguales
    """
    v1 = parse_version(version1)
    v2 = parse_version(version2)
    
    if v1 > v2:
        return 1
    elif v1 < v2:
        return -1
    else:
        return 0

def is_newer_version(candidate, current):
    """
    Verifica si la versión candidata es más nueva que la actual
    
    Args:
        candidate: String de versión candidata
        current: String de versión actual
    
    Returns:
        bool: True si candidate > current
    """
    return compare_versions(candidate, current) > 0
