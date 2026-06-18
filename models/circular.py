# -*- coding: utf-8 -*-
"""
Modelo de Circular - Sistema de Auditoría Operativa
"""
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import date
import json


@dataclass
class Circular:
    """Representa una circular comercial con sus reglas"""
    
    # Identificación
    codigo: str  # Ej: "684-26"
    nombre: str  # Ej: "Circular Junio 2026"
    
    # Vigencia
    fecha_inicio: date
    fecha_fin: date
    
    # Descuento general
    descuento_porcentaje: float  # Ej: 8.0
    
    # Reglas por categoría
    reglas: List['ReglaCircular'] = field(default_factory=list)
    
    # Exclusiones (productos que NO aplican)
    exclusiones: List[str] = field(default_factory=list)  # Ej: ["lingotes", "plan separe"]
    
    # Condiciones especiales
    condiciones_especiales: List[str] = field(default_factory=list)
    
    # Estado
    activa: bool = True
    
    def esta_vigente(self, fecha: date) -> bool:
        """Verifica si la circular está vigente en una fecha"""
        return self.fecha_inicio <= fecha <= self.fecha_fin and self.activa
    
    def to_dict(self) -> dict:
        """Convierte la circular a un diccionario para serialización"""
        return {
            "codigo": self.codigo,
            "nombre": self.nombre,
            "fecha_inicio": self.fecha_inicio.isoformat(),
            "fecha_fin": self.fecha_fin.isoformat(),
            "descuento_porcentaje": self.descuento_porcentaje,
            "reglas": [regla.to_dict() for regla in self.reglas],
            "exclusiones": self.exclusiones,
            "condiciones_especiales": self.condiciones_especiales,
            "activa": self.activa
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Circular':
        """Crea una Circular desde un diccionario"""
        from models.regla_circular import ReglaCircular
        
        return cls(
            codigo=data["codigo"],
            nombre=data["nombre"],
            fecha_inicio=date.fromisoformat(data["fecha_inicio"]),
            fecha_fin=date.fromisoformat(data["fecha_fin"]),
            descuento_porcentaje=data["descuento_porcentaje"],
            reglas=[ReglaCircular.from_dict(r) for r in data.get("reglas", [])],
            exclusiones=data.get("exclusiones", []),
            condiciones_especiales=data.get("condiciones_especiales", []),
            activa=data.get("activa", True)
        )
    
    def __str__(self) -> str:
        return f"Circular {self.codigo} - {self.nombre} ({self.fecha_inicio} a {self.fecha_fin})"


# Import al final para evitar circular dependency
from models.regla_circular import ReglaCircular
