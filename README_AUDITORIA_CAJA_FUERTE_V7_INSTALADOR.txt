GAMAN - Auditoria de Caja Fuerte V7
Desarrollado por SANTIAGO AGUDELO - GAMAN -

1. SOBRE OFFICE / EXCEL
----------------------
La aplicacion NO necesita Microsoft Office activado para funcionar.
Lee y escribe archivos .xlsx usando la libreria openpyxl de Python.

Importante:
- Para ejecutar la auditoria: no hace falta Office.
- Para abrir visualmente el Excel generado: el auditor puede usar Excel, LibreOffice Calc, WPS Office o Google Sheets.
- Si Office no esta activado, normalmente podra abrir archivos, pero podria tener limitaciones para editar/guardar desde Excel. Eso no afecta la generacion del archivo por la aplicacion.

2. EJECUTAR EN MODO SCRIPT
--------------------------
Coloca estos archivos en una carpeta:
- gui.py
- caja_fuerte_backend.py
- ejecutar_auditoria_caja_fuerte.bat

Ejecuta:
ejecutar_auditoria_caja_fuerte.bat

3. CREAR EXE PORTABLE
---------------------
En tu computador de desarrollo, dentro de la carpeta del proyecto, ejecuta:
crear_exe_portable.bat

Esto generara:
dist\GAMAN_Auditoria_Caja_Fuerte\GAMAN_Auditoria_Caja_Fuerte.exe

Para compartirlo sin instalador, copia toda esta carpeta al PC del auditor:
dist\GAMAN_Auditoria_Caja_Fuerte

4. CREAR INSTALADOR .EXE
------------------------
Primero genera el EXE portable con:
crear_exe_portable.bat

Luego instala Inno Setup 6 en tu computador.
Despues ejecuta:
crear_instalador_inno_setup.bat

El instalador final quedara en:
Output\Instalador_GAMAN_Auditoria_Caja_Fuerte_V7.exe

5. FIRMA DEL DESARROLLADOR
--------------------------
La interfaz muestra:
Desarrollado por SANTIAGO AGUDELO - GAMAN -

Tambien se agrega en la hoja RESUMEN_CF del Excel generado.

6. RECOMENDACION PRACTICA
-------------------------
Para una primera entrega al auditor, usa el EXE portable.
Es mas simple, no requiere permisos de administrador y evita problemas de instalacion.
Cuando confirmes que funciona bien en su PC, crea el instalador con Inno Setup.
