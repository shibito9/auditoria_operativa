# -*- coding: utf-8 -*-
"""
Modelo de Base de Datos SQLite para Gestión de Circulares - Sistema de Auditoría Operativa
"""
import sqlite3
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
import json


class CircularesDB:
    """Modelo de base de datos para gestión de circulares comerciales"""
    
    def __init__(self, db_path: Optional[Path] = None):
        """
        Inicializa la conexión a la base de datos SQLite
        
        Args:
            db_path: Ruta al archivo SQLite. Por defecto: database/circulares.db
        """
        if db_path is None:
            # Usar ruta relativa al directorio raíz del proyecto
            root_dir = Path(__file__).resolve().parent.parent
            db_path = root_dir / "database" / "circulares.db"
        
        self.db_path = db_path
        self.conn = None
        self._initialize_db()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Obtiene una conexión a la base de datos"""
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
        return self.conn
    
    def _initialize_db(self):
        """Inicializa las tablas de la base de datos si no existen"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Tabla circulares
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS circulares (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo TEXT UNIQUE NOT NULL,
                nombre TEXT NOT NULL,
                fecha_inicio DATE NOT NULL,
                fecha_fin DATE NOT NULL,
                descuento_porcentaje REAL,
                activa BOOLEAN DEFAULT 1,
                archivo_fuente TEXT,
                observaciones TEXT,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabla reglas_circulares
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reglas_circulares (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                circular_id INTEGER NOT NULL,
                categoria TEXT NOT NULL,
                criterios_procedencia TEXT,
                criterios_categoria TEXT,
                criterios_linea TEXT,
                criterios_descripcion TEXT,
                criterios_peso TEXT,
                precio_full REAL,
                valor_antes_iva REAL,
                iva REAL,
                valor_final REAL,
                descuento_porcentaje REAL,
                accion_especial TEXT,
                observaciones TEXT,
                orden INTEGER DEFAULT 0,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (circular_id) REFERENCES circulares(id) ON DELETE CASCADE
            )
        """)
        
        # Tabla exclusiones_circulares
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS exclusiones_circulares (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                circular_id INTEGER NOT NULL,
                patron TEXT NOT NULL,
                tipo TEXT DEFAULT 'descripcion',
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (circular_id) REFERENCES circulares(id) ON DELETE CASCADE
            )
        """)
        
        # Índices para optimizar consultas
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_circulares_codigo ON circulares(codigo)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_circulares_activas ON circulares(activa, fecha_inicio, fecha_fin)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_reglas_circular_id ON reglas_circulares(circular_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_exclusiones_circular_id ON exclusiones_circulares(circular_id)
        """)
        
        conn.commit()
    
    def close(self):
        """Cierra la conexión a la base de datos"""
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    # ============================
    # Operaciones CRUD - Circulares
    # ============================
    
    def crear_circular(self, circular_data: Dict[str, Any]) -> int:
        """
        Crea una nueva circular
        
        Args:
            circular_data: Diccionario con datos de la circular
        
        Returns:
            ID de la circular creada
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO circulares (
                codigo, nombre, fecha_inicio, fecha_fin, descuento_porcentaje,
                activa, archivo_fuente, observaciones
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            circular_data["codigo"],
            circular_data["nombre"],
            circular_data["fecha_inicio"],
            circular_data["fecha_fin"],
            circular_data.get("descuento_porcentaje"),
            circular_data.get("activa", True),
            circular_data.get("archivo_fuente"),
            circular_data.get("observaciones", "")
        ))
        
        conn.commit()
        return cursor.lastrowid
    
    def obtener_circular_por_id(self, circular_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene una circular por su ID"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM circulares WHERE id = ?", (circular_id,))
        row = cursor.fetchone()
        
        if row:
            return dict(row)
        return None
    
    def obtener_circular_por_codigo(self, codigo: str) -> Optional[Dict[str, Any]]:
        """Obtiene una circular por su código"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM circulares WHERE codigo = ?", (codigo,))
        row = cursor.fetchone()
        
        if row:
            return dict(row)
        return None
    
    def obtener_todas_circulares(self, solo_activas: bool = False) -> List[Dict[str, Any]]:
        """
        Obtiene todas las circulares
        
        Args:
            solo_activas: Si True, solo retorna circulares activas
        
        Returns:
            Lista de circulares
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        if solo_activas:
            cursor.execute("""
                SELECT * FROM circulares 
                WHERE activa = 1 
                ORDER BY fecha_inicio DESC
            """)
        else:
            cursor.execute("""
                SELECT * FROM circulares 
                ORDER BY fecha_inicio DESC
            """)
        
        return [dict(row) for row in cursor.fetchall()]
    
    def obtener_circulares_vigentes(self, fecha: str) -> List[Dict[str, Any]]:
        """
        Obtiene circulares vigentes en una fecha específica
        
        Args:
            fecha: Fecha en formato YYYY-MM-DD
        
        Returns:
            Lista de circulares vigentes
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM circulares 
            WHERE activa = 1 
            AND fecha_inicio <= ? 
            AND fecha_fin >= ?
            ORDER BY fecha_inicio DESC
        """, (fecha, fecha))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def actualizar_circular(self, circular_id: int, circular_data: Dict[str, Any]) -> bool:
        """
        Actualiza una circular existente
        
        Args:
            circular_id: ID de la circular a actualizar
            circular_data: Datos actualizados
        
        Returns:
            True si se actualizó, False en caso contrario
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE circulares SET
                codigo = ?,
                nombre = ?,
                fecha_inicio = ?,
                fecha_fin = ?,
                descuento_porcentaje = ?,
                activa = ?,
                archivo_fuente = ?,
                observaciones = ?,
                fecha_actualizacion = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (
            circular_data["codigo"],
            circular_data["nombre"],
            circular_data["fecha_inicio"],
            circular_data["fecha_fin"],
            circular_data.get("descuento_porcentaje"),
            circular_data.get("activa", True),
            circular_data.get("archivo_fuente"),
            circular_data.get("observaciones", ""),
            circular_id
        ))
        
        conn.commit()
        return cursor.rowcount > 0
    
    def eliminar_circular(self, circular_id: int) -> bool:
        """
        Elimina una circular (con sus reglas y exclusiones en cascada)
        
        Args:
            circular_id: ID de la circular a eliminar
        
        Returns:
            True si se eliminó, False en caso contrario
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM circulares WHERE id = ?", (circular_id,))
        conn.commit()
        return cursor.rowcount > 0
    
    def activar_circular(self, circular_id: int, activa: bool) -> bool:
        """
        Activa o desactiva una circular
        
        Args:
            circular_id: ID de la circular
            activa: True para activar, False para desactivar
        
        Returns:
            True si se actualizó, False en caso contrario
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE circulares SET 
                activa = ?,
                fecha_actualizacion = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (activa, circular_id))
        
        conn.commit()
        return cursor.rowcount > 0
    
    # ============================
    # Operaciones CRUD - Reglas
    # ============================
    
    def crear_regla(self, circular_id: int, regla_data: Dict[str, Any]) -> int:
        """
        Crea una nueva regla para una circular
        
        Args:
            circular_id: ID de la circular
            regla_data: Datos de la regla
        
        Returns:
            ID de la regla creada
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Convertir listas/dict a JSON para almacenamiento
        criterios_procedencia_json = json.dumps(regla_data.get("criterios_procedencia", []))
        criterios_categoria_json = json.dumps(regla_data.get("criterios_categoria", []))
        criterios_linea_json = json.dumps(regla_data.get("criterios_linea", []))
        criterios_descripcion_json = json.dumps(regla_data.get("criterios_descripcion", []))
        criterios_peso_json = json.dumps(regla_data.get("criterios_peso"))
        
        cursor.execute("""
            INSERT INTO reglas_circulares (
                circular_id, categoria, criterios_procedencia, criterios_categoria,
                criterios_linea, criterios_descripcion, criterios_peso,
                precio_full, valor_antes_iva, iva, valor_final, descuento_porcentaje,
                accion_especial, observaciones, orden
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            circular_id,
            regla_data["categoria"],
            criterios_procedencia_json,
            criterios_categoria_json,
            criterios_linea_json,
            criterios_descripcion_json,
            criterios_peso_json,
            regla_data.get("precio_full"),
            regla_data.get("valor_antes_iva"),
            regla_data.get("iva"),
            regla_data.get("valor_final"),
            regla_data.get("descuento_porcentaje"),
            regla_data.get("accion_especial"),
            regla_data.get("observaciones", ""),
            regla_data.get("orden", 0)
        ))
        
        conn.commit()
        return cursor.lastrowid
    
    def obtener_reglas_por_circular(self, circular_id: int) -> List[Dict[str, Any]]:
        """Obtiene todas las reglas de una circular"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM reglas_circulares 
            WHERE circular_id = ? 
            ORDER BY orden ASC, id ASC
        """, (circular_id,))
        
        reglas = []
        for row in cursor.fetchall():
            regla_dict = dict(row)
            # Convertir JSON de vuelta a listas/dict
            regla_dict["criterios_procedencia"] = json.loads(regla_dict["criterios_procedencia"] or "[]")
            regla_dict["criterios_categoria"] = json.loads(regla_dict["criterios_categoria"] or "[]")
            regla_dict["criterios_linea"] = json.loads(regla_dict["criterios_linea"] or "[]")
            regla_dict["criterios_descripcion"] = json.loads(regla_dict["criterios_descripcion"] or "[]")
            regla_dict["criterios_peso"] = json.loads(regla_dict["criterios_peso"] or "null")
            reglas.append(regla_dict)
        
        return reglas
    
    def actualizar_regla(self, regla_id: int, regla_data: Dict[str, Any]) -> bool:
        """Actualiza una regla existente"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        criterios_procedencia_json = json.dumps(regla_data.get("criterios_procedencia", []))
        criterios_categoria_json = json.dumps(regla_data.get("criterios_categoria", []))
        criterios_linea_json = json.dumps(regla_data.get("criterios_linea", []))
        criterios_descripcion_json = json.dumps(regla_data.get("criterios_descripcion", []))
        criterios_peso_json = json.dumps(regla_data.get("criterios_peso"))
        
        cursor.execute("""
            UPDATE reglas_circulares SET
                categoria = ?,
                criterios_procedencia = ?,
                criterios_categoria = ?,
                criterios_linea = ?,
                criterios_descripcion = ?,
                criterios_peso = ?,
                precio_full = ?,
                valor_antes_iva = ?,
                iva = ?,
                valor_final = ?,
                descuento_porcentaje = ?,
                accion_especial = ?,
                observaciones = ?,
                orden = ?
            WHERE id = ?
        """, (
            regla_data["categoria"],
            criterios_procedencia_json,
            criterios_categoria_json,
            criterios_linea_json,
            criterios_descripcion_json,
            criterios_peso_json,
            regla_data.get("precio_full"),
            regla_data.get("valor_antes_iva"),
            regla_data.get("iva"),
            regla_data.get("valor_final"),
            regla_data.get("descuento_porcentaje"),
            regla_data.get("accion_especial"),
            regla_data.get("observaciones", ""),
            regla_data.get("orden", 0),
            regla_id
        ))
        
        conn.commit()
        return cursor.rowcount > 0
    
    def eliminar_regla(self, regla_id: int) -> bool:
        """Elimina una regla"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM reglas_circulares WHERE id = ?", (regla_id,))
        conn.commit()
        return cursor.rowcount > 0
    
    # ============================
    # Operaciones CRUD - Exclusiones
    # ============================
    
    def crear_exclusion(self, circular_id: int, patron: str, tipo: str = "descripcion") -> int:
        """
        Crea una nueva exclusión para una circular
        
        Args:
            circular_id: ID de la circular
            patron: Patrón de exclusión
            tipo: Tipo de exclusión ('descripcion' o 'categoria')
        
        Returns:
            ID de la exclusión creada
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO exclusiones_circulares (circular_id, patron, tipo)
            VALUES (?, ?, ?)
        """, (circular_id, patron, tipo))
        
        conn.commit()
        return cursor.lastrowid
    
    def obtener_exclusiones_por_circular(self, circular_id: int) -> List[Dict[str, Any]]:
        """Obtiene todas las exclusiones de una circular"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM exclusiones_circulares 
            WHERE circular_id = ? 
            ORDER BY id ASC
        """, (circular_id,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def eliminar_exclusion(self, exclusion_id: int) -> bool:
        """Elimina una exclusión"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM exclusiones_circulares WHERE id = ?", (exclusion_id,))
        conn.commit()
        return cursor.rowcount > 0
    
    def eliminar_exclusiones_por_circular(self, circular_id: int) -> int:
        """Elimina todas las exclusiones de una circular"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM exclusiones_circulares WHERE circular_id = ?", (circular_id,))
        conn.commit()
        return cursor.rowcount
    
    # ============================
    # Utilidades
    # ============================
    
    def esta_vacia(self) -> bool:
        """Verifica si la base de datos está vacía"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) as count FROM circulares")
        row = cursor.fetchone()
        
        return row["count"] == 0
    
    def obtener_circular_completa(self, circular_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene una circular completa con sus reglas y exclusiones
        
        Args:
            circular_id: ID de la circular
        
        Returns:
            Diccionario con circular, reglas y exclusiones
        """
        circular = self.obtener_circular_por_id(circular_id)
        if not circular:
            return None
        
        reglas = self.obtener_reglas_por_circular(circular_id)
        exclusiones = self.obtener_exclusiones_por_circular(circular_id)
        
        return {
            "circular": circular,
            "reglas": reglas,
            "exclusiones": exclusiones
        }
