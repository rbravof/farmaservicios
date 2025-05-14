@echo off

echo Activando entorno virtual...
call env\Scripts\activate.bat

echo Iniciando servidor FastAPI...
uvicorn app.main:app --reload

pause
