# -*- coding: utf-8 -*-
"""
Modelo de Factura - Sistema de Auditoría Operativa
"""
from dataclasses import dataclass, field
from typing import List, Optional, Any
from datetime import date


@dataclass
class Factura:
    """Modelo que representa una factura con sus productos asociados"""
    
    # Identificación
    secuencia_factura: str
    numero_factura: str
    
    # Información del cliente
    cliente: str = ""
    documento_cliente: str = ""
    
    # Fechas
    fecha_factura: Optional[date] = None
    fecha_operacion: Optional[date] = None
    
    # Valores monetarios (se toman una sola vez por factura)
    subtotal: Optional[float] = None
    descuento: Optional[float] = None
    valor_total: Optional[float] = None
    
    # Valores de peso
    factura_gramos: Optional[float] = None
    
    # Estado de auditoría
    estado_auditoria: str = "PENDIENTE"  # PENDIENTE, CORRECTA, ERROR, REVISION_MANUAL, EXCLUIDA
    tipo_error: str = ""
    observacion: str = ""
    
    # Productos asociados a la factura
    productos: List[Any] = field(default_factory=list)
    
    # Metadatos
    fila_origen: int = 0
    joyeria: str = ""
    ciudad: str = ""
    
    def to_dict(self) -> dict:
        """Convierte la factura a un diccionario para serialización"""
        return {
            "secuencia_factura": self.secuencia_factura,
            "numero_factura": self.numero_factura,
            "cliente": self.cliente,
            "documento_cliente": self.documento_cliente,
            "fecha_factura": self.fecha_factura.isoformat() if self.fecha_factura else "",
            "fecha_operacion": self.fecha_operacion.isoformat() if self.fecha_operacion else "",
            "subtotal": self.subtotal,
            "descuento": self.descuento,
            "valor_total": self.valor_total,
            "factura_gramos": self.factura_gramos,
            "estado_auditoria": self.estado_auditoria,
            "tipo_error": self.tipo_error,
            "observacion": self.observacion,
            "num_productos": len(self.productos),
            "joyeria": self.joyeria,
            "ciudad": self.ciudad,
        }
    
    def __str__(self) -> str:
        return f"Factura {self.secuencia_factura} - {self.cliente} - ${self.valor_total or 0:,.2f}"
