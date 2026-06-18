# -*- coding: utf-8 -*-
"""
Modelo de Categoría Circular - Sistema de Auditoría Operativa
"""
from dataclasses import dataclass, field
from typing import List, Optional
from models.regla_circular import ReglaCircular


@dataclass
class CategoriaCircular:
    """Categoría de producto con sus reglas asociadas"""
    
    nombre: str
    descripcion: str
    reglas: List[ReglaCircular] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        """Convierte la categoría a un diccionario para serialización"""
        return {
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "reglas": [regla.to_dict() for regla in self.reglas]
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'CategoriaCircular':
        """Crea una CategoriaCircular desde un diccionario"""
        return cls(
            nombre=data["nombre"],
            descripcion=data["descripcion"],
            reglas=[ReglaCircular.from_dict(r) for r in data.get("reglas", [])]
        )
    
    def __str__(self) -> str:
        return f"Categoría {self.nombre} - {len(self.reglas)} reglas"
