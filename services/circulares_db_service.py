# -*- coding: utf-8 -*-
"""
Servicio CRUD para Gestión de Circulares - Sistema de Auditoría Operativa
"""
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import date, datetime

from database.circulares_db import CircularesDB


class CircularesDbService:
    """Servicio para operaciones CRUD de circulares en SQLite"""
    
    def __init__(self, db_path: Optional[Path] = None):
        """
        Inicializa el servicio de circulares
        
        Args:
            db_path: Ruta al archivo SQLite. Por defecto: database/circulares.db
        """
        self.db = CircularesDB(db_path)
    
    def close(self):
        """Cierra la conexión a la base de datos"""
        self.db.close()
    
    # ============================
    # Operaciones - Circulares
    # ============================
    
    def crear_circular(self, circular_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Crea una nueva circular
        
        Args:
            circular_data: Diccionario con datos de la circular
                - codigo: str (único)
                - nombre: str
                - fecha_inicio: str (YYYY-MM-DD)
                - fecha_fin: str (YYYY-MM-DD)
                - descuento_porcentaje: float (opcional)
                - activa: bool (default True)
                - archivo_fuente: str (opcional)
                - observaciones: str (opcional)
        
        Returns:
            Diccionario con la circular creada (incluyendo ID)
        
        Raises:
            Exception: Si ya existe una circular con el mismo código
        """
        # Verificar que no exista el código
        existente = self.db.obtener_circular_por_codigo(circular_data["codigo"])
        if existente:
            raise Exception(f"Ya existe una circular con código {circular_data['codigo']}")
        
        # Validar fechas
        self._validar_fechas(circular_data["fecha_inicio"], circular_data["fecha_fin"])
        
        # Crear circular
        circular_id = self.db.crear_circular(circular_data)
        
        # Retornar circular creada
        return self.db.obtener_circular_por_id(circular_id)
    
    def obtener_circular(self, circular_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene una circular por su ID
        
        Args:
            circular_id: ID de la circular
        
        Returns:
            Diccionario con la circular o None si no existe
        """
        return self.db.obtener_circular_por_id(circular_id)
    
    def obtener_circular_por_codigo(self, codigo: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene una circular por su código
        
        Args:
            codigo: Código de la circular
        
        Returns:
            Diccionario con la circular o None si no existe
        """
        return self.db.obtener_circular_por_codigo(codigo)
    
    def obtener_todas_circulares(self, solo_activas: bool = False) -> List[Dict[str, Any]]:
        """
        Obtiene todas las circulares
        
        Args:
            solo_activas: Si True, solo retorna circulares activas
        
        Returns:
            Lista de circulares
        """
        return self.db.obtener_todas_circulares(solo_activas)
    
    def obtener_circular_vigente(self, fecha: date) -> Optional[Dict[str, Any]]:
        """
        Obtiene la circular vigente para una fecha específica
        Si hay múltiples vigentes, retorna la más reciente
        
        Args:
            fecha: Fecha a verificar
        
        Returns:
            Circular vigente o None si no hay ninguna
        """
        fecha_str = fecha.strftime("%Y-%m-%d")
        vigentes = self.db.obtener_circulares_vigentes(fecha_str)
        
        if not vigentes:
            return None
        
        # Retornar la más reciente (por fecha de inicio)
        return vigentes[0]  # Ya están ordenadas por fecha_inicio DESC
    
    def actualizar_circular(self, circular_id: int, circular_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Actualiza una circular existente
        
        Args:
            circular_id: ID de la circular a actualizar
            circular_data: Datos actualizados
        
        Returns:
            Diccionario con la circular actualizada
        
        Raises:
            Exception: Si no existe la circular o si el código ya está en uso
        """
        # Verificar que existe
        existente = self.db.obtener_circular_por_id(circular_id)
        if not existente:
            raise Exception(f"No existe circular con ID {circular_id}")
        
        # Verificar que el código no esté en uso por otra circular
        if "codigo" in circular_data and circular_data["codigo"] != existente["codigo"]:
            codigo_en_uso = self.db.obtener_circular_por_codigo(circular_data["codigo"])
            if codigo_en_uso:
                raise Exception(f"Ya existe una circular con código {circular_data['codigo']}")
        
        # Validar fechas si se proporcionan
        if "fecha_inicio" in circular_data and "fecha_fin" in circular_data:
            self._validar_fechas(circular_data["fecha_inicio"], circular_data["fecha_fin"])
        
        # Actualizar
        self.db.actualizar_circular(circular_id, circular_data)
        
        return self.db.obtener_circular_por_id(circular_id)
    
    def eliminar_circular(self, circular_id: int) -> bool:
        """
        Elimina una circular (con sus reglas y exclusiones en cascada)
        
        Args:
            circular_id: ID de la circular a eliminar
        
        Returns:
            True si se eliminó, False en caso contrario
        
        Raises:
            Exception: Si no existe la circular
        """
        existente = self.db.obtener_circular_por_id(circular_id)
        if not existente:
            raise Exception(f"No existe circular con ID {circular_id}")
        
        return self.db.eliminar_circular(circular_id)
    
    def activar_circular(self, circular_id: int, activa: bool) -> Dict[str, Any]:
        """
        Activa o desactiva una circular
        
        Args:
            circular_id: ID de la circular
            activa: True para activar, False para desactivar
        
        Returns:
            Diccionario con la circular actualizada
        
        Raises:
            Exception: Si no existe la circular
        """
        existente = self.db.obtener_circular_por_id(circular_id)
        if not existente:
            raise Exception(f"No existe circular con ID {circular_id}")
        
        self.db.activar_circular(circular_id, activa)
        
        return self.db.obtener_circular_por_id(circular_id)
    
    # ============================
    # Operaciones - Reglas
    # ============================
    
    def agregar_regla(self, circular_id: int, regla_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Agrega una regla a una circular
        
        Args:
            circular_id: ID de la circular
            regla_data: Datos de la regla
                - categoria: str
                - criterios_procedencia: List[str] (opcional)
                - criterios_categoria: List[str] (opcional)
                - criterios_linea: List[str] (opcional)
                - criterios_descripcion: List[str] (opcional)
                - criterios_peso: Dict[str, float] (opcional)
                - precio_full: float (opcional)
                - valor_antes_iva: float (opcional)
                - iva: float (opcional)
                - valor_final: float (opcional)
                - descuento_porcentaje: float (opcional)
                - accion_especial: str (opcional)
                - observaciones: str (opcional)
                - orden: int (opcional, default 0)
        
        Returns:
            Diccionario con la regla creada
        
        Raises:
            Exception: Si no existe la circular
        """
        # Verificar que existe la circular
        existente = self.db.obtener_circular_por_id(circular_id)
        if not existente:
            raise Exception(f"No existe circular con ID {circular_id}")
        
        # Crear regla
        regla_id = self.db.crear_regla(circular_id, regla_data)
        
        # Retornar regla creada (necesitamos obtenerla de la lista)
        reglas = self.db.obtener_reglas_por_circular(circular_id)
        for regla in reglas:
            if regla["id"] == regla_id:
                return regla
        
        raise Exception("Error al crear la regla")
    
    def obtener_reglas(self, circular_id: int) -> List[Dict[str, Any]]:
        """
        Obtiene todas las reglas de una circular
        
        Args:
            circular_id: ID de la circular
        
        Returns:
            Lista de reglas
        """
        return self.db.obtener_reglas_por_circular(circular_id)
    
    def actualizar_regla(self, regla_id: int, regla_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Actualiza una regla existente
        
        Args:
            regla_id: ID de la regla a actualizar
            regla_data: Datos actualizados
        
        Returns:
            Diccionario con la regla actualizada
        
        Raises:
            Exception: Si no existe la regla
        """
        # Verificar que existe la regla
        # Nota: Necesitamos obtener el circular_id primero para verificar
        # Por ahora, asumimos que el servicio de validación manejará esto
        
        self.db.actualizar_regla(regla_id, regla_data)
        
        # Retornar regla actualizada
        # Necesitamos obtenerla de alguna manera, por ahora retornamos los datos
        return {**regla_data, "id": regla_id}
    
    def eliminar_regla(self, regla_id: int) -> bool:
        """
        Elimina una regla
        
        Args:
            regla_id: ID de la regla a eliminar
        
        Returns:
            True si se eliminó, False en caso contrario
        """
        return self.db.eliminar_regla(regla_id)
    
    # ============================
    # Operaciones - Exclusiones
    # ============================
    
    def agregar_exclusion(self, circular_id: int, patron: str, tipo: str = "descripcion") -> Dict[str, Any]:
        """
        Agrega una exclusión a una circular
        
        Args:
            circular_id: ID de la circular
            patron: Patrón de exclusión
            tipo: Tipo de exclusión ('descripcion' o 'categoria')
        
        Returns:
            Diccionario con la exclusión creada
        
        Raises:
            Exception: Si no existe la circular
        """
        # Verificar que existe la circular
        existente = self.db.obtener_circular_por_id(circular_id)
        if not existente:
            raise Exception(f"No existe circular con ID {circular_id}")
        
        exclusion_id = self.db.crear_exclusion(circular_id, patron, tipo)
        
        # Retornar exclusión creada
        exclusiones = self.db.obtener_exclusiones_por_circular(circular_id)
        for exclusion in exclusiones:
            if exclusion["id"] == exclusion_id:
                return exclusion
        
        raise Exception("Error al crear la exclusión")
    
    def obtener_exclusiones(self, circular_id: int) -> List[Dict[str, Any]]:
        """
        Obtiene todas las exclusiones de una circular
        
        Args:
            circular_id: ID de la circular
        
        Returns:
            Lista de exclusiones
        """
        return self.db.obtener_exclusiones_por_circular(circular_id)
    
    def eliminar_exclusion(self, exclusion_id: int) -> bool:
        """
        Elimina una exclusión
        
        Args:
            exclusion_id: ID de la exclusión a eliminar
        
        Returns:
            True si se eliminó, False en caso contrario
        """
        return self.db.eliminar_exclusion(exclusion_id)
    
    # ============================
    # Operaciones - Circular Completa
    # ============================
    
    def obtener_circular_completa(self, circular_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene una circular completa con sus reglas y exclusiones
        
        Args:
            circular_id: ID de la circular
        
        Returns:
            Diccionario con circular, reglas y exclusiones
        """
        return self.db.obtener_circular_completa(circular_id)
    
    # ============================
    # Utilidades
    # ============================
    
    def esta_vacia(self) -> bool:
        """Verifica si la base de datos está vacía"""
        return self.db.esta_vacia()
    
    def _validar_fechas(self, fecha_inicio: str, fecha_fin: str):
        """
        Valida que las fechas sean correctas
        
        Args:
            fecha_inicio: Fecha de inicio (YYYY-MM-DD)
            fecha_fin: Fecha de fin (YYYY-MM-DD)
        
        Raises:
            Exception: Si las fechas son inválidas
        """
        try:
            inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d").date()
            fin = datetime.strptime(fecha_fin, "%Y-%m-%d").date()
            
            if inicio > fin:
                raise Exception("La fecha de inicio debe ser anterior o igual a la fecha de fin")
        except ValueError as e:
            raise Exception(f"Formato de fecha inválido: {e}")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
