# -*- coding: utf-8 -*-
"""
Modelo de Regla Circular - Sistema de Auditoría Operativa
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class ReglaCircular:
    """Regla comercial para una categoría específica"""
    
    # Identificación
    id: str
    categoria: str  # Ej: "Joyeria importada"
    
    # Valores permitidos
    precio_full: Optional[float] = None
    valor_antes_iva: Optional[float] = None
    iva: Optional[float] = None
    valor_final: Optional[float] = None
    descuento_porcentaje: Optional[float] = None
    
    # Criterios de mapeo
    criterios_procedencia: List[str] = field(default_factory=list)  # IMPORTADO, NACIONAL, MAQUILA, etc.
    criterios_categoria: List[str] = field(default_factory=list)  # Nombres exactos de categoría
    criterios_descripcion: List[str] = field(default_factory=list)  # Patrones en descripción
    criterios_linea: List[str] = field(default_factory=list)  # Nombres de línea
    criterios_peso: Optional[Dict[str, float]] = None  # {"min": 0.19, "max": 0.20}
    
    # Acción especial
    accion_especial: Optional[str] = None  # "REQUIERE_OTRA_CIRCULAR", "EXCLUIDA", "REVISION_MANUAL"
    
    # Observaciones
    observaciones: str = ""
    
    def to_dict(self) -> dict:
        """Convierte la regla a un diccionario para serialización"""
        return {
            "id": self.id,
            "categoria": self.categoria,
            "precio_full": self.precio_full,
            "valor_antes_iva": self.valor_antes_iva,
            "iva": self.iva,
            "valor_final": self.valor_final,
            "descuento_porcentaje": self.descuento_porcentaje,
            "criterios_procedencia": self.criterios_procedencia,
            "criterios_categoria": self.criterios_categoria,
            "criterios_descripcion": self.criterios_descripcion,
            "criterios_linea": self.criterios_linea,
            "criterios_peso": self.criterios_peso,
            "accion_especial": self.accion_especial,
            "observaciones": self.observaciones
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ReglaCircular':
        """Crea una ReglaCircular desde un diccionario"""
        return cls(
            id=data["id"],
            categoria=data["categoria"],
            precio_full=data.get("precio_full"),
            valor_antes_iva=data.get("valor_antes_iva"),
            iva=data.get("iva"),
            valor_final=data.get("valor_final"),
            descuento_porcentaje=data.get("descuento_porcentaje"),
            criterios_procedencia=data.get("criterios_procedencia", []),
            criterios_categoria=data.get("criterios_categoria", []),
            criterios_descripcion=data.get("criterios_descripcion", []),
            criterios_linea=data.get("criterios_linea", []),
            criterios_peso=data.get("criterios_peso"),
            accion_especial=data.get("accion_especial"),
            observaciones=data.get("observaciones", "")
        )
    
    def coincide_procedencia(self, procedencia: str) -> bool:
        """Verifica si la procedencia coincide con algún criterio"""
        return procedencia in self.criterios_procedencia
    
    def coincide_categoria(self, categoria: str) -> bool:
        """Verifica si la categoría coincide con algún criterio"""
        return categoria in self.criterios_categoria
    
    def coincide_descripcion(self, descripcion: str) -> bool:
        """Verifica si la descripción contiene algún patrón"""
        desc_lower = descripcion.lower()
        return any(patron.lower() in desc_lower for patron in self.criterios_descripcion)
    
    def coincide_linea(self, linea: str) -> bool:
        """Verifica si la línea coincide con algún criterio"""
        return linea in self.criterios_linea
    
    def coincide_peso(self, peso: float) -> bool:
        """Verifica si el peso está en el rango especificado"""
        if not self.criterios_peso or peso is None:
            return False
        
        peso_min = self.criterios_peso.get("min")
        peso_max = self.criterios_peso.get("max")
        
        if peso_min is not None and peso_max is not None:
            return peso_min <= peso <= peso_max
        elif peso_min is not None:
            return peso >= peso_min
        elif peso_max is not None:
            return peso <= peso_max
        
        return False
    
    def __str__(self) -> str:
        return f"Regla {self.id} - {self.categoria}"
