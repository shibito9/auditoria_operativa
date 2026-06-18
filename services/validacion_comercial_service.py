# -*- coding: utf-8 -*-
"""
Servicio de Validación Comercial - Sistema de Auditoría Operativa
"""
from typing import Dict, Any, Optional, Tuple
from datetime import date
from dataclasses import dataclass

from models import Circular, ReglaCircular
from services.circular_service import CircularService


@dataclass
class ResultadoValidacionLinea:
    """Resultado de validación de una línea de factura"""
    estado: str  # CORRECTA, ERROR_DESCUENTO, ERROR_VALOR_VENTA, FUERA_DE_VIGENCIA, EXCLUIDA_POR_CIRCULAR, REQUIERE_OTRA_CIRCULAR, REVISION_MANUAL, SIN_REGLA
    circular_aplicada: Optional[str]
    regla_aplicada: Optional[str]
    categoria_regla: Optional[str]
    observacion: str
    descuento_esperado: Optional[float]
    descuento_real: float


class ValidacionComercialService:
    """Servicio para validación comercial de facturas con circulares"""
    
    # Estados de validación
    ESTADO_CORRECTA = "CORRECTA"
    ESTADO_ERROR_DESCUENTO = "ERROR_DESCUENTO"
    ESTADO_ERROR_VALOR_VENTA = "ERROR_VALOR_VENTA"
    ESTADO_FUERA_DE_VIGENCIA = "FUERA_DE_VIGENCIA"
    ESTADO_EXCLUIDA_POR_CIRCULAR = "EXCLUIDA_POR_CIRCULAR"
    ESTADO_REQUIERE_OTRA_CIRCULAR = "REQUIERE_OTRA_CIRCULAR"
    ESTADO_REVISION_MANUAL = "REVISION_MANUAL"
    ESTADO_SIN_REGLA = "SIN_REGLA"
    
    def __init__(self, circular_service: CircularService):
        """
        Inicializa el servicio de validación comercial
        
        Args:
            circular_service: Servicio de gestión de circulares
        """
        self.circular_service = circular_service
    
    def validar_linea(
        self,
        linea_factura: Dict[str, Any],
        fecha_factura: date,
        tolerancia_descuento: float = 0.0
    ) -> ResultadoValidacionLinea:
        """
        Valida una línea de factura contra las circulares vigentes
        
        Args:
            linea_factura: Diccionario con datos de la línea de factura
            fecha_factura: Fecha de la factura
            tolerancia_descuento: Tolerancia para descuento (porcentaje)
        
        Returns:
            ResultadoValidacionLinea con el resultado de la validación
        """
        # 1. Buscar circular vigente
        circular = self.circular_service.obtener_circular_vigente(fecha_factura)
        
        if not circular:
            return ResultadoValidacionLinea(
                estado=self.ESTADO_SIN_REGLA,
                circular_aplicada=None,
                regla_aplicada=None,
                categoria_regla=None,
                observacion="No hay circular vigente para la fecha de la factura",
                descuento_esperado=None,
                descuento_real=linea_factura.get("Descuento", 0)
            )
        
        # 2. Verificar exclusión
        if self.circular_service.verificar_exclusion(linea_factura, circular):
            return ResultadoValidacionLinea(
                estado=self.ESTADO_EXCLUIDA_POR_CIRCULAR,
                circular_aplicada=circular.codigo,
                regla_aplicada=None,
                categoria_regla=None,
                observacion=f"Producto excluido en circular {circular.codigo}",
                descuento_esperado=None,
                descuento_real=linea_factura.get("Descuento", 0)
            )
        
        # 3. Buscar regla aplicable
        regla = self.circular_service.buscar_regla_para_linea(linea_factura, circular)
        
        if not regla:
            return ResultadoValidacionLinea(
                estado=self.ESTADO_SIN_REGLA,
                circular_aplicada=circular.codigo,
                regla_aplicada=None,
                categoria_regla=None,
                observacion=f"No se encontró regla aplicable en circular {circular.codigo}",
                descuento_esperado=circular.descuento_porcentaje,
                descuento_real=linea_factura.get("Descuento", 0)
            )
        
        # 4. Verificar acción especial
        if regla.accion_especial:
            if regla.accion_especial == "REQUIERE_OTRA_CIRCULAR":
                return ResultadoValidacionLinea(
                    estado=self.ESTADO_REQUIERE_OTRA_CIRCULAR,
                    circular_aplicada=circular.codigo,
                    regla_aplicada=regla.id,
                    categoria_regla=regla.categoria,
                    observacion=f"{regla.categoria}: {regla.observaciones or 'Requiere circular específica'}",
                    descuento_esperado=regla.descuento_porcentaje,
                    descuento_real=linea_factura.get("Descuento", 0)
                )
            elif regla.accion_especial == "REVISION_MANUAL":
                return ResultadoValidacionLinea(
                    estado=self.ESTADO_REVISION_MANUAL,
                    circular_aplicada=circular.codigo,
                    regla_aplicada=regla.id,
                    categoria_regla=regla.categoria,
                    observacion=f"{regla.categoria}: {regla.observaciones or 'Requiere revisión manual'}",
                    descuento_esperado=regla.descuento_porcentaje,
                    descuento_real=linea_factura.get("Descuento", 0)
                )
        
        # 5. Validar descuento
        subtotal = linea_factura.get("Subtotal", 0)
        descuento = linea_factura.get("Descuento", 0)
        
        if subtotal > 0:
            descuento_porcentaje_real = (descuento / subtotal) * 100
        else:
            descuento_porcentaje_real = 0
        
        descuento_esperado = regla.descuento_porcentaje or circular.descuento_porcentaje
        
        if descuento_esperado is not None:
            limite_superior = descuento_esperado + tolerancia_descuento
            if descuento_porcentaje_real > limite_superior:
                return ResultadoValidacionLinea(
                    estado=self.ESTADO_ERROR_DESCUENTO,
                    circular_aplicada=circular.codigo,
                    regla_aplicada=regla.id,
                    categoria_regla=regla.categoria,
                    observacion=f"Descuento {descuento_porcentaje_real:.2f}% excede límite {limite_superior:.2f}% (esperado: {descuento_esperado:.2f}%)",
                    descuento_esperado=descuento_esperado,
                    descuento_real=descuento_porcentaje_real
                )
        
        # 6. Validar valor de venta (si está definido en regla)
        valor_total = linea_factura.get("Valor Total", 0)
        if regla.valor_final is not None and valor_total > 0:
            # Validar con tolerancia del 1%
            tolerancia_valor = regla.valor_final * 0.01
            if abs(valor_total - regla.valor_final) > tolerancia_valor:
                return ResultadoValidacionLinea(
                    estado=self.ESTADO_ERROR_VALOR_VENTA,
                    circular_aplicada=circular.codigo,
                    regla_aplicada=regla.id,
                    categoria_regla=regla.categoria,
                    observacion=f"Valor venta ${valor_total:,.2f} difiere de esperado ${regla.valor_final:,.2f}",
                    descuento_esperado=descuento_esperado,
                    descuento_real=descuento_porcentaje_real
                )
        
        # 7. Validación correcta
        return ResultadoValidacionLinea(
            estado=self.ESTADO_CORRECTA,
            circular_aplicada=circular.codigo,
            regla_aplicada=regla.id,
            categoria_regla=regla.categoria,
            observacion=f"Validación correcta según circular {circular.codigo}",
            descuento_esperado=descuento_esperado,
            descuento_real=descuento_porcentaje_real
        )
    
    def validar_factura(
        self,
        lineas_factura: list,
        fecha_factura: date,
        tolerancia_descuento: float = 0.0
    ) -> Dict[str, Any]:
        """
        Valida todas las líneas de una factura y determina el estado final
        
        Args:
            lineas_factura: Lista de diccionarios con líneas de factura
            fecha_factura: Fecha de la factura
            tolerancia_descuento: Tolerancia para descuento (porcentaje)
        
        Returns:
            Diccionario con resultado de validación de la factura
        """
        if not lineas_factura:
            return {
                "estado": self.ESTADO_SIN_REGLA,
                "observacion": "Factura sin líneas",
                "resultados_lineas": []
            }
        
        # Validar cada línea
        resultados_lineas = []
        for linea in lineas_factura:
            resultado = self.validar_linea(linea, fecha_factura, tolerancia_descuento)
            resultados_lineas.append(resultado)
        
        # Determinar estado final de la factura
        estados = {r.estado for r in resultados_lineas}
        
        # Prioridad de estados (de mayor a menor severidad)
        prioridad_estados = [
            self.ESTADO_ERROR_VALOR_VENTA,
            self.ESTADO_ERROR_DESCUENTO,
            self.ESTADO_FUERA_DE_VIGENCIA,
            self.ESTADO_REQUIERE_OTRA_CIRCULAR,
            self.ESTADO_REVISION_MANUAL,
            self.ESTADO_EXCLUIDA_POR_CIRCULAR,
            self.ESTADO_SIN_REGLA,
            self.ESTADO_CORRECTA
        ]
        
        estado_final = self.ESTADO_CORRECTA
        for estado in prioridad_estados:
            if estado in estados:
                estado_final = estado
                break
        
        # Generar observación consolidada
        observaciones = []
        for resultado in resultados_lineas:
            if resultado.estado != self.ESTADO_CORRECTA:
                obs = f"{resultado.estado}: {resultado.observacion}"
                if obs not in observaciones:
                    observaciones.append(obs)
        
        observacion_final = "; ".join(observaciones[:3])  # Máximo 3 observaciones
        if not observacion_final:
            observacion_final = "Todas las líneas validadas correctamente"
        
        return {
            "estado": estado_final,
            "observacion": observacion_final,
            "resultados_lineas": resultados_lineas,
            "circular_aplicada": resultados_lineas[0].circular_aplicada if resultados_lineas else None
        }
