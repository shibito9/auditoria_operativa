# -*- coding: utf-8 -*-
"""
Servicio de Gestión de Circulares - Sistema de Auditoría Operativa
"""
from pathlib import Path
from typing import List, Optional
from datetime import date
import json

from models import Circular, ReglaCircular
from services.circulares_db_service import CircularesDbService


class CircularService:
    """Servicio para gestión de circulares comerciales"""
    
    def __init__(self, data_path: Optional[Path] = None, use_sqlite: bool = True):
        """
        Inicializa el servicio de circulares
        
        Args:
            data_path: Ruta al archivo JSON de circulares (fallback). Por defecto: data/circulares.json
            use_sqlite: Si True, usa SQLite como backend principal. Por defecto: True
        """
        if data_path is None:
            # Usar ruta relativa al directorio raíz del proyecto
            root_dir = Path(__file__).resolve().parent.parent
            data_path = root_dir / "data" / "circulares.json"
        
        self.data_path = data_path
        self.use_sqlite = use_sqlite
        self._circulares: List[Circular] = []
        
        # Inicializar servicio SQLite
        if use_sqlite:
            try:
                self.db_service = CircularesDbService()
                # Cargar desde SQLite
                self._load_from_sqlite()
                
                # Si SQLite está vacío, cargar desde JSON como fallback
                if not self._circulares and self.data_path.exists():
                    print("SQLite vacío, cargando desde JSON como fallback...")
                    self._load_from_json()
            except Exception as e:
                print(f"Error al inicializar SQLite: {e}. Usando JSON como fallback.")
                self.use_sqlite = False
                self._load_from_json()
        else:
            self._load_from_json()
    
    def _load_from_sqlite(self):
        """Carga las circulares desde SQLite"""
        try:
            circulares_db = self.db_service.obtener_todas_circulares(solo_activas=False)
            self._circulares = [self._db_to_circular(c) for c in circulares_db]
        except Exception as e:
            print(f"Error al cargar circulares desde SQLite: {e}")
            self._circulares = []
    
    def _load_from_json(self):
        """Carga las circulares desde el archivo JSON (fallback)"""
        if not self.data_path.exists():
            self._circulares = []
            return
        
        try:
            with open(self.data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self._circulares = [
                    Circular.from_dict(c) for c in data.get("circulares", [])
                ]
        except Exception as e:
            print(f"Error al cargar circulares desde JSON: {e}")
            self._circulares = []
    
    def _save_circulares(self):
        """Guarda las circulares en el archivo JSON (solo modo legacy)"""
        if self.use_sqlite:
            return  # No guardar en JSON si estamos usando SQLite
        
        try:
            data = {
                "circulares": [c.to_dict() for c in self._circulares]
            }
            with open(self.data_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise Exception(f"Error al guardar circulares: {e}")
    
    def _db_to_circular(self, db_circular: dict) -> Circular:
        """Convierte un diccionario de DB a objeto Circular"""
        # Obtener reglas y exclusiones desde DB
        reglas_db = self.db_service.obtener_reglas(db_circular["id"])
        exclusiones_db = self.db_service.obtener_exclusiones(db_circular["id"])
        
        # Convertir reglas
        reglas = [self._db_to_regla(r) for r in reglas_db]
        
        # Convertir exclusiones
        exclusiones = [e["patron"] for e in exclusiones_db]
        
        # Crear objeto Circular
        return Circular(
            codigo=db_circular["codigo"],
            nombre=db_circular["nombre"],
            fecha_inicio=date.fromisoformat(db_circular["fecha_inicio"]),
            fecha_fin=date.fromisoformat(db_circular["fecha_fin"]),
            descuento_porcentaje=db_circular.get("descuento_porcentaje"),
            activa=db_circular.get("activa", True),
            exclusiones=exclusiones,
            condiciones_especiales=[],
            reglas=reglas
        )
    
    def _db_to_regla(self, db_regla: dict) -> ReglaCircular:
        """Convierte un diccionario de DB a objeto ReglaCircular"""
        return ReglaCircular(
            id=str(db_regla["id"]),  # Convertir a string para compatibilidad
            categoria=db_regla["categoria"],
            precio_full=db_regla.get("precio_full"),
            valor_antes_iva=db_regla.get("valor_antes_iva"),
            iva=db_regla.get("iva"),
            valor_final=db_regla.get("valor_final"),
            descuento_porcentaje=db_regla.get("descuento_porcentaje"),
            criterios_procedencia=db_regla.get("criterios_procedencia", []),
            criterios_categoria=db_regla.get("criterios_categoria", []),
            criterios_descripcion=db_regla.get("criterios_descripcion", []),
            criterios_linea=db_regla.get("criterios_linea", []),
            criterios_peso=db_regla.get("criterios_peso"),
            accion_especial=db_regla.get("accion_especial"),
            observaciones=db_regla.get("observaciones", "")
        )
    
    def _regla_to_db_dict(self, regla: ReglaCircular) -> dict:
        """Convierte un objeto ReglaCircular a diccionario para DB"""
        return {
            "categoria": regla.categoria,
            "criterios_procedencia": regla.criterios_procedencia,
            "criterios_categoria": regla.criterios_categoria,
            "criterios_linea": regla.criterios_linea,
            "criterios_descripcion": regla.criterios_descripcion,
            "criterios_peso": regla.criterios_peso,
            "precio_full": regla.precio_full,
            "valor_antes_iva": regla.valor_antes_iva,
            "iva": regla.iva,
            "valor_final": regla.valor_final,
            "descuento_porcentaje": regla.descuento_porcentaje,
            "accion_especial": regla.accion_especial,
            "observaciones": regla.observaciones,
            "orden": 0
        }
    
    def obtener_todas(self) -> List[Circular]:
        """Obtiene todas las circulares"""
        return self._circulares.copy()
    
    def obtener_por_codigo(self, codigo: str) -> Optional[Circular]:
        """Obtiene una circular por su código"""
        for circular in self._circulares:
            if circular.codigo == codigo:
                return circular
        return None
    
    def obtener_vigentes(self, fecha: date) -> List[Circular]:
        """
        Obtiene las circulares vigentes en una fecha
        
        Args:
            fecha: Fecha a verificar
        
        Returns:
            Lista de circulares vigentes en la fecha
        """
        return [c for c in self._circulares if c.esta_vigente(fecha)]
    
    def obtener_circular_vigente(self, fecha: date) -> Optional[Circular]:
        """
        Obtiene la circular vigente para una fecha específica
        Si hay múltiples vigentes, retorna la más reciente
        
        Args:
            fecha: Fecha a verificar
        
        Returns:
            Circular vigente o None si no hay ninguna
        """
        vigentes = self.obtener_vigentes(fecha)
        if not vigentes:
            return None
        
        # Retornar la más reciente (por fecha de inicio)
        return max(vigentes, key=lambda c: c.fecha_inicio)
    
    def crear_circular(self, circular: Circular) -> Circular:
        """
        Crea una nueva circular
        
        Args:
            circular: Circular a crear
        
        Returns:
            Circular creada
        
        Raises:
            Exception: Si ya existe una circular con el mismo código
        """
        if self.obtener_por_codigo(circular.codigo):
            raise Exception(f"Ya existe una circular con código {circular.codigo}")
        
        if self.use_sqlite:
            # Usar SQLite
            circular_data = {
                "codigo": circular.codigo,
                "nombre": circular.nombre,
                "fecha_inicio": circular.fecha_inicio.strftime("%Y-%m-%d"),
                "fecha_fin": circular.fecha_fin.strftime("%Y-%m-%d"),
                "descuento_porcentaje": circular.descuento_porcentaje,
                "activa": circular.activa,
                "observaciones": ""
            }
            db_circular = self.db_service.crear_circular(circular_data)
            
            # Agregar reglas
            for regla in circular.reglas:
                self.db_service.agregar_regla(db_circular["id"], self._regla_to_db_dict(regla))
            
            # Agregar exclusiones
            for exclusion in circular.exclusiones:
                self.db_service.agregar_exclusion(db_circular["id"], exclusion, "descripcion")
            
            # Recargar desde DB para obtener el objeto completo
            self._load_from_sqlite()
            return self.obtener_por_codigo(circular.codigo)
        else:
            # Usar JSON (legacy)
            self._circulares.append(circular)
            self._save_circulares()
            return circular
    
    def actualizar_circular(self, codigo: str, circular_actualizada: Circular) -> Circular:
        """
        Actualiza una circular existente
        
        Args:
            codigo: Código de la circular a actualizar
            circular_actualizada: Datos actualizados
        
        Returns:
            Circular actualizada
        
        Raises:
            Exception: Si no existe la circular
        """
        circular_existente = self.obtener_por_codigo(codigo)
        if not circular_existente:
            raise Exception(f"No existe circular con código {codigo}")
        
        if self.use_sqlite:
            # Usar SQLite
            db_circular = self.db_service.obtener_circular_por_codigo(codigo)
            if not db_circular:
                raise Exception(f"No existe circular con código {codigo}")
            
            circular_data = {
                "codigo": circular_actualizada.codigo,
                "nombre": circular_actualizada.nombre,
                "fecha_inicio": circular_actualizada.fecha_inicio.strftime("%Y-%m-%d"),
                "fecha_fin": circular_actualizada.fecha_fin.strftime("%Y-%m-%d"),
                "descuento_porcentaje": circular_actualizada.descuento_porcentaje,
                "activa": circular_actualizada.activa,
                "observaciones": ""
            }
            
            self.db_service.actualizar_circular(db_circular["id"], circular_data)
            
            # Recargar desde DB
            self._load_from_sqlite()
            return self.obtener_por_codigo(circular_actualizada.codigo)
        else:
            # Usar JSON (legacy)
            for i, circular in enumerate(self._circulares):
                if circular.codigo == codigo:
                    self._circulares[i] = circular_actualizada
                    self._save_circulares()
                    return circular_actualizada
        
        raise Exception(f"No existe circular con código {codigo}")
    
    def eliminar_circular(self, codigo: str) -> bool:
        """
        Elimina una circular por su código
        
        Args:
            codigo: Código de la circular a eliminar
        
        Returns:
            True si se eliminó, False si no existía
        """
        circular_existente = self.obtener_por_codigo(codigo)
        if not circular_existente:
            return False
        
        if self.use_sqlite:
            # Usar SQLite
            db_circular = self.db_service.obtener_circular_por_codigo(codigo)
            if db_circular:
                self.db_service.eliminar_circular(db_circular["id"])
                self._load_from_sqlite()
                return True
            return False
        else:
            # Usar JSON (legacy)
            for i, circular in enumerate(self._circulares):
                if circular.codigo == codigo:
                    del self._circulares[i]
                    self._save_circulares()
                    return True
            return False
    
    def agregar_regla(self, codigo_circular: str, regla: ReglaCircular) -> Circular:
        """
        Agrega una regla a una circular
        
        Args:
            codigo_circular: Código de la circular
            regla: Regla a agregar
        
        Returns:
            Circular actualizada
        
        Raises:
            Exception: Si no existe la circular
        """
        circular = self.obtener_por_codigo(codigo_circular)
        if not circular:
            raise Exception(f"No existe circular con código {codigo_circular}")
        
        if self.use_sqlite:
            # Usar SQLite
            db_circular = self.db_service.obtener_circular_por_codigo(codigo_circular)
            if not db_circular:
                raise Exception(f"No existe circular con código {codigo_circular}")
            
            self.db_service.agregar_regla(db_circular["id"], self._regla_to_db_dict(regla))
            self._load_from_sqlite()
            return self.obtener_por_codigo(codigo_circular)
        else:
            # Usar JSON (legacy)
            circular.reglas.append(regla)
            self._save_circulares()
            return circular
    
    def eliminar_regla(self, codigo_circular: str, id_regla: str) -> Circular:
        """
        Elimina una regla de una circular
        
        Args:
            codigo_circular: Código de la circular
            id_regla: ID de la regla a eliminar
        
        Returns:
            Circular actualizada
        
        Raises:
            Exception: Si no existe la circular o la regla
        """
        circular = self.obtener_por_codigo(codigo_circular)
        if not circular:
            raise Exception(f"No existe circular con código {codigo_circular}")
        
        if self.use_sqlite:
            # Usar SQLite
            try:
                regla_id_int = int(id_regla)
                self.db_service.eliminar_regla(regla_id_int)
                self._load_from_sqlite()
                return self.obtener_por_codigo(codigo_circular)
            except ValueError:
                # Si el ID no es numérico, buscar en memoria
                pass
        
        # Usar JSON (legacy) o fallback
        for i, regla in enumerate(circular.reglas):
            if regla.id == id_regla:
                del circular.reglas[i]
                if not self.use_sqlite:
                    self._save_circulares()
                return circular
        
        raise Exception(f"No existe regla con ID {id_regla} en circular {codigo_circular}")
    
    def buscar_regla_para_linea(self, linea_factura: dict, circular: Circular) -> Optional[ReglaCircular]:
        """
        Busca la mejor regla aplicable para una línea de factura usando scoring
        
        Sistema de scoring:
        - origen_comercial coincide: 100 puntos (filtro principal)
        - Categoría exacta coincide: 50 puntos
        - Línea exacta coincide: 30 puntos
        - Descripción contiene patrón: 20 puntos
        - Peso en rango: 10 puntos
        
        Desempate:
        1. Mayor puntaje total
        2. Mayor número de criterios coincidentes
        3. Orden en JSON (último recurso)
        
        Args:
            linea_factura: Diccionario con datos de la línea de factura
            circular: Circular donde buscar la regla
        
        Returns:
            ReglaCircular encontrada o None
        """
        origen_comercial = linea_factura.get("origen_comercial", "").upper()
        categoria = linea_factura.get("Producto Categoria", "")
        descripcion = linea_factura.get("Producto Descripcion", "")
        linea = linea_factura.get("Linea Nombre", "")
        peso = linea_factura.get("Producto Gramos")
        
        reglas_candidatas = []
        
        for idx, regla in enumerate(circular.reglas):
            puntaje = 0
            criterios_coincidentes = 0
            
            # 1. origen_comercial (filtro principal - 100 puntos)
            # Usa coincidencia_procedencia pero con origen_comercial normalizado
            if origen_comercial and regla.coincide_procedencia(origen_comercial):
                puntaje += 100
                criterios_coincidentes += 1
            
            # 2. Categoría exacta (50 puntos)
            if regla.coincide_categoria(categoria):
                puntaje += 50
                criterios_coincidentes += 1
            
            # 3. Línea exacta (30 puntos)
            if regla.coincide_linea(linea):
                puntaje += 30
                criterios_coincidentes += 1
            
            # 4. Descripción contiene patrón (20 puntos)
            if regla.coincide_descripcion(descripcion):
                puntaje += 20
                criterios_coincidentes += 1
            
            # 5. Peso en rango (10 puntos)
            if peso is not None and regla.coincide_peso(peso):
                puntaje += 10
                criterios_coincidentes += 1
            
            # Solo considerar reglas con al menos un criterio coincidente
            if puntaje > 0:
                reglas_candidatas.append({
                    'regla': regla,
                    'puntaje': puntaje,
                    'criterios': criterios_coincidentes,
                    'indice': idx
                })
        
        if not reglas_candidatas:
            return None
        
        # Ordenar por puntaje (descendente), luego por número de criterios (descendente)
        reglas_candidatas.sort(key=lambda x: (x['puntaje'], x['criterios']), reverse=True)
        
        # Retornar la regla con mayor puntaje
        return reglas_candidatas[0]['regla']
    
    def verificar_exclusion(self, linea_factura: dict, circular: Circular) -> bool:
        """
        Verifica si una línea de factura está excluida en la circular
        
        Args:
            linea_factura: Diccionario con datos de la línea de factura
            circular: Circular a verificar
        
        Returns:
            True si está excluida, False en caso contrario
        """
        descripcion = linea_factura.get("Producto Descripcion", "").lower()
        categoria = linea_factura.get("Producto Categoria", "").lower()
        
        for exclusion in circular.exclusiones:
            exclusion_lower = exclusion.lower()
            if exclusion_lower in descripcion or exclusion_lower in categoria:
                return True
        
        return False
