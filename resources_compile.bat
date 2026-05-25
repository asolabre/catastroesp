
@echo off
REM Activar entorno QGIS
call "c:\Program Files\QGIS 3.40.15\bin\o4w_env.bat"
call "c:\Program Files\QGIS 3.40.15\bin\qt5_env.bat"
call "c:\Program Files\QGIS 3.40.15\bin\py3_env.bat"

REM Compilar con python
@echo on
pyrcc5 -o resources.py resources.qrc
