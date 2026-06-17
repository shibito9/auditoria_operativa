# -*- coding: utf-8 -*-
"""
Modelo de Producto de Factura - Sistema de Auditoría Operativa
"""
from dataclasses import dataclass
from typing import Optional, Any


@dataclass
class ProductoFactura:
    """Modelo que representa un producto asociado a una factura"""
    
    # Identificación
    numero_producto: str
    secuencia_factura: str  # Referencia a la factura padre
    
    # Información del producto
    familia: str = ""
    calidad: str = ""
    descripcion: str = ""
    tipo_articulo: str = ""
    
    # Valores
    peso_estimado: Optional[float] = None
    peso_total: Optional[float] = None
    valor_compra: Optional[float] = None
    
    # Metadatos
    fila_origen: int = 0
    
    def to_dict(self) -> dict:
        """Convierte el producto a un diccionario para serialización"""
        return {
            "numero_producto": self.numero_producto,
            "secuencia_factura": self.secuencia_factura,
            "familia": self.familia,
            "calidad": self.calidad,
            "descripcion": self.descripcion,
            "tipo_articulo": self.tipo_articulo,
            "peso_estimado": self.peso_estimado,
            "peso_total": self.peso_total,
            "valor_compra": self.valor_compra,
        }
    
    def __str__(self) -> str:
        return f"Producto {self.numero_producto} - {self.descripcion} - {self.peso_total or 0}g"
