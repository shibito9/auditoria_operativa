# -*- coding: utf-8 -*-
"""
Script de Migración de circulares.json a SQLite - Sistema de Auditoría Operativa

Este script migra los datos del archivo JSON a la base de datos SQLite.
"""
import sys
from pathlib import Path
import json

# Agregar directorio raíz al path para imports absolutos
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from services.circulares_db_service import CircularesDbService


def migrate_json_to_sqlite(json_path: Path = None, db_path: Path = None):
    """
    Migra los datos de circulares.json a SQLite
    
    Args:
        json_path: Ruta al archivo JSON. Por defecto: data/circulares.json
        db_path: Ruta al archivo SQLite. Por defecto: database/circulares.db
    """
    if json_path is None:
        json_path = ROOT_DIR / "data" / "circulares.json"
    
    if not json_path.exists():
        print(f"❌ No existe el archivo JSON: {json_path}")
        return False
    
    # Cargar datos del JSON
    print(f"📂 Cargando datos desde: {json_path}")
    with open(json_path, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
    
    circulares_json = json_data.get("circulares", [])
    print(f"📊 Se encontraron {len(circulares_json)} circulares en el JSON")
    
    # Inicializar servicio de base de datos
    print(f"🗄️  Inicializando base de datos SQLite...")
    service = CircularesDbService(db_path)
    
    # Verificar si la base de datos ya tiene datos
    if not service.esta_vacia():
        print("⚠️  La base de datos ya contiene datos.")
        respuesta = input("¿Desea continuar y agregar datos adicionales? (s/n): ")
        if respuesta.lower() != 's':
            print("❌ Migración cancelada")
            service.close()
            return False
    
    # Migrar cada circular
    migradas = 0
    errores = []
    
    for circular_json in circulares_json:
        try:
            print(f"\n🔄 Migrando circular: {circular_json['codigo']}")
            
            # Preparar datos de la circular
            circular_data = {
                "codigo": circular_json["codigo"],
                "nombre": circular_json["nombre"],
                "fecha_inicio": circular_json["fecha_inicio"],
                "fecha_fin": circular_json["fecha_fin"],
                "descuento_porcentaje": circular_json.get("descuento_porcentaje"),
                "activa": circular_json.get("activa", True),
                "archivo_fuente": circular_json.get("archivo_fuente"),
                "observaciones": circular_json.get("observaciones", "")
            }
            
            # Crear circular
            circular_creada = service.crear_circular(circular_data)
            circular_id = circular_creada["id"]
            print(f"   ✅ Circular creada con ID: {circular_id}")
            
            # Migrar reglas
            reglas_json = circular_json.get("reglas", [])
            print(f"   📋 Migrando {len(reglas_json)} reglas...")
            
            for idx, regla_json in enumerate(reglas_json):
                regla_data = {
                    "categoria": regla_json["categoria"],
                    "criterios_procedencia": regla_json.get("criterios_procedencia", []),
                    "criterios_categoria": regla_json.get("criterios_categoria", []),
                    "criterios_linea": regla_json.get("criterios_linea", []),
                    "criterios_descripcion": regla_json.get("criterios_descripcion", []),
                    "criterios_peso": regla_json.get("criterios_peso"),
                    "precio_full": regla_json.get("precio_full"),
                    "valor_antes_iva": regla_json.get("valor_antes_iva"),
                    "iva": regla_json.get("iva"),
                    "valor_final": regla_json.get("valor_final"),
                    "descuento_porcentaje": regla_json.get("descuento_porcentaje"),
                    "accion_especial": regla_json.get("accion_especial"),
                    "observaciones": regla_json.get("observaciones", ""),
                    "orden": idx
                }
                
                service.agregar_regla(circular_id, regla_data)
            
            print(f"   ✅ Reglas migradas correctamente")
            
            # Migrar exclusiones
            exclusiones_json = circular_json.get("exclusiones", [])
            print(f"   🚫 Migrando {len(exclusiones_json)} exclusiones...")
            
            for exclusion in exclusiones_json:
                service.agregar_exclusion(circular_id, exclusion, "descripcion")
            
            print(f"   ✅ Exclusiones migradas correctamente")
            
            migradas += 1
            print(f"   ✅ Circular {circular_json['codigo']} migrada exitosamente")
            
        except Exception as e:
            error_msg = f"Error migrando circular {circular_json.get('codigo', 'desconocida')}: {str(e)}"
            print(f"   ❌ {error_msg}")
            errores.append(error_msg)
    
    # Cerrar conexión
    service.close()
    
    # Resumen
    print("\n" + "="*60)
    print("📊 RESUMEN DE MIGRACIÓN")
    print("="*60)
    print(f"✅ Circulares migradas: {migradas}/{len(circulares_json)}")
    print(f"❌ Errores: {len(errores)}")
    
    if errores:
        print("\n❌ Lista de errores:")
        for error in errores:
            print(f"   - {error}")
    
    if migradas == len(circulares_json):
        print("\n🎉 ¡Migración completada exitosamente!")
        return True
    else:
        print("\n⚠️  Migración completada con errores")
        return False


def main():
    """Función principal para ejecutar la migración"""
    print("="*60)
    print("🔄 MIGRACIÓN DE CIRCULARES JSON A SQLITE")
    print("="*60)
    
    # Ejecutar migración
    exito = migrate_json_to_sqlite()
    
    if exito:
        print("\n✅ Puede eliminar o respaldar el archivo JSON original")
        print("   El sistema ahora usará SQLite como fuente de datos")
    else:
        print("\n⚠️  Revise los errores antes de continuar")
    
    return exito


if __name__ == "__main__":
    import sys
    sys.exit(0 if main() else 1)
